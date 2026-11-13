# src/modules/auth/ports/inbound/login_use_case_port.py (o application)
from fastapi import HTTPException, status
from src.modules.auth.ports.outbound.user_repository_port import UserRepositoryPort
from src.shared.security import create_access_token

class LoginUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    async def execute(self, curp: str, rfc: str) -> dict:
        # 1. Buscar usuario por CURP
        user = await self.user_repository.get_by_curp(curp)

        # 2. Validar existencia y que el RFC coincida como contraseña
        if not user or user.rfc != rfc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="CURP o RFC incorrectos"
            )

        # 3. Crear el token JWT (guardamos el curp como identificador 'sub')
        access_token = create_access_token(data={"sub": user.curp, "nivel": user.nivel})

        # 4. Respuesta con el token y datos del usuario
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "curp": user.curp,
                "nivel": user.nivel,
                "adsc": user.adsc
            }
        }