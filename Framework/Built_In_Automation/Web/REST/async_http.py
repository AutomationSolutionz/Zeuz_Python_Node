import asyncio
import httpx
from typing import List, Optional, Union, Dict, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# Define the type for client certificates
CertTypes = Union[
    str,  # certfile
    Tuple[str, Optional[str]],  # (certfile, keyfile)
    Tuple[str, Optional[str], Optional[str]],  # (certfile, keyfile, password)
]


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    TRACE = "TRACE"
    CONNECT = "CONNECT"


class FormDataValue(BaseModel):
    Str: Optional[str] = None
    FilePath: Optional[Tuple[str, str]] = None  # (path, content_type)


class KeyValue(BaseModel):
    key: str
    value: Union[str, FormDataValue]


class HttpBodyType(str, Enum):
    EMPTY = "Empty"
    RAW = "Raw"
    FORM_DATA = "FormData"
    FORM_URL_ENCODED = "FormUrlEncoded"
    MULTIPART = "Multipart"


class HttpBody(BaseModel):
    type: HttpBodyType
    content: Optional[Union[str, List[KeyValue]]] = None


class HttpRequestParam(BaseModel):
    url: str
    method: HttpMethod = HttpMethod.GET
    headers: List[KeyValue] = Field(default_factory=list)
    body: HttpBody = Field(default_factory=lambda: HttpBody(type=HttpBodyType.EMPTY))
    query_params: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 60
    redirect_limit: Optional[int] = 5
    auth: Optional[Tuple[str, str]] = None  # (username, password) for basic auth
    cookies: Optional[Dict[str, str]] = None
    # Verify the authenticity of the requested host.
    ssl_verify: Optional[Union[bool, str]] = True  # bool or path to certificate file
    proxies: Optional[Dict[str, str]] = None  # {"http": "http://proxy.example.com"}
    # Send client side certificates to the requested host, so it can verify who
    # (client) is sending the request.
    cert: Optional[CertTypes] = None  # Client certificate


class HttpResponse(BaseModel):
    status_code: int
    body: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    url: str
    method: str
    time_stamp: str


async def make_request(param: HttpRequestParam) -> HttpResponse:
    async with httpx.AsyncClient(
        timeout=param.timeout,
        follow_redirects=param.redirect_limit is not None,
        proxies=param.proxies, # type: ignore
        verify=param.ssl_verify, # type: ignore
        cert=param.cert,  # Pass the client certificate
    ) as client:
        headers = {
            kv.key: kv.value if isinstance(kv.value, str) else kv.value.dict()
            for kv in param.headers
        }
        body = None

        if param.body.type == HttpBodyType.RAW:
            body = param.body.content
        elif param.body.type == HttpBodyType.FORM_DATA:
            body = {
                kv.key: kv.value.Str or kv.value.FilePath for kv in param.body.content
            }
        elif param.body.type == HttpBodyType.FORM_URL_ENCODED:
            body = {kv.key: kv.value for kv in param.body.content}
        elif param.body.type == HttpBodyType.MULTIPART:
            body = {
                kv.key: kv.value.FilePath for kv in param.body.content
            }  # Handle files with content_type

        response = await client.request(
            method=param.method,
            url=param.url,
            headers=headers,
            data=body,
            params=param.query_params,
            cookies=param.cookies,
            auth=param.auth,
        )

        response_body = response.text
        response_headers = dict(response.headers)
        response_cookies = dict(response.cookies)

        # Capture the time of the request
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # Return a structured response object
        return HttpResponse(
            status_code=response.status_code,
            body=response_body,
            headers=response_headers,
            cookies=response_cookies,
            url=str(response.url),
            method=param.method.value,
            time_stamp=time_stamp,
        )


async def main():
    param = HttpRequestParam(
        url="https://example.com/upload",
        method=HttpMethod.POST,
        headers=[KeyValue(key="Authorization", value="Bearer your_token")],
        body=HttpBody(
            type=HttpBodyType.MULTIPART,
            content=[
                KeyValue(
                    key="file",
                    value=FormDataValue(FilePath=("path/to/file.txt", "text/plain")),
                ),
                KeyValue(
                    key="description", value=FormDataValue(Str="Sample file upload")
                ),
            ],
        ),
        ssl_verify="path/to/ca_cert.pem",  # Path to a CA certificate file
        cert=(
            "path/to/client_cert.pem",
            "path/to/client_key.pem",
        ),  # Client certificate and key
    )

    response = await make_request(param)
    print(response.model_dump_json())  # Serialize the response to JSON


asyncio.run(main())
