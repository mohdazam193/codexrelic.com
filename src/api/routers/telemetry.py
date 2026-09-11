import psutil
import time
import os
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.core.logger import logger

router = APIRouter(prefix="/api/ws")

@router.websocket("/stats")
async def websocket_vm_stats(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            days, rem = divmod(uptime_seconds, 86400)
            hours, rem = divmod(rem, 3600)
            minutes, seconds = divmod(rem, 60)
            uptime_str = f"{int(days)} days, {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
            tasks_total = len(psutil.pids())
            tasks_running = sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_RUNNING)
            
            try:
                load_avg = os.getloadavg()
            except AttributeError:
                load_avg = (0.0, 0.0, 0.0)

            stats = {
                "cpu": cpu_per_core,
                "memory": {
                    "used": mem.used,
                    "total": mem.total,
                    "percent": mem.percent
                },
                "swap": {
                    "used": swap.used,
                    "total": swap.total,
                    "percent": swap.percent
                },
                "uptime": uptime_str,
                "tasks": {
                    "total": tasks_total,
                    "running": tasks_running
                },
                "load": load_avg
            }
            await websocket.send_json(stats)
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from VM stats stream.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
