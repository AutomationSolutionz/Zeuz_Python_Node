import os
import glob
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional

router = APIRouter(prefix="/debug/reports/security", tags=["security-reports"])

# Resolve the Node's root directory relative to THIS file's location
# This file lives at: <node_root>/server/reports.py
NODE_ROOT = Path(__file__).resolve().parent.parent
AUTO_LOG_DIR = NODE_ROOT / "AutomationLog"


@router.get("")
def get_security_report(file_path: Optional[str] = None):
    """
    Security report downloader for the ZeuZ Node.

    - file_path (optional): exact path of the report file (absolute OR relative to a run dir).
      If not given, the newest HTML file in the security_report folder is returned.
    """
    try:
        # ── Case 1: caller supplied an explicit file path ──────────────────────
        if file_path:
            p = Path(file_path)

            # Absolute path provided
            if p.is_absolute() and p.is_file():
                return FileResponse(str(p))

            # Relative path – search across every debug run folder (newest first)
            run_dirs = sorted(
                AUTO_LOG_DIR.glob("debug_*/session_*/*"),
                key=lambda d: d.stat().st_mtime,
                reverse=True,
            )
            for run_dir in run_dirs:
                candidate = run_dir / file_path
                if candidate.is_file():
                    return FileResponse(str(candidate))

        # ── Case 2: auto-find the newest HTML in any security_report folder ──
        candidates = list(AUTO_LOG_DIR.glob("debug_*/session_*/*/security_report/*.html"))

        if not candidates:
            return JSONResponse(
                {"error": f"No security report found. Searched in: {AUTO_LOG_DIR}"},
                status_code=404,
            )

        latest_report = max(candidates, key=lambda f: f.stat().st_mtime)
        return FileResponse(str(latest_report))

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
