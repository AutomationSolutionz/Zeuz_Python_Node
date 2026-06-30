import asyncio
import importlib
import inspect
import json
import os
import threading
import time
import uuid
from collections import defaultdict, deque
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from Framework.install_handler import install_log_config
from Framework.install_handler import utils as install_utils
from Framework.install_handler.route import services as INSTALLER_SERVICES
from Framework.install_handler.android.android_emulator import (
    android_emulator_install,
    check_emulator_list,
    create_avd_from_system_image,
    launch_avd,
)
from Framework.install_handler.system_info.system_info import get_formatted_system_info


router = APIRouter(prefix="/installer", tags=["installer"])

# --- Configuration --- #

MAX_CONCURRENCY = int(os.getenv("INSTALLER_MAX_CONCURRENCY", "2"))
EVENT_HISTORY = int(os.getenv("INSTALLER_EVENT_HISTORY", "200"))
FORWARD_TO_REMOTE = os.getenv("INSTALLER_FORWARD_REMOTE", "").lower() in (
    "1",
    "true",
    "yes",
)
ANDROID_CATEGORIES = {"Android", "AndroidEmulator"}
WEB_CATEGORIES = {"Web"}
NATIVE_CATEGORIES = {"Linux", "Windows", "MacOS"}

# Combined categories for patching
PATCH_CATEGORIES = ANDROID_CATEGORIES | WEB_CATEGORIES | NATIVE_CATEGORIES

# --- Models --- #

JobStatus = Literal["queued", "running", "succeeded", "failed"]


class ServiceRequest(BaseModel):
    category: str
    name: str
    user_password: str | None = None
    request_id: str | None = None

class AndroidEmulatorCreateRequest(BaseModel):
    device_id: str
    device_name: str
    request_id: str | None = None


class AndroidEmulatorLaunchRequest(BaseModel):
    name: str
    request_id: str | None = None


class IOSSimulatorCreateRequest(BaseModel):
    device_type: str
    runtime: str | None = None
    name: str | None = None
    request_id: str | None = None


class IOSSimulatorLaunchRequest(BaseModel):
    udid: str
    request_id: str | None = None


class IOSSimulatorDeleteRequest(BaseModel):
    udid: str
    request_id: str | None = None


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus
    action: str
    category: str | None
    name: str | None
    request_id: str | None
    submitted_at: float


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    action: str
    category: str | None
    name: str | None
    request_id: str | None
    created_at: float
    updated_at: float
    error: str | None
    result: Any | None
    last_event: dict | None


class ServicesResponse(BaseModel):
    node_id: str
    generated_at: float
    services: list[dict]


class SystemInfoResponse(BaseModel):
    node_id: str
    generated_at: float
    data: dict


# --- Event Bus --- #


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)
        self._lock = threading.Lock()

    def subscribe(self, job_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=EVENT_HISTORY)
        with self._lock:
            self._subscribers[job_id].add(queue)
        return queue

    def unsubscribe(self, job_id: str, queue: asyncio.Queue) -> None:
        with self._lock:
            queues = self._subscribers.get(job_id)
            if not queues:
                return
            queues.discard(queue)
            if not queues:
                self._subscribers.pop(job_id, None)

    def publish(self, event: dict) -> None:
        job_id = event.get("job_id")
        with self._lock:
            targets = list(self._subscribers.get(job_id, set())) if job_id else []
            targets += list(self._subscribers.get("*", set()))
        for queue in targets:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                try:
                    _ = queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    pass


# --- Job Store --- #


