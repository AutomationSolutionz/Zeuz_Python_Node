"""
Shared config and logger for the install handler.
Used by installer modules for console + (when set up) rotating file logging.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

INSTALLER_LOG_DIR: Path | None = None
INSTALLER_LOGGER_NAME = "Framework.install_handler"
INSTALLER_LOG_FILENAME = "installer.log"
LOG_FORMAT = "{message}"
LOG_DATE_FMT = "%Y-%m-%d %H:%M"
ROTATING_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
ROTATING_BACKUP_COUNT = 3


def get_installer_log_dir() -> Path:
    """Return the directory for installer log files. Uses default if not yet set."""
    if INSTALLER_LOG_DIR is not None:
        return INSTALLER_LOG_DIR
    return Path.home() / ".zeuz" / "logs"


def get_logger() -> logging.Logger:
    """Return the shared installer logger. Handlers are attached by setup_installer_logging()."""
    return logging.getLogger(INSTALLER_LOGGER_NAME)


def setup_installer_logging(log_dir: Path | None = None) -> None:
    """
    Attach console and (optionally) rotating file handler to the installer logger.
    Safe to call multiple times; avoids duplicate handlers.

    Under no circumstances does this function raise. If anything fails (e.g. log
    dir creation, file open, permissions), we continue without the file handler
    or, in the worst case, without any handlers—the node and installer must
    never be interrupted by logging setup.
    """
    try:
        global INSTALLER_LOG_DIR
        if log_dir is not None:
            INSTALLER_LOG_DIR = log_dir
        effective_dir = get_installer_log_dir()

        logger = logging.getLogger(INSTALLER_LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(LOG_FORMAT, style="{", datefmt=LOG_DATE_FMT)

        # Avoid duplicate handlers: remove existing ones from this logger
        for h in list(logger.handlers):
            logger.removeHandler(h)

        # Console (always)
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(formatter)
        logger.addHandler(console)

        # Rotating file: only if we can create the dir and open the file.
        # On any failure we keep console-only; never re-raise.
        try:
            effective_dir.mkdir(parents=True, exist_ok=True)
            log_file = effective_dir / INSTALLER_LOG_FILENAME
            # Truncate so this process only has current-session logs; then append
            try:
                log_file.open("w", encoding="utf-8").close()
            except Exception:
                pass
            file_handler = RotatingFileHandler(
                log_file,
                mode="a",
                maxBytes=ROTATING_MAX_BYTES,
                backupCount=ROTATING_BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # File logging unavailable (permissions, read-only, disk full, etc.)
            logger.warning("Installer file logging disabled (could not create log file)")
    except Exception:
        # Do not re-raise. Node and installer must never be interrupted.
        print("[installer] Logging setup failed; continuing without installer log.", file=sys.stderr)
