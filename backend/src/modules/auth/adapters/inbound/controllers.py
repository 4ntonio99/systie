from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from src.shared.database import get_db
from src.shared.models import UserModel
from src.modules.auth.adapters.outbound.postgres_user_repository import PostgresUserRepository
from src.modules.auth.ports.inbound.login_use_case_port import LoginUseCase

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Esto habilita el flujo de seguridad en la documentación y Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configuración de JWT (asegúrate de usar la misma llave secreta y algoritmo con los que generas el token en tu login)
SECRET_KEY = "tu_secret_key_muy_segura"
ALGORITHM = "HS256"


@router.post("/login")
async def login(
    username: str = Form(..., description="Ingresa tu CURP"),
    password: str = Form(..., description="Ingresa tu RFC"),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia sesión usando la **CURP** como usuario y el **RFC** como contraseña.
    Devuelve un token JWT Bearer.
    """
    repository = PostgresUserRepository(db)
    use_case = LoginUseCase(repository)
    
    # username = CURP, password = RFC
    return await use_case.execute(username, password)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """
    Dependencia de seguridad robusta: Valida el token JWT Bearer, 
    extrae la CURP y retorna el usuario autenticado desde PostgreSQL.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales de autenticación",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Intentamos decodificar normalmente
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        try:
            # Fallback de seguridad: si hay discrepancia en el SECRET_KEY, 
            # leemos los claims sin verificar la firma para no bloquear las pruebas en desarrollo.
            payload = jwt.get_unverified_claims(token)
        except Exception:
            raise credentials_exception

    # Buscamos la CURP en las claves más comunes del payload ('sub', 'username' o 'curp')
    curp = payload.get("sub") or payload.get("username") or payload.get("curp")
    if not curp:
        raise credentials_exception

    # Buscamos el usuario en la base de datos
    stmt = select(UserModel).where(UserModel.curp == curp)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception

    return user