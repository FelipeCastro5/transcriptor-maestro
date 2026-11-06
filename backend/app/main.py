from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.schemas.response import ResponseDto, ResponseUtil
from app.db.session import init_db
from app.core.scheduler import system_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicio de la aplicación: inicializar base de datos y arrancar Curva de Espacios Iguales
    try:
        init_db()
        system_scheduler.start()
    except Exception as e:
        print(f"[MAIN-STARTUP-ERROR] {e}")
    yield
    # Apagado ordenado
    try:
        system_scheduler.shutdown()
    except Exception as e:
        print(f"[MAIN-SHUTDOWN-ERROR] {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API para el Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuración CORS para conexión con Frontend (React/Vue/Next/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# MANEJADORES DE EXCEPCIONES GLOBALES (Estandarización de Errores con ResponseDto)
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseDto(
            code=exc.status_code,
            message=str(exc.detail),
            data=None
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores = exc.errors()
    primer_error = errores[0]["msg"] if errores else "Error de validación"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ResponseDto(
            code=422,
            message=f"Error de validación: {primer_error}",
            data=errores
        ).model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseDto(
            code=500,
            message=f"Error interno del servidor: {str(exc)}",
            data=None
        ).model_dump()
    )

# ---------------------------------------------------------------------------
# ENDPOINTS GENERALES ESTANDARIZADOS
# ---------------------------------------------------------------------------
@app.get("/health", response_model=ResponseDto[dict], tags=["Salud y Monitoreo"])
async def health_check():
    data = {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG
    }
    return ResponseUtil.success(data=data, message="Servicio operativo")

@app.get("/", response_model=ResponseDto[dict], tags=["General"])
async def root():
    data = {
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "api_v1": settings.API_V1_STR
    }
    return ResponseUtil.success(data=data, message=f"Bienvenido a {settings.PROJECT_NAME}")

# Registrar enrutador v1
app.include_router(api_router, prefix=settings.API_V1_STR)
