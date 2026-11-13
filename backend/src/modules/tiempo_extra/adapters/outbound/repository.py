from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.shared.models import UserModel, AttendanceModel, HorariosModel
from src.modules.tiempo_extra.domain.services import (
    obtener_rango_fechas_quincena,
    parsear_fecha_ddmmaa,
    hora_a_minutos,
    minutos_a_horas_minutos,
    cumple_con_tolerancia
)

class TiempoExtraRepository:

    @staticmethod
    async def obtener_reporte_por_curps(curps: list[str], quincena: int, db: AsyncSession) -> dict:
        if not curps:
            return {
                "success": True,
                "totalCoincidencias": 0,
                "totalRegistrosValidos": 0,
                "totalMinutosExtraGlobal": 0,
                "tiempoExtraGlobalFormateado": "0 hrs 0 min",
                "resultados": []
            }

        fecha_inicio, fecha_fin = obtener_rango_fechas_quincena(quincena)

        # 1. Obtener empleados
        stmt_emp = select(UserModel).where(UserModel.curp.in_(curps))
        res_emp = await db.execute(stmt_emp)
        empleados = res_emp.scalars().all()

        resultados_completos = []
        total_registros_global = 0
        total_minutos_extra_global = 0

        for emp in empleados:
            # 2. Obtener horario oficial del empleado
            stmt_horario = select(HorariosModel).where(HorariosModel.curp == emp.curp)
            res_horario = await db.execute(stmt_horario)
            horario = res_horario.scalars().first()

            entrada_oficial = horario.entrada if horario else "09:00"
            salida_oficial = horario.salida if horario else "18:00"

            # 3. Obtener asistencias
            stmt_asistencia = select(AttendanceModel).where(AttendanceModel.curp == emp.curp)
            res_asistencia = await db.execute(stmt_asistencia)
            asistencias = res_asistencia.scalars().all()

            registros_filtrados = []
            minutos_extra_empleado = 0
            es_horario_especial = (entrada_oficial == "24:00" and salida_oficial == "24:00")
            minutos_salida_oficial = hora_a_minutos(salida_oficial)

            for reg in asistencias:
                fecha_reg = parsear_fecha_ddmmaa(reg.fecha)
                if not fecha_reg or not (fecha_inicio <= fecha_reg <= fecha_fin):
                    continue

                minutos_extra_dia = 0

                if es_horario_especial:
                    # Lógica para turno especial 24:00
                    horas_en_reg = [
                        v for v in [reg.reg_e1, reg.reg_s1, reg.reg_s2]
                        if v and ":" in v and len(v) >= 5
                    ]
                    if len(horas_en_reg) >= 2:
                        min_s1 = hora_a_minutos(horas_en_reg[-2])
                        min_s2 = hora_a_minutos(horas_en_reg[-1])
                        if min_s1 is not None and min_s2 is not None and min_s2 > min_s1:
                            minutos_extra_dia = (min_s2 - min_s1)
                else:
                    # Lógica normal con tolerancias (Calculando exclusivamente la salida)
                    if cumple_con_tolerancia(
                        reg.reg_e1, reg.reg_s1, reg.reg_s2,
                        entrada_oficial, salida_oficial, fecha_reg
                    ):
                        es_fin_de_semana = fecha_reg.weekday() in (5, 6)
                        if es_fin_de_semana:
                            min_e = hora_a_minutos(reg.reg_e1)
                            salida_str = reg.reg_s2 if (reg.reg_s2 and reg.reg_s2.strip()) else reg.reg_s1
                            min_s = hora_a_minutos(salida_str)
                            if min_e is not None and min_s is not None and min_s > min_e:
                                minutos_extra_dia = (min_s - min_e)
                        else:
                            # Se removió la evaluación de entrada anticipada; solo se evalúa la salida
                            if minutos_salida_oficial is not None:
                                min_s1 = hora_a_minutos(reg.reg_s1) if reg.reg_s1 else None
                                min_s2 = hora_a_minutos(reg.reg_s2) if reg.reg_s2 else None
                                umbral_salida = minutos_salida_oficial + 30

                                if min_s1 is not None and min_s1 >= umbral_salida:
                                    minutos_extra_dia += (min_s1 - minutos_salida_oficial)
                                elif min_s2 is not None and min_s2 >= umbral_salida:
                                    minutos_extra_dia += (min_s2 - minutos_salida_oficial)

                if minutos_extra_dia > 0:
                    registros_filtrados.append({
                        "fecha": reg.fecha,
                        "reg_e1": reg.reg_e1,
                        "reg_s1": reg.reg_s1,
                        "reg_s2": reg.reg_s2,
                        "duracion_minutos": minutos_extra_dia,
                        "duracion_formateada": minutos_a_horas_minutos(minutos_extra_dia)
                    })
                    total_registros_global += 1
                    minutos_extra_empleado += minutos_extra_dia

            if registros_filtrados:
                total_minutos_extra_global += minutos_extra_empleado
                resultados_completos.append({
                    "empleado": {
                        "curp": emp.curp,
                        "nombre": emp.nombre,
                        "rfc": emp.rfc,
                        "adsc": emp.adsc,
                        "entrada": entrada_oficial,
                        "salida": salida_oficial
                    },
                    "totalRegistrosValidos": len(registros_filtrados),
                    "totalMinutosExtra": minutos_extra_empleado,
                    "tiempoExtraFormateado": minutos_a_horas_minutos(minutos_extra_empleado),
                    "registros": registros_filtrados
                })

        return {
            "success": True,
            "totalCoincidencias": len(resultados_completos),
            "totalRegistrosValidos": total_registros_global,
            "totalMinutosExtraGlobal": total_minutos_extra_global,
            "tiempoExtraGlobalFormateado": minutos_a_horas_minutos(total_minutos_extra_global),
            "resultados": resultados_completos
        }