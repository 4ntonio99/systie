from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.database import get_db
from src.modules.auth.adapters.inbound.controllers import get_current_user
from src.shared.models import UserModel
from src.modules.tiempo_extra.application.use_cases import ExportarTiempoExtraTxtUseCase
from fastapi import APIRouter, Depends, Query, HTTPException, status, Response
from src.modules.tiempo_extra.application.use_cases import (
    ConsultarTiempoExtraUsuarioUseCase,
    ConsultarTiempoExtraEncargadoUseCase,
    ExportarTiempoExtraTxtUseCase
)

router = APIRouter(prefix="/tiempo-extra", tags=["Tiempo Extra"])

@router.get("/mi-reporte")
async def consultar_mi_tiempo_extra(
    quincena: int = Query(..., ge=1, le=24, description="Número de quincena (1 a 24)"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para Usuario: Permite consultar únicamente su propia información de tiempo extra.
    """
    return await ConsultarTiempoExtraUsuarioUseCase.execute(
        curp_usuario=current_user.curp,
        quincena=quincena,
        db=db
    )

@router.get("/reporte-area")
async def consultar_tiempo_extra_area(
    quincena: int = Query(..., ge=1, le=24, description="Número de quincena (1 a 24)"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para Encargado: Permite consultar el tiempo extra de todos los empleados de su área.
    """
    if current_user.nivel not in ["encargado", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para consultar información del área."
        )

    return await ConsultarTiempoExtraEncargadoUseCase.execute(
        adsc_encargado=current_user.adsc,
        quincena=quincena,
        db=db
    )

@router.get("/reporte-area-txt")
async def exportar_tiempo_extra_area_txt(
    quincena: int = Query(..., ge=1, le=24, description="Número de quincena (1 a 24)"),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint para Encargado: Genera y descarga un archivo .txt con el reporte de tiempo extra 
    de todos los miembros del área, listo para copiar y pegar en Excel.
    """
    if current_user.nivel not in ["encargado", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para exportar la información del área."
        )

    # Obtenemos el contenido en texto plano desde el caso de uso
    contenido_txt = await ExportarTiempoExtraTxtUseCase.execute(
        adsc_encargado=current_user.adsc,
        quincena=quincena,
        db=db
    )
    
    # Definimos el nombre del archivo dinámicamente según la quincena
    nombre_archivo = f"reporte_tiempo_extra_quincena_{quincena}.txt"

    # Retornamos una respuesta HTTP configurada específicamente para forzar la descarga del archivo
    return Response(
        content=contenido_txt,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={nombre_archivo}"
        }
    )