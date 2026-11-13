from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.modules.auth.ports.outbound.user_repository_port import UserRepositoryPort
from src.shared.models import UserModel

class PostgresUserRepository(UserRepositoryPort):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_curp(self, curp: str) -> Optional[UserModel]:
        result = await self.db.execute(select(UserModel).where(UserModel.curp == curp))
        return result.scalars().first()