@dataclass
class Job:
    id: str
    action: str
    category: str | None
    name: str | None
    request_id: str | None
    payload: dict | None
    status: JobStatus = "queued"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    error: str | None = None
    result: Any | None = None
    last_event: dict | None = None
    events: deque = field(default_factory=lambda: deque(maxlen=EVENT_HISTORY))


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def add(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.id] = job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for key, value in kwargs.items():
                setattr(job, key, value)
            job.updated_at = time.time()

    def add_event(self, job_id: str, event: dict) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.last_event = event
            job.events.append(event)

    def find_active(
        self, action: str, category: str | None, name: str | None
    ) -> Job | None:
        """Return an existing queued/running job for the same action+category+name."""
        with self._lock:
            for job in self._jobs.values():
                if (
                    job.status in ("queued", "running")
                    and job.action == action
                    and job.category == category
                    and job.name == name
                ):
                    return job
            return None


EVENT_BUS = EventBus()
JOB_STORE = JobStore()
SEM = asyncio.Semaphore(MAX_CONCURRENCY)

_event_context: ContextVar[str | None] = ContextVar("installer_job_id", default=None)
ORIGINAL_SEND_RESPONSE = install_utils.send_response


def _make_event(job_id: str, event_type: str, payload: dict | None) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "job_id": job_id,
        "timestamp": time.time(),
        "type": event_type,
        "payload": payload,
        "node_id": install_utils.read_node_id(),
        "version": install_utils.version,
    }


async def send_response_proxy(data: dict | None = None) -> None:
    job_id = _event_context.get()
    if job_id:
        event = _make_event(job_id, "installer.update", data or {})
        JOB_STORE.add_event(job_id, event)
        EVENT_BUS.publish(event)

    if job_id is None or FORWARD_TO_REMOTE:
        await ORIGINAL_SEND_RESPONSE(data)


def _patch_send_response_targets() -> None:
    modules: set[str] = set()

    # Collect modules from Android and Web service registry
    for category in INSTALLER_SERVICES:
        if category.get("category") not in PATCH_CATEGORIES:
            continue
        for key in ("install_function", "status_function"):
            func = category.get(key)
            if func:
                modules.add(func.__module__)
        for service in category.get("services", []):
            for key in ("install_function", "status_function"):
                func = service.get(key)
                if func:
                    modules.add(func.__module__)

    # Explicitly add emulator module
    modules.add("Framework.install_handler.android.emulator")
    modules.add("Framework.install_handler.android.emulator_windows_linux")

    # Patch modules that use send_response
    for mod_name in modules:
        mod = importlib.import_module(mod_name)
        if hasattr(mod, "send_response"):
            setattr(mod, "send_response", send_response_proxy)

    # Patch utils as well (for any late imports)
    install_utils.send_response = send_response_proxy


_patch_send_response_targets()


# --- Helpers --- #


def _find_category(category_name: str) -> dict:
    if category_name not in PATCH_CATEGORIES:
        raise KeyError(f"Unsupported category: {category_name}")
    for category in INSTALLER_SERVICES:
        if category.get("category") == category_name:
            return category
    raise KeyError(f"Unknown category: {category_name}")


def _find_service(category: dict, service_name: str) -> dict:
    for service in category.get("services", []):
        if service.get("name") == service_name:
            return service
    raise KeyError(f"Unknown service: {service_name}")


async def _call_install_function(func, user_password: str | None = None):
    if func is None:
        raise RuntimeError("Install function not defined")

    sig = inspect.signature(func)
    if len(sig.parameters) > 0:
        return await _maybe_await(func, user_password or "")
    return await _maybe_await(func)


async def _call_status_function(func):
    if func is None:
        raise RuntimeError("Status function not defined")
    return await _maybe_await(func)


async def _maybe_await(func, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    result = await asyncio.to_thread(func, *args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


async def _run_job(job: Job) -> None:
    # Status checks are read-only and fast — skip the concurrency semaphore
    # so they don't queue behind running installs.
    if job.action == "status":
        await _execute_job(job)
    else:
        async with SEM:
            await _execute_job(job)


async def _execute_job(job: Job) -> None:
    JOB_STORE.update(job.id, status="running")
    EVENT_BUS.publish(_make_event(job.id, "job.started", None))
    token = _event_context.set(job.id)
    try:
        result = await _dispatch_job(job)
        JOB_STORE.update(job.id, status="succeeded", result=result)
        EVENT_BUS.publish(_make_event(job.id, "job.completed", {"result": result}))
    except Exception as exc:
        JOB_STORE.update(job.id, status="failed", error=str(exc))
        EVENT_BUS.publish(
            _make_event(job.id, "job.failed", {"error": str(exc)})
        )
    finally:
        _event_context.reset(token)


async def _dispatch_job(job: Job) -> Any:
    action = job.action

    if action == "install":
        category = _find_category(job.category or "")
        if category.get("category") == "AndroidEmulator":
            raise RuntimeError("Use the emulator endpoints for AndroidEmulator")
        service = _find_service(category, job.name or "")
        if install_utils.current_os not in service.get("os", []):
            raise RuntimeError("Service not supported on current OS")
        return await _call_install_function(
            service.get("install_function"),
            job.payload.get("user_password") if job.payload else None,
        )

    if action == "status":
        category = _find_category(job.category or "")
        if category.get("category") == "AndroidEmulator":
            raise RuntimeError("Use the emulator endpoints for AndroidEmulator")
        service = _find_service(category, job.name or "")
        if install_utils.current_os not in service.get("os", []):
            raise RuntimeError("Service not supported on current OS")
        return await _call_status_function(service.get("status_function"))

    if action == "android_emulator_refresh":
        return await _maybe_await(check_emulator_list)

    if action == "android_emulator_list_installables":
        return await _maybe_await(android_emulator_install)

    if action == "android_emulator_create":
        device_id = job.payload.get("device_id") if job.payload else None
        device_name = job.payload.get("device_name") if job.payload else None
        if not device_id or not device_name:
            raise RuntimeError("device_id and device_name are required")
        device_param = f"install device;{device_id};{device_name}"
        return await _maybe_await(create_avd_from_system_image, device_param)

    if action == "android_emulator_launch":
        name = job.payload.get("name") if job.payload else None
        if not name:
            raise RuntimeError("name is required")
        return await _maybe_await(launch_avd, name)

    if action == "system_info":
        return await get_formatted_system_info()

    raise RuntimeError(f"Unsupported action: {action}")


def _submit_job(
    action: str,
    category: str | None = None,
    name: str | None = None,
    payload: dict | None = None,
    request_id: str | None = None,
) -> Job:
    # Deduplicate: if an identical job is already queued/running, return it.
    existing = JOB_STORE.find_active(action, category, name)
    if existing:
        return existing

    job = Job(
        id=str(uuid.uuid4()),
        action=action,
        category=category,
        name=name,
        request_id=request_id,
        payload=payload or {},
    )
    JOB_STORE.add(job)
    EVENT_BUS.publish(_make_event(job.id, "job.queued", None))
    asyncio.create_task(_run_job(job))
    return job


# --- Routes --- #


@router.get("/services", response_model=ServicesResponse)
async def services_list():
    services = [
        svc
        for svc in install_utils.generate_services_list(INSTALLER_SERVICES)
        if svc.get("category") in PATCH_CATEGORIES
    ]
    return ServicesResponse(
        node_id=install_utils.read_node_id(),
        generated_at=time.time(),
        services=services,
    )


@router.post("/jobs/install", response_model=JobCreateResponse)
async def install_service(req: ServiceRequest):
    try:
        category = _find_category(req.category)
        if category.get("category") == "AndroidEmulator":
            raise HTTPException(
                status_code=400,
                detail="Use the emulator endpoints for AndroidEmulator",
            )
        service = _find_service(category, req.name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if install_utils.current_os not in service.get("os", []):
        raise HTTPException(status_code=400, detail="Service not supported on current OS")

    job = _submit_job(
        action="install",
        category=req.category,
        name=req.name,
        payload={"user_password": req.user_password},
        request_id=req.request_id,
    )
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        action=job.action,
        category=job.category,
        name=job.name,
        request_id=job.request_id,
        submitted_at=job.created_at,
    )


@router.post("/jobs/status", response_model=JobCreateResponse)
async def status_service(req: ServiceRequest):
    try:
        category = _find_category(req.category)
        if category.get("category") == "AndroidEmulator":
            raise HTTPException(
                status_code=400,
                detail="Use the emulator endpoints for AndroidEmulator",
            )
        service = _find_service(category, req.name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if install_utils.current_os not in service.get("os", []):
        raise HTTPException(status_code=400, detail="Service not supported on current OS")

    job = _submit_job(
        action="status",
        category=req.category,
        name=req.name,
        payload={},
        request_id=req.request_id,
    )
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        action=job.action,
        category=job.category,
        name=job.name,
        request_id=job.request_id,
        submitted_at=job.created_at,
    )


@router.post("/jobs/android-emulator/refresh-installed", response_model=JobCreateResponse)
async def android_emulator_refresh():
    job = _submit_job(action="android_emulator_refresh")
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        action=job.action,
        category=None,
        name=None,
        request_id=None,
        submitted_at=job.created_at,
    )


@router.post("/jobs/android-emulator/list-installables", response_model=JobCreateResponse)
async def android_emulator_list_installables():
    job = _submit_job(action="android_emulator_list_installables")
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        action=job.action,
        category=None,
        name=None,
        request_id=None,
        submitted_at=job.created_at,
    )


@router.post("/jobs/android-emulator/create", response_model=JobCreateResponse)
async def android_emulator_create(req: AndroidEmulatorCreateRequest):
    job = _submit_job(
        action="android_emulator_create",
        payload={"device_id": req.device_id, "device_name": req.device_name},
        request_id=req.request_id,
    )
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        action=job.action,
        category=None,
        name=None,
        request_id=job.request_id,
        submitted_at=job.created_at,
    )


@router.post("/jobs/android-emulator/launch", response_model=JobCreateResponse)
async def android_emulator_launch(req: AndroidEmulatorLaunchRequest):
    job = _submit_job(
        action="android_emulator_launch",
        payload={"name": req.name},
        request_id=req.request_id,
    )
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        action=job.action,
        category=None,
        name=None,
        request_id=job.request_id,
        submitted_at=job.created_at,
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def job_status(job_id: str):
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        action=job.action,
        category=job.category,
        name=job.name,
        request_id=job.request_id,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error=job.error,
        result=job.result,
        last_event=job.last_event,
    )


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str):
    if not JOB_STORE.get(job_id):
        raise HTTPException(status_code=404, detail="Job not found")

    queue = EVENT_BUS.subscribe(job_id)

    async def event_stream():
        try:
            yield ": connected\n\n"
            while True:
                event = await queue.get()
                yield f"event: {event.get('type', 'message')}\n"
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            EVENT_BUS.unsubscribe(job_id, queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/events")
async def all_events():
    queue = EVENT_BUS.subscribe("*")

    async def event_stream():
        try:
            yield ": connected\n\n"
            while True:
                event = await queue.get()
                yield f"event: {event.get('type', 'message')}\n"
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            EVENT_BUS.unsubscribe("*", queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# --- System info --- #


@router.get("/system-info", response_model=SystemInfoResponse)
async def system_info():
    data = await get_formatted_system_info()
    return SystemInfoResponse(
        node_id=install_utils.read_node_id(),
        generated_at=time.time(),
        data=data,
    )


# --- Installer log download (node-side; Zeuz UI fetches from node host:port) --- #


@router.get("/logs/download")
async def download_installer_log():
    """Serve the current installer log file. Returns 404 if log dir or file is missing."""
    try:
        log_dir = install_log_config.get_installer_log_dir()
        log_path = log_dir / install_log_config.INSTALLER_LOG_FILENAME
        if not log_path.is_file():
            raise HTTPException(status_code=404, detail="Installer log not found")
        return FileResponse(
            path=str(log_path),
            filename=install_log_config.INSTALLER_LOG_FILENAME,
            media_type="text/plain",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Installer log not found")
