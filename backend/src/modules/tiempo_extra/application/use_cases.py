from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.shared.models import UserModel
from src.modules.tiempo_extra.adapters.outbound.repository import TiempoExtraRepository


class ConsultarTiempoExtraUsuarioUseCase:
    @staticmethod
    async def execute(curp_usuario: str, quincena: int, db: AsyncSession) -> dict:
        return await TiempoExtraRepository.obtener_reporte_por_curps([curp_usuario], quincena, db)

class ConsultarTiempoExtraEncargadoUseCase:
    @staticmethod
    async def execute(adsc_encargado: str, quincena: int, db: AsyncSession) -> dict:
        # Obtener las CURPs de todos los empleados pertenecientes a la misma adscripción
        stmt = select(UserModel.curp).where(UserModel.adsc == adsc_encargado)
        res = await db.execute(stmt)
        curps_area = list(res.scalars().all())

        return await TiempoExtraRepository.obtener_reporte_por_curps(curps_area, quincena, db)

from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.tiempo_extra.application.use_cases import ConsultarTiempoExtraEncargadoUseCase
from datetime import datetime

class ExportarTiempoExtraTxtUseCase:
    @staticmethod
    async def execute(adsc_encargado: str, quincena: int, db: AsyncSession) -> str:
        reporte = await ConsultarTiempoExtraEncargadoUseCase.execute(adsc_encargado, quincena, db)
        
        # Diccionario para traducir el día de la semana a español
        dias_semana = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo"
        }
        
        lineas = []
        for resultado in reporte.get("resultados", []):
            emp = resultado["empleado"]
            curp_completa = emp.get("curp", "")
            curp_reducida = curp_completa[:10]
            adsc = emp.get("adsc", "")
            h_salida = emp.get("salida", "")
            
            for reg in resultado.get("registros", []):
                fecha_str = reg.get("fecha", "")
                reg_s1 = reg.get("reg_s1") or "null"
                reg_s2 = reg.get("reg_s2") or "null"
                
                # Calculamos el formato HH:MM de la duración de este registro específico
                mins = reg.get("duracion_minutos", 0)
                horas = mins // 60
                m_rest = mins % 60
                duracion_hhmm = f"{horas:02d}:{m_rest:02d}"
                
                # Obtener el día de la semana a partir de la fecha
                dia_semana_str = ""
                try:
                    parts = fecha_str.split("/")
                    if len(parts) == 3:
                        dia, mes, anio = parts
                        if len(anio) == 2:
                            anio = f"20{anio}"
                        dt = datetime(int(anio), int(mes), int(dia))
                        dia_semana_str = dias_semana.get(dt.weekday(), "")
                except Exception:
                    dia_semana_str = ""
                
                linea = f"{curp_reducida} | {adsc} | {fecha_str} | {dia_semana_str} | {h_salida} | {reg_s1} | {reg_s2} | {duracion_hhmm}"
                lineas.append(linea)
                
        return "\n".join(lineas)