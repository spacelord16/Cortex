import psutil
import json
from datetime import datetime
from langchain_core.tools import tool

@tool
def get_system_stats():
    """Get current system statistics: CPU, RAM, Disk, and Battery."""
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    battery = psutil.sensors_battery()
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_free_gb": round(disk.free / (1024**3), 2),
    }
    
    if battery:
        stats["battery_percent"] = round(battery.percent, 1)
        stats["battery_plugged"] = battery.power_plugged
        if battery.secsleft and battery.secsleft > 0: 
             stats["battery_time_left_min"] = int(battery.secsleft / 60)
    
    return json.dumps(stats, indent=2)

@tool
def get_process_list(limit: int = 5):
    """Get the top N processes by memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
    # Sort by memory usage
    sorted_procs = sorted(processes, key=lambda p: p['memory_percent'] or 0, reverse=True)
    return json.dumps(sorted_procs[:limit], indent=2)
