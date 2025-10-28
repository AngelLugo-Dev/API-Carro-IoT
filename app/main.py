from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from .config import get_settings
from .services.websocket_manager import sio
# Importar handlers para registrar eventos Socket.IO
from .controllers import socket_handlers  # noqa: F401
from .routers import health, devices, movements, events, status, simulate

settings = get_settings()

# Create FastAPI app
api = FastAPI(title=settings.app_name)

# CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api.include_router(health.router)
api.include_router(devices.router)
api.include_router(movements.router)
api.include_router(events.router)
api.include_router(status.router)
api.include_router(simulate.router)

# Mount Socket.IO on top of FastAPI
app = socketio.ASGIApp(sio, other_asgi_app=api)


# Entrypoint for uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info",
    )
