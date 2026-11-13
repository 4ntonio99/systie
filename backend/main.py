import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- 1. Importar el middleware de CORS
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuth2 as OAuth2Model
from fastapi.security import OAuth2
from sqlalchemy.exc import OperationalError
from src.shared.database import engine, Base

# 1. IMPORTANTE: Importa todos tus modelos ORM desde shared para que SQLAlchemy los registre y cree las tablas
from src.shared.models import UserModel, AttendanceModel, HorariosModel

# 2. Después importa tus routers y controladores
from src.modules.auth.adapters.inbound.controllers import router as auth_router
from src.modules.bulk_import.adapters.inbound.controllers import router as bulk_router
from src.modules.tiempo_extra.adapters.inbound.controllers import router as tiempo_extra_router

app = FastAPI(
    title="sysTie API",
    swagger_ui_parameters={"persistAuthorization": True}
)

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "http://abarretov.com"
]

# --- 2. AGREGAR ESTE BLOQUE DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras (Authorization, Content-Type, etc.)
)
# ---------------------------------------

@app.on_event("startup")
async def startup_event():
    max_retries = 5
    retry_delay = 3

    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("¡Base de datos conectada y tablas creadas exitosamente!")
            break
        except (OperationalError, ConnectionRefusedError) as e:
            if attempt == max_retries:
                print("No se pudo conectar a la base de datos después de varios intentos.")
                raise e
            print(f"Intento {attempt}/{max_retries}: Base de datos no disponible aún, reintentando en {retry_delay}s...")
            await asyncio.sleep(retry_delay)

# Registrar las rutas
app.include_router(auth_router)
app.include_router(bulk_router)
app.include_router(tiempo_extra_router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a sysTie"}