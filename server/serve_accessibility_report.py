"""
API endpoint for serving accessibility HTML reports from the node's filesystem.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from urllib.parse import unquote

router = APIRouter(prefix="/debug/reports", tags=["debug-reports"])
REPORTS_BASE_DIR = Path("reports/accessibility").resolve()


@router.get("/accessibility")
def serve_accessibility_report(file_path: str):
    
    try:
        # Decode URL-encoded path
        print("Serving accessi file")
        decoded_path = unquote(file_path)
        requested_path = Path(decoded_path)

        # Reject absolute paths and traversal attempts before joining
        if requested_path.is_absolute() or ".." in requested_path.parts:
            raise HTTPException(
                status_code=400,
                detail="Invalid report path"
            )

        # Resolve path under a fixed reports directory to prevent traversal
        html_file = (REPORTS_BASE_DIR / requested_path).resolve()
        try:
            html_file.relative_to(REPORTS_BASE_DIR)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid report path"
            )
        
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
