from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.database import get_db
from src.modules.bulk_import.application.use_cases import ImportHorariosUseCase, ImportUsersUseCase, ImportAttendanceUseCase

router = APIRouter(prefix="/bulk", tags=["Bulk Import"])

@router.post("/users-txt")
async def upload_users_txt(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    content = await file.read()
    return await ImportUsersUseCase.execute(content, db)

@router.post("/attendance-txt")
async def upload_attendance_txt(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Sube el archivo TXT de asistencias (ej. formato con comillas y espacios).
    """
    content = await file.read()
    return await ImportAttendanceUseCase.execute(content, db)

@router.post("/horarios-txt")
async def upload_horarios_txt(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Sube el archivo TXT de horarios, extrae únicamente CURP, entrada y salida 
    con formato de hora y realiza la carga masiva.
    """
    content = await file.read()
    return await ImportHorariosUseCase.execute(content, db)