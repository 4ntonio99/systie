from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.bulk_import.adapters.outbound.bulk_repository import BulkRepository

class ImportUsersUseCase:
    @staticmethod
    async def execute(file_content: bytes, db: AsyncSession) -> dict:
        result = await BulkRepository.process_and_insert_txt(file_content, db)
        return result

class ImportAttendanceUseCase:
    @staticmethod
    async def execute(file_content: bytes, db: AsyncSession) -> dict:
        result = await BulkRepository.process_and_insert_attendance_txt(file_content, db)
        return result
    
class ImportHorariosUseCase:
    @staticmethod
    async def execute(file_content: bytes, db: AsyncSession) -> dict:
        return await BulkRepository.process_and_insert_horarios_txt(file_content, db)