import platform
import subprocess
import asyncio
import re
import time
from typing import Dict, List, Any, Optional
try:
    import psutil
except ImportError:
    psutil = None


def get_system_uptime() -> Dict[str, Any]:
    """
    Get system uptime in seconds and human-readable format.
    Returns a dictionary with uptime_seconds and uptime_human.
    """
    try:
        if psutil:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
        else:
            system = platform.system()
            if system == "Linux":
                try:
                    result = subprocess.run(
                        ["cat", "/proc/uptime"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    if result.returncode == 0:
                        uptime_seconds = float(result.stdout.split()[0])
                    else:
                        uptime_seconds = None
                except Exception:
                    uptime_seconds = None
            elif system == "Darwin":
                try:
                    result = subprocess.run(
                        ["sysctl", "-n", "kern.boottime"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    if result.returncode == 0:
                        # Format: { sec = 1234567890, usec = 0 } Mon Jan 1 00:00:00 2000
                        import re
                        match = re.search(r'sec\s*=\s*(\d+)', result.stdout)
                        if match:
                            boot_time = int(match.group(1))
                            uptime_seconds = time.time() - boot_time
                        else:
                            uptime_seconds = None
                    else:
                        uptime_seconds = None
                except Exception:
                    uptime_seconds = None
            elif system == "Windows":
                try:
                    result = subprocess.run(
                        ["wmic", "os", "get", "LastBootUpTime"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split("\n")
                        if len(lines) > 1:
                            boot_time_str = lines[1].strip()
                            # Format: 20240101120000.000000+000
                            from datetime import datetime
                            boot_time = datetime.strptime(boot_time_str[:14], "%Y%m%d%H%M%S").timestamp()
                            uptime_seconds = time.time() - boot_time
                        else:
                            uptime_seconds = None
                    else:
                        uptime_seconds = None
                except Exception:
                    uptime_seconds = None
            else:
                uptime_seconds = None
        
        if uptime_seconds is not None:
            # Convert to human-readable format
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if days > 0:
                uptime_human = f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                uptime_human = f"{hours}h {minutes}m"
            else:
                uptime_human = f"{minutes}m"
            
            return {
                "uptime_seconds": int(uptime_seconds),
                "uptime_human": uptime_human
            }
        else:
            return {
                "uptime_seconds": None,
                "uptime_human": "Unknown"
            }
    except Exception as e:
        print(f"[installer][system-info] Error getting uptime: {e}")
        return {
            "uptime_seconds": None,
            "uptime_human": "Unknown"
        }


def get_device_model() -> str:
    """
    Get device/model name if available.
    Returns device model string or "Unknown".
    """
    try:
        system = platform.system()
        if system == "Linux":
            try:
                # Try to get product name from /sys/class/dmi/id/product_name
                result = subprocess.run(
                    ["cat", "/sys/class/dmi/id/product_name"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    model = result.stdout.strip()
                    if model:
                        return model
            except Exception:
                pass
            
            try:
                # Try to get model from /proc/device-tree/model
                result = subprocess.run(
                    ["cat", "/proc/device-tree/model"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    model = result.stdout.strip()
                    if model:
                        return model
            except Exception:
                pass
        elif system == "Darwin":
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "hw.model"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass
        elif system == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "computersystem", "get", "model"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        return lines[1].strip()
            except Exception:
                pass
        
        return "Unknown"
    except Exception as e:
        print(f"[installer][system-info] Error getting device model: {e}")
        return "Unknown"


def get_os_info() -> Dict[str, str]:
    """
    Get OS details (name, version, release).
    Returns a dictionary with os_name, os_version, and os_release.
    """
    try:
        system = platform.system()
        release = platform.release()
        version = platform.version()
        
        # Get more specific OS name
        os_name = system
        if system == "Linux":
            # Try to get distribution name
            try:
                result = subprocess.run(
                    ["lsb_release", "-si"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    os_name = result.stdout.strip()
                else:
                    # Try /etc/os-release
                    try:
                        with open("/etc/os-release", "r") as f:
                            for line in f:
                                if line.startswith("NAME="):
                                    os_name = line.split("=", 1)[1].strip().strip('"')
                                    break
                    except Exception:
                        pass
            except Exception:
                pass
        elif system == "Darwin":
            os_name = "macOS"
            # Get macOS version
            try:
                result = subprocess.run(
                    ["sw_vers", "-productVersion"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
            except Exception:
                pass
        elif system == "Windows":
            os_name = "Windows"
            # Get Windows version
            try:
                result = subprocess.run(
                    ["cmd", "/c", "ver"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
            except Exception:
                pass
        
        return {
            "os_name": os_name,
            "os_version": version,
            "os_release": release
        }
    except Exception as e:
        print(f"[installer][system-info] Error getting OS info: {e}")
        return {
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release()
        }


def get_cpu_info() -> Dict[str, Any]:
    """
    Get CPU info (cores, model, architecture).
    Returns a dictionary with cpu_cores, cpu_model, and cpu_architecture.
    """
    try:
        cpu_cores = psutil.cpu_count(logical=True) if psutil else None
        cpu_physical_cores = psutil.cpu_count(logical=False) if psutil else None
        cpu_architecture = platform.machine()
        cpu_model = "Unknown"
        
        system = platform.system()
        
        if system == "Linux":
            try:
                # Try to get CPU model from /proc/cpuinfo
                result = subprocess.run(
                    ["grep", "-m", "1", "model name", "/proc/cpuinfo"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    cpu_model = result.stdout.split(":", 1)[1].strip()
            except Exception:
                pass
        elif system == "Darwin":
            try:
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    cpu_model = result.stdout.strip()
            except Exception:
                pass
        elif system == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "cpu", "get", "name"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) > 1:
                        cpu_model = lines[1].strip()
            except Exception:
                pass
        
        # Get CPU usage and load average
        cpu_usage_percent = None
        cpu_load_avg = None
        cpu_temperature = None
        
        if psutil:
            # CPU usage percentage (average across all cores)
            cpu_usage_percent = psutil.cpu_percent(interval=0.1)
            
            # Load average (1m, 5m, 15m) - only available on Unix systems
            if system in ["Linux", "Darwin"]:
                try:
                    load_avg = psutil.getloadavg()
                    cpu_load_avg = {
                        "1m": round(load_avg[0], 2),
                        "5m": round(load_avg[1], 2),
                        "15m": round(load_avg[2], 2)
                    }
                except AttributeError:
                    # getloadavg() not available on this system
                    pass
            
            # CPU temperature (if available)
            if hasattr(psutil, "sensors_temperatures"):
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        # Get CPU temperature (look for 'cpu_thermal', 'coretemp', etc.)
                        for name, entries in temps.items():
                            if 'cpu' in name.lower() or 'core' in name.lower():
                                if entries:
                                    cpu_temperature = round(entries[0].current, 1)
                                    break
                except Exception:
                    pass
        
        return {
            "cpu_cores": cpu_cores,
            "cpu_physical_cores": cpu_physical_cores,
            "cpu_model": cpu_model,
            "cpu_architecture": cpu_architecture,
            "cpu_usage_percent": cpu_usage_percent,
            "cpu_load_avg": cpu_load_avg,
            "cpu_temperature": cpu_temperature
        }
    except Exception as e:
        print(f"[installer][system-info] Error getting CPU info: {e}")
        return {
            "cpu_cores": None,
            "cpu_physical_cores": None,
            "cpu_model": "Unknown",
            "cpu_architecture": platform.machine()
        }


def get_memory_info() -> Dict[str, Any]:
    """
    Get memory info (total RAM and swap).
    Returns a dictionary with total_ram and swap info (in bytes and human-readable format).
    """
    try:
        if psutil:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            total_ram_bytes = memory.total
            total_ram_gb = total_ram_bytes / (1024 ** 3)
            total_ram_mb = total_ram_bytes / (1024 ** 2)
            
            swap_total_bytes = swap.total
            swap_used_bytes = swap.used
            swap_free_bytes = swap.free
            swap_total_gb = swap_total_bytes / (1024 ** 3)
            swap_used_gb = swap_used_bytes / (1024 ** 3)
            swap_free_gb = swap_free_bytes / (1024 ** 3)
            swap_percent = swap.percent if swap_total_bytes > 0 else 0
            
            # Get RAM usage details
            used_ram_bytes = memory.used
            free_ram_bytes = memory.available
            used_ram_gb = used_ram_bytes / (1024 ** 3)
            free_ram_gb = free_ram_bytes / (1024 ** 3)
            ram_percent = memory.percent
            
            return {
                "total_ram_bytes": total_ram_bytes,
                "total_ram_gb": round(total_ram_gb, 2),
                "total_ram_mb": round(total_ram_mb, 2),
                "total_ram_human": f"{total_ram_gb:.2f} GB",
                "used_ram_bytes": used_ram_bytes,
                "used_ram_gb": round(used_ram_gb, 2),
                "used_ram_human": f"{used_ram_gb:.2f} GB",
                "free_ram_bytes": free_ram_bytes,
                "free_ram_gb": round(free_ram_gb, 2),
                "free_ram_human": f"{free_ram_gb:.2f} GB",
                "ram_percent": round(ram_percent, 2),
                "swap_total_bytes": swap_total_bytes,
                "swap_total_gb": round(swap_total_gb, 2),
                "swap_total_human": f"{swap_total_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                "swap_used_bytes": swap_used_bytes,
                "swap_used_gb": round(swap_used_gb, 2),
                "swap_used_human": f"{swap_used_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                "swap_free_bytes": swap_free_bytes,
                "swap_free_gb": round(swap_free_gb, 2),
                "swap_free_human": f"{swap_free_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                "swap_percent": round(swap_percent, 2) if swap_total_bytes > 0 else 0
            }
        else:
            # Fallback for systems without psutil
            system = platform.system()
            if system == "Linux":
                try:
                    # Get RAM info
                    ram_result = subprocess.run(
                        ["grep", "MemTotal", "/proc/meminfo"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    
                    # Get swap info
                    swap_total_result = subprocess.run(
                        ["grep", "SwapTotal", "/proc/meminfo"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    
                    swap_free_result = subprocess.run(
                        ["grep", "SwapFree", "/proc/meminfo"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    
                    total_ram_bytes = None
                    swap_total_bytes = 0
                    swap_free_bytes = 0
                    
                    if ram_result.returncode == 0:
                        # Format: MemTotal:       16384000 kB
                        parts = ram_result.stdout.split()
                        if len(parts) >= 2:
                            total_ram_kb = int(parts[1])
                            total_ram_bytes = total_ram_kb * 1024
                    
                    if swap_total_result.returncode == 0:
                        parts = swap_total_result.stdout.split()
                        if len(parts) >= 2:
                            swap_total_kb = int(parts[1])
                            swap_total_bytes = swap_total_kb * 1024
                    
                    if swap_free_result.returncode == 0:
                        parts = swap_free_result.stdout.split()
                        if len(parts) >= 2:
                            swap_free_kb = int(parts[1])
                            swap_free_bytes = swap_free_kb * 1024
                    
                    swap_used_bytes = swap_total_bytes - swap_free_bytes
                    swap_total_gb = swap_total_bytes / (1024 ** 3)
                    swap_used_gb = swap_used_bytes / (1024 ** 3)
                    swap_free_gb = swap_free_bytes / (1024 ** 3)
                    swap_percent = (swap_used_bytes / swap_total_bytes * 100) if swap_total_bytes > 0 else 0
                    
                    if total_ram_bytes:
                        total_ram_gb = total_ram_bytes / (1024 ** 3)
                        return {
                            "total_ram_bytes": total_ram_bytes,
                            "total_ram_gb": round(total_ram_gb, 2),
                            "total_ram_mb": round(total_ram_bytes / (1024 ** 2), 2),
                            "total_ram_human": f"{total_ram_gb:.2f} GB",
                            "swap_total_bytes": swap_total_bytes,
                            "swap_total_gb": round(swap_total_gb, 2),
                            "swap_total_human": f"{swap_total_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_used_bytes": swap_used_bytes,
                            "swap_used_gb": round(swap_used_gb, 2),
                            "swap_used_human": f"{swap_used_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_free_bytes": swap_free_bytes,
                            "swap_free_gb": round(swap_free_gb, 2),
                            "swap_free_human": f"{swap_free_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_percent": round(swap_percent, 2) if swap_total_bytes > 0 else 0
                        }
                except Exception:
                    pass
            elif system == "Darwin":
                try:
                    # Get RAM
                    ram_result = subprocess.run(
                        ["sysctl", "-n", "hw.memsize"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    
                    # Get swap info
                    swap_result = subprocess.run(
                        ["sysctl", "-n", "vm.swapusage"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    
                    total_ram_bytes = None
                    swap_total_bytes = 0
                    swap_used_bytes = 0
                    swap_free_bytes = 0
                    
                    if ram_result.returncode == 0:
                        total_ram_bytes = int(ram_result.stdout.strip())
                    
                    if swap_result.returncode == 0:
                        # Format: total = 4096.00M  used = 0.00M  free = 4096.00M  (encrypted)
                        swap_output = swap_result.stdout.strip()
                        # Parse the swap output
                        total_match = re.search(r'total\s*=\s*([\d.]+)([KMGT]?)', swap_output, re.IGNORECASE)
                        used_match = re.search(r'used\s*=\s*([\d.]+)([KMGT]?)', swap_output, re.IGNORECASE)
                        free_match = re.search(r'free\s*=\s*([\d.]+)([KMGT]?)', swap_output, re.IGNORECASE)
                        
                        def parse_size(value: str, unit: str) -> int:
                            """Convert size string to bytes"""
                            val = float(value)
                            unit = unit.upper()
                            if unit == 'K':
                                return int(val * 1024)
                            elif unit == 'M':
                                return int(val * 1024 * 1024)
                            elif unit == 'G':
                                return int(val * 1024 * 1024 * 1024)
                            elif unit == 'T':
                                return int(val * 1024 * 1024 * 1024 * 1024)
                            else:
                                return int(val)
                        
                        if total_match:
                            swap_total_bytes = parse_size(total_match.group(1), total_match.group(2) or 'M')
                        if used_match:
                            swap_used_bytes = parse_size(used_match.group(1), used_match.group(2) or 'M')
                        if free_match:
                            swap_free_bytes = parse_size(free_match.group(1), free_match.group(2) or 'M')
                    
                    swap_total_gb = swap_total_bytes / (1024 ** 3)
                    swap_used_gb = swap_used_bytes / (1024 ** 3)
                    swap_free_gb = swap_free_bytes / (1024 ** 3)
                    swap_percent = (swap_used_bytes / swap_total_bytes * 100) if swap_total_bytes > 0 else 0
                    
                    if total_ram_bytes:
                        total_ram_gb = total_ram_bytes / (1024 ** 3)
                        return {
                            "total_ram_bytes": total_ram_bytes,
                            "total_ram_gb": round(total_ram_gb, 2),
                            "total_ram_mb": round(total_ram_bytes / (1024 ** 2), 2),
                            "total_ram_human": f"{total_ram_gb:.2f} GB",
                            "swap_total_bytes": swap_total_bytes,
                            "swap_total_gb": round(swap_total_gb, 2),
                            "swap_total_human": f"{swap_total_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_used_bytes": swap_used_bytes,
                            "swap_used_gb": round(swap_used_gb, 2),
                            "swap_used_human": f"{swap_used_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_free_bytes": swap_free_bytes,
                            "swap_free_gb": round(swap_free_gb, 2),
                            "swap_free_human": f"{swap_free_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_percent": round(swap_percent, 2) if swap_total_bytes > 0 else 0
                        }
                except Exception:
                    pass
            elif system == "Windows":
                try:
                    # Get RAM
                    ram_result = subprocess.run(
                        ["wmic", "computersystem", "get", "TotalPhysicalMemory"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    
                    # Get swap info (page file)
                    swap_result = subprocess.run(
                        ["wmic", "pagefile", "get", "AllocatedBaseSize,CurrentUsage"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False
                    )
                    
                    total_ram_bytes = None
                    swap_total_bytes = 0
                    swap_used_bytes = 0
                    swap_free_bytes = 0
                    
                    if ram_result.returncode == 0:
                        lines = ram_result.stdout.strip().split("\n")
                        if len(lines) > 1:
                            total_ram_bytes = int(lines[1].strip())
                    
                    if swap_result.returncode == 0:
                        # Parse page file info (size is in MB)
                        lines = swap_result.stdout.strip().split("\n")
                        for line in lines[1:]:  # Skip header
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    allocated_mb = int(parts[0])
                                    used_mb = int(parts[1]) if parts[1].isdigit() else 0
                                    swap_total_bytes = allocated_mb * 1024 * 1024
                                    swap_used_bytes = used_mb * 1024 * 1024
                                    swap_free_bytes = swap_total_bytes - swap_used_bytes
                                    break
                                except (ValueError, IndexError):
                                    continue
                    
                    swap_total_gb = swap_total_bytes / (1024 ** 3)
                    swap_used_gb = swap_used_bytes / (1024 ** 3)
                    swap_free_gb = swap_free_bytes / (1024 ** 3)
                    swap_percent = (swap_used_bytes / swap_total_bytes * 100) if swap_total_bytes > 0 else 0
                    
                    if total_ram_bytes:
                        total_ram_gb = total_ram_bytes / (1024 ** 3)
                        return {
                            "total_ram_bytes": total_ram_bytes,
                            "total_ram_gb": round(total_ram_gb, 2),
                            "total_ram_mb": round(total_ram_bytes / (1024 ** 2), 2),
                            "total_ram_human": f"{total_ram_gb:.2f} GB",
                            "swap_total_bytes": swap_total_bytes,
                            "swap_total_gb": round(swap_total_gb, 2),
                            "swap_total_human": f"{swap_total_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_used_bytes": swap_used_bytes,
                            "swap_used_gb": round(swap_used_gb, 2),
                            "swap_used_human": f"{swap_used_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_free_bytes": swap_free_bytes,
                            "swap_free_gb": round(swap_free_gb, 2),
                            "swap_free_human": f"{swap_free_gb:.2f} GB" if swap_total_bytes > 0 else "0 GB",
                            "swap_percent": round(swap_percent, 2) if swap_total_bytes > 0 else 0
                        }
                except Exception:
                    pass
        
        return {
            "total_ram_bytes": None,
            "total_ram_gb": None,
            "total_ram_mb": None,
            "total_ram_human": "Unknown",
            "swap_total_bytes": 0,
            "swap_total_gb": 0,
            "swap_total_human": "0 GB",
            "swap_used_bytes": 0,
            "swap_used_gb": 0,
            "swap_used_human": "0 GB",
            "swap_free_bytes": 0,
            "swap_free_gb": 0,
            "swap_free_human": "0 GB",
            "swap_percent": 0
        }
    except Exception as e:
        print(f"[installer][system-info] Error getting memory info: {e}")
        return {
            "total_ram_bytes": None,
            "total_ram_gb": None,
            "total_ram_mb": None,
            "total_ram_human": "Unknown",
            "swap_total_bytes": 0,
            "swap_total_gb": 0,
            "swap_total_human": "0 GB",
            "swap_used_bytes": 0,
            "swap_used_gb": 0,
            "swap_used_human": "0 GB",
            "swap_free_bytes": 0,
            "swap_free_gb": 0,
            "swap_free_human": "0 GB",
            "swap_percent": 0
        }


def _should_include_mount_point(device: str, mountpoint: str, fstype: str) -> bool:
    """
    Determine if a mount point should be included in disk info.
    Filters out snap mounts, loop devices, and other virtual filesystems.
    """
    # Filter out snap mounts (they're loop devices, part of main filesystem)
    if mountpoint.startswith("/snap/"):
        return False
    
    # Filter out loop devices
    if device.startswith("/dev/loop"):
        return False
    
    # Filter out virtual filesystems
    virtual_fs = ["tmpfs", "devtmpfs", "sysfs", "proc", "devpts", "cgroup", "cgroup2", "pstore", "bpf", "tracefs", "debugfs", "securityfs", "hugetlbfs", "mqueue", "overlay", "autofs", "binfmt_misc"]
    if fstype in virtual_fs:
        return False
    
    # Filter out virtual mount points
    virtual_mounts = ["/proc", "/sys", "/dev", "/run", "/tmp", "/var/run"]
    if mountpoint in virtual_mounts or mountpoint.startswith("/proc/") or mountpoint.startswith("/sys/"):
        return False
    
    return True


def get_disk_info() -> Dict[str, Any]:
    """
    Get disk info (total space, mount points).
    Returns a dictionary with total_disk_space and mount_points (list of dictionaries).
    Filters out snap mounts, loop devices, and virtual filesystems to avoid double-counting.
    """
    try:
        mount_points = []
        
        if psutil:
            partitions = psutil.disk_partitions()
            total_disk_space_bytes = 0
            seen_devices = set()  # Track devices to avoid double-counting
            
            for partition in partitions:
                # Skip if we've already seen this device (avoid double-counting)
                if partition.device in seen_devices:
                    continue
                
                # Filter out snap mounts, loop devices, and virtual filesystems
                if not _should_include_mount_point(partition.device, partition.mountpoint, partition.fstype):
                    continue
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Only count each device once (use the largest mount point if device appears multiple times)
                    if partition.device not in seen_devices:
                        total_disk_space_bytes += usage.total
                        seen_devices.add(partition.device)
                    
                    mount_points.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_bytes": usage.total,
                        "total_gb": round(usage.total / (1024 ** 3), 2),
                        "used_bytes": usage.used,
                        "used_gb": round(usage.used / (1024 ** 3), 2),
                        "free_bytes": usage.free,
                        "free_gb": round(usage.free / (1024 ** 3), 2),
                        "percent_used": round(usage.percent, 2)
                    })
                except PermissionError:
                    # Skip partitions we don't have permission to access
                    continue
                except Exception as e:
                    print(f"[installer][system-info] Error getting usage for {partition.mountpoint}: {e}")
                    continue
            
            total_disk_space_gb = total_disk_space_bytes / (1024 ** 3)
            
            # Calculate total used and free disk space
            total_used_bytes = sum(mp.get("used_bytes", 0) for mp in mount_points)
            total_free_bytes = sum(mp.get("free_bytes", 0) for mp in mount_points)
            total_used_gb = total_used_bytes / (1024 ** 3)
            total_free_gb = total_free_bytes / (1024 ** 3)
            disk_percent = (total_used_bytes / total_disk_space_bytes * 100) if total_disk_space_bytes > 0 else 0
            
            # Get disk I/O stats
            disk_io = None
            if psutil:
                try:
                    io_counters = psutil.disk_io_counters()
                    if io_counters:
                        disk_io = {
                            "read_bytes": io_counters.read_bytes,
                            "write_bytes": io_counters.write_bytes,
                            "read_count": io_counters.read_count,
                            "write_count": io_counters.write_count
                        }
                except Exception:
                    pass
            
            return {
                "total_disk_space_bytes": total_disk_space_bytes,
                "total_disk_space_gb": round(total_disk_space_gb, 2),
                "total_disk_space_human": f"{total_disk_space_gb:.2f} GB",
                "total_used_bytes": total_used_bytes,
                "total_used_gb": round(total_used_gb, 2),
                "total_used_human": f"{total_used_gb:.2f} GB",
                "total_free_bytes": total_free_bytes,
                "total_free_gb": round(total_free_gb, 2),
                "total_free_human": f"{total_free_gb:.2f} GB",
                "disk_percent": round(disk_percent, 2),
                "disk_io": disk_io,
                "mount_points": mount_points
            }
        else:
            # Fallback for systems without psutil
            system = platform.system()
            if system == "Linux":
                try:
                    result = subprocess.run(
                        ["df", "-B1", "-x", "tmpfs", "-x", "devtmpfs", "-x", "sysfs", "-x", "proc", "-x", "overlay"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split("\n")
                        total_disk_space_bytes = 0
                        seen_devices = set()
                        
                        # Get individual mount points (skip header)
                        for line in lines[1:]:
                            parts = line.split()
                            if len(parts) >= 6:
                                device = parts[0]
                                mountpoint = parts[5]
                                fstype = parts[1] if len(parts) > 1 else "unknown"
                                
                                # Filter out snap mounts, loop devices, and virtual filesystems
                                if not _should_include_mount_point(device, mountpoint, fstype):
                                    continue
                                
                                # Skip if we've already counted this device
                                if device in seen_devices:
                                    continue
                                
                                total_bytes = int(parts[1])
                                total_disk_space_bytes += total_bytes
                                seen_devices.add(device)
                                
                                mount_points.append({
                                    "device": device,
                                    "mountpoint": mountpoint,
                                    "fstype": fstype,
                                    "total_bytes": total_bytes,
                                    "total_gb": round(total_bytes / (1024 ** 3), 2),
                                    "used_bytes": int(parts[2]),
                                    "used_gb": round(int(parts[2]) / (1024 ** 3), 2),
                                    "free_bytes": int(parts[3]),
                                    "free_gb": round(int(parts[3]) / (1024 ** 3), 2),
                                    "percent_used": round((int(parts[2]) / total_bytes) * 100, 2) if total_bytes > 0 else 0
                                })
                        
                        total_disk_space_gb = total_disk_space_bytes / (1024 ** 3)
                        
                        # Calculate total used and free
                        total_used_bytes = sum(mp.get("used_bytes", 0) for mp in mount_points)
                        total_free_bytes = sum(mp.get("free_bytes", 0) for mp in mount_points)
                        total_used_gb = total_used_bytes / (1024 ** 3)
                        total_free_gb = total_free_bytes / (1024 ** 3)
                        disk_percent = (total_used_bytes / total_disk_space_bytes * 100) if total_disk_space_bytes > 0 else 0
                        
                        return {
                            "total_disk_space_bytes": total_disk_space_bytes,
                            "total_disk_space_gb": round(total_disk_space_gb, 2),
                            "total_disk_space_human": f"{total_disk_space_gb:.2f} GB",
                            "total_used_bytes": total_used_bytes,
                            "total_used_gb": round(total_used_gb, 2),
                            "total_used_human": f"{total_used_gb:.2f} GB",
                            "total_free_bytes": total_free_bytes,
                            "total_free_gb": round(total_free_gb, 2),
                            "total_free_human": f"{total_free_gb:.2f} GB",
                            "disk_percent": round(disk_percent, 2),
                            "disk_io": None,
                            "mount_points": mount_points
                        }
                except Exception as e:
                    print(f"[installer][system-info] Error getting disk info (Linux fallback): {e}")
            elif system == "Darwin":
                try:
                    result = subprocess.run(
                        ["df", "-B1"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split("\n")
                        total_disk_space_bytes = 0
                        for line in lines[1:]:  # Skip header
                            parts = line.split()
                            if len(parts) >= 9:
                                total_bytes = int(parts[1])
                                total_disk_space_bytes += total_bytes
                                mount_points.append({
                                    "device": parts[0],
                                    "mountpoint": parts[8],
                                    "fstype": parts[2] if len(parts) > 2 else "unknown",
                                    "total_bytes": total_bytes,
                                    "total_gb": round(total_bytes / (1024 ** 3), 2),
                                    "used_bytes": int(parts[2]),
                                    "used_gb": round(int(parts[2]) / (1024 ** 3), 2),
                                    "free_bytes": int(parts[3]),
                                    "free_gb": round(int(parts[3]) / (1024 ** 3), 2),
                                    "percent_used": round((int(parts[2]) / total_bytes) * 100, 2) if total_bytes > 0 else 0
                                })
                        
                        total_disk_space_gb = total_disk_space_bytes / (1024 ** 3)
                        return {
                            "total_disk_space_bytes": total_disk_space_bytes,
                            "total_disk_space_gb": round(total_disk_space_gb, 2),
                            "total_disk_space_human": f"{total_disk_space_gb:.2f} GB",
                            "mount_points": mount_points
                        }
                except Exception as e:
                    print(f"[installer][system-info] Error getting disk info (macOS fallback): {e}")
            elif system == "Windows":
                try:
                    result = subprocess.run(
                        ["wmic", "logicaldisk", "get", "size,freespace,caption,filesystem"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False
                    )
                    if result.returncode == 0:
                        lines = result.stdout.strip().split("\n")
                        total_disk_space_bytes = 0
                        for line in lines[1:]:  # Skip header
                            parts = line.split()
                            if len(parts) >= 4:
                                caption = parts[0]
                                fstype = parts[1] if len(parts) > 1 else "unknown"
                                size = int(parts[2]) if parts[2].isdigit() else 0
                                freespace = int(parts[3]) if parts[3].isdigit() else 0
                                used = size - freespace
                                total_disk_space_bytes += size
                                
                                mount_points.append({
                                    "device": caption,
                                    "mountpoint": caption,
                                    "fstype": fstype,
                                    "total_bytes": size,
                                    "total_gb": round(size / (1024 ** 3), 2),
                                    "used_bytes": used,
                                    "used_gb": round(used / (1024 ** 3), 2),
                                    "free_bytes": freespace,
                                    "free_gb": round(freespace / (1024 ** 3), 2),
                                    "percent_used": round((used / size) * 100, 2) if size > 0 else 0
                                })
                        
                        total_disk_space_gb = total_disk_space_bytes / (1024 ** 3)
                        
                        # Calculate total used and free
                        total_used_bytes = sum(mp.get("used_bytes", 0) for mp in mount_points)
                        total_free_bytes = sum(mp.get("free_bytes", 0) for mp in mount_points)
                        total_used_gb = total_used_bytes / (1024 ** 3)
                        total_free_gb = total_free_bytes / (1024 ** 3)
                        disk_percent = (total_used_bytes / total_disk_space_bytes * 100) if total_disk_space_bytes > 0 else 0
                        
                        return {
                            "total_disk_space_bytes": total_disk_space_bytes,
                            "total_disk_space_gb": round(total_disk_space_gb, 2),
                            "total_disk_space_human": f"{total_disk_space_gb:.2f} GB",
                            "total_used_bytes": total_used_bytes,
                            "total_used_gb": round(total_used_gb, 2),
                            "total_used_human": f"{total_used_gb:.2f} GB",
                            "total_free_bytes": total_free_bytes,
                            "total_free_gb": round(total_free_gb, 2),
                            "total_free_human": f"{total_free_gb:.2f} GB",
                            "disk_percent": round(disk_percent, 2),
                            "disk_io": None,
                            "mount_points": mount_points
                        }
                except Exception as e:
                    print(f"[installer][system-info] Error getting disk info (Windows fallback): {e}")
        
        return {
            "total_disk_space_bytes": None,
            "total_disk_space_gb": None,
            "total_disk_space_human": "Unknown",
            "total_used_bytes": None,
            "total_used_gb": None,
            "total_used_human": "Unknown",
            "total_free_bytes": None,
            "total_free_gb": None,
            "total_free_human": "Unknown",
            "disk_percent": None,
            "disk_io": None,
            "mount_points": []
        }
    except Exception as e:
        print(f"[installer][system-info] Error getting disk info: {e}")
        return {
            "total_disk_space_bytes": None,
            "total_disk_space_gb": None,
            "total_disk_space_human": "Unknown",
            "total_used_bytes": None,
            "total_used_gb": None,
            "total_used_human": "Unknown",
            "total_free_bytes": None,
            "total_free_gb": None,
            "total_free_human": "Unknown",
            "disk_percent": None,
            "disk_io": None,
            "mount_points": []
        }


async def get_all_system_info() -> Dict[str, Any]:
    """
    Get all system information (OS, CPU, Memory, Disk, Uptime, Device Model).
    Returns a dictionary containing all system information.
    """
    try:
        loop = asyncio.get_event_loop()
        
        # Run synchronous functions in executor to avoid blocking
        os_info = await loop.run_in_executor(None, get_os_info)
        cpu_info = await loop.run_in_executor(None, get_cpu_info)
        memory_info = await loop.run_in_executor(None, get_memory_info)
        disk_info = await loop.run_in_executor(None, get_disk_info)
        
        return {
            "os": os_info,
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info
        }
    except Exception as e:
        print(f"[installer][system-info] Error getting all system info: {e}")
        return {
            "os": get_os_info(),
            "cpu": get_cpu_info(),
            "memory": get_memory_info(),
            "disk": get_disk_info()
        }


def format_size_gb(size_gb: Optional[float]) -> str:
    """
    Format size in GB to a clean string format.
    Removes unnecessary decimal places (e.g., "16.00 GB" -> "16 GB").
    
    Args:
        size_gb: Size in GB as a float, or None if unknown
        
    Returns:
        Formatted string like "16 GB" or "500.50 GB" or "Unknown"
    """
    if size_gb is None:
        return "Unknown"
    
    # Round to nearest integer if close to whole number, otherwise keep 2 decimals
    if abs(size_gb - round(size_gb)) < 0.01:
        return f"{int(round(size_gb))} GB"
    else:
        return f"{size_gb:.2f} GB"


async def get_formatted_system_info() -> Dict[str, Any]:
    """
    Get system information formatted according to the server schema.
    Returns a dictionary with "action" and "data" keys matching the expected format.
    
    Returns:
        {
            "action": "system_info",
            "data": {
                "os": {
                    "name": "Ubuntu",
                    "version": "22.04",
                    "release": "22.04.3 LTS"
                },
                "cpu": {
                    "cores": 8,
                    "model": "Intel Core i7",
                    "architecture": "x86_64"
                },
                "memory": {
                    "total_ram": "16 GB",
                    "swap": {
                        "total": "4 GB",
                        "used": "0.5 GB",
                        "free": "3.5 GB",
                        "percent": 12.5
                    }
                },
                "disk": {
                    "total_space": "500 GB",
                    "mount_points": [
                        {
                            "path": "/",
                            "total": "500 GB",
                            "available": "200 GB"
                        }
                    ]
                }
            }
        }
    """
    try:
        # Get all system info
        system_info = await get_all_system_info()
        
        # Format OS info
        os_data = {
            "name": system_info.get("os", {}).get("os_name", "Unknown"),
            "version": system_info.get("os", {}).get("os_version", "Unknown"),
            "release": system_info.get("os", {}).get("os_release", "Unknown"),
            "kernel": system_info.get("os", {}).get("os_release", "Unknown")  # Kernel version (same as release on Linux)
        }
        
        # Format CPU info
        cpu_info_raw = system_info.get("cpu", {})
        cpu_data = {
            "cores": cpu_info_raw.get("cpu_cores"),
            "model": cpu_info_raw.get("cpu_model", "Unknown"),
            "architecture": cpu_info_raw.get("cpu_architecture", "Unknown"),
            "usage_percent": round(cpu_info_raw.get("cpu_usage_percent", 0), 2) if cpu_info_raw.get("cpu_usage_percent") is not None else None,
            "load_avg": cpu_info_raw.get("cpu_load_avg"),
            "temperature": cpu_info_raw.get("cpu_temperature")
        }
        
        # Format Memory info - extract GB value and format as string
        memory_info_raw = system_info.get("memory", {})
        memory_gb = memory_info_raw.get("total_ram_gb")
        swap_total_gb = memory_info_raw.get("swap_total_gb", 0)
        swap_used_gb = memory_info_raw.get("swap_used_gb", 0)
        swap_free_gb = memory_info_raw.get("swap_free_gb", 0)
        swap_percent = memory_info_raw.get("swap_percent", 0)
        
        used_ram_gb = memory_info_raw.get("used_ram_gb")
        free_ram_gb = memory_info_raw.get("free_ram_gb")
        ram_percent = memory_info_raw.get("ram_percent", 0)
        
        memory_data = {
            "total_ram": format_size_gb(memory_gb) if memory_gb is not None else "Unknown",
            "used_ram": format_size_gb(used_ram_gb) if used_ram_gb is not None else "Unknown",
            "free_ram": format_size_gb(free_ram_gb) if free_ram_gb is not None else "Unknown",
            "ram_percent": round(ram_percent, 2) if ram_percent is not None else 0,
            "swap": {
                "total": format_size_gb(swap_total_gb) if swap_total_gb > 0 else "0 GB",
                "used": format_size_gb(swap_used_gb) if swap_total_gb > 0 else "0 GB",
                "free": format_size_gb(swap_free_gb) if swap_total_gb > 0 else "0 GB",
                "percent": round(swap_percent, 2) if swap_total_gb > 0 else 0
            }
        }
        
        # Format Disk info
        disk_info_raw = system_info.get("disk", {})
        disk_total_gb = disk_info_raw.get("total_disk_space_gb")
        disk_used_gb = disk_info_raw.get("total_used_gb")
        disk_free_gb = disk_info_raw.get("total_free_gb")
        disk_percent = disk_info_raw.get("disk_percent", 0)
        disk_io_raw = disk_info_raw.get("disk_io")
        
        # Format disk I/O as human-readable strings
        disk_io = None
        if disk_io_raw:
            read_bytes = disk_io_raw.get("read_bytes", 0)
            write_bytes = disk_io_raw.get("write_bytes", 0)
            read_gb = read_bytes / (1024 ** 3)
            write_gb = write_bytes / (1024 ** 3)
            
            disk_io = {
                "read_bytes": format_size_gb(read_gb),
                "write_bytes": format_size_gb(write_gb),
                "read_count": disk_io_raw.get("read_count", 0),
                "write_count": disk_io_raw.get("write_count", 0)
            }
        
        disk_data = {
            "total_space": format_size_gb(disk_total_gb) if disk_total_gb is not None else "Unknown",
            "used_space": format_size_gb(disk_used_gb) if disk_used_gb is not None else "Unknown",
            "free_space": format_size_gb(disk_free_gb) if disk_free_gb is not None else "Unknown",
            "disk_percent": round(disk_percent, 2) if disk_percent is not None else 0,
            "disk_io": disk_io,
            "mount_points": []
        }
        
        # Format mount points - simplify to just path, total, and available
        mount_points_raw = disk_info_raw.get("mount_points", [])
        for mp in mount_points_raw:
            mount_point = {
                "path": mp.get("mountpoint", "Unknown"),
                "total": format_size_gb(mp.get("total_gb")),
                "available": format_size_gb(mp.get("free_gb"))
            }
            disk_data["mount_points"].append(mount_point)
        
        # Return formatted response
        return {
            "action": "system_info",
            "data": {
                "os": os_data,
                "cpu": cpu_data,
                "memory": memory_data,
                "disk": disk_data
            }
        }
    except Exception as e:
        print(f"[installer][system-info] Error formatting system info: {e}")
        # Return minimal error response
        return {
            "action": "system_info",
            "data": {
                "os": {"name": "Unknown", "version": "Unknown", "release": "Unknown"},
                "cpu": {"cores": None, "model": "Unknown", "architecture": "Unknown"},
                "memory": {"total_ram": "Unknown"},
                "disk": {"total_space": "Unknown", "mount_points": []}
            }
        }
