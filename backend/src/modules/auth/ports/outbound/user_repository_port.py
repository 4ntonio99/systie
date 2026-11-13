from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.modules.auth.adapters.outbound.models import UserModel

class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_by_curp(self, curp: str) -> Optional["UserModel"]:
        pass