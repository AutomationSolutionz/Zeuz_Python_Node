"""
API endpoint for serving accessibility HTML reports from the node's filesystem.

The node server runs on the same machine where test execution occurs, so it can directly
access and serve files from the local filesystem where accessibility reports are saved.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from urllib.parse import unquote

router = APIRouter(prefix="/debug/reports", tags=["debug-reports"])


@router.get("/accessibility")
def serve_accessibility_report(file_path: str):
    """
    Serve accessibility HTML report by full file path.
    
    This endpoint serves the HTML file directly from the node's filesystem where the
    accessibility test was executed. The node server runs on the same machine as the
    test execution, allowing direct file system access.
    
    **Endpoint:**
    ```
    GET /api/v1/debug/reports/accessibility?file_path={full_path}
    ```
    
    **Example Request:**
    ```
    GET http://127.0.0.1:18100/api/v1/debug/reports/accessibility?file_path=C%3A%2FUsers%2Fuser%2FZeuz_Python_Node%2FAutomationLog%2Fdebug_abc123%2Fsession_1%2FTEST-123%2Fzeuz_download_folder%2Faccessibility_report_example_com_20250120_143022.html
    ```
    
    **Example with decoded path:**
    ```
    GET http://127.0.0.1:18100/api/v1/debug/reports/accessibility?file_path=C:/Users/user/Zeuz_Python_Node/AutomationLog/debug_abc123/session_1/TEST-123/zeuz_download_folder/accessibility_report_example_com_20250120_143022.html
    ```
    
    **Parameter:**
    - `file_path` (query parameter, required): The full absolute path to the accessibility HTML report file
      - Can be Windows path: `C:/Users/.../zeuz_download_folder/accessibility_report_*.html`
      - Can be Unix path: `/home/user/.../zeuz_download_folder/accessibility_report_*.html`
      - Should be URL-encoded if containing special characters
      - The path is extracted from the log message: `"HTML report saved to zeuz_download_folder: {html_path}"`
    
    **File Location:**
    The file is served from the machine where the ZeuZ node is running. The node server
    has direct filesystem access to the AutomationLog directory where test artifacts
    (including accessibility reports) are stored during test execution.
    
    **Returns:**
    - `200 OK`: FileResponse with the HTML report content
    - `400 Bad Request`: If path is not a file or not an HTML file
    - `404 Not Found`: If the file doesn't exist
    - `500 Internal Server Error`: If there's an error reading the file
    
    **Example Response:**
    ```
    Content-Type: text/html
    Content-Disposition: attachment; filename="accessibility_report_example_com_20250120_143022.html"
    
    <!DOCTYPE html>
    <html>...</html>
    ```
    """
    try:
        # Decode URL-encoded path
        decoded_path = unquote(file_path)
        
        # Convert to Path object (handles both Windows and Unix paths)
        html_file = Path(decoded_path)
        
        # Security check: ensure file exists and is a file (not a directory)
        if not html_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Accessibility report file not found: {file_path}"
            )
        
        if not html_file.is_file():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a file: {file_path}"
            )
        
        # Verify it's an HTML file
        if html_file.suffix.lower() != ".html":
            raise HTTPException(
                status_code=400,
                detail=f"File is not an HTML file: {file_path}"
            )
        
        return FileResponse(
            str(html_file),
            media_type="text/html",
            filename=html_file.name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve accessibility report: {str(e)}")
