from datetime import datetime, date

def hora_a_minutos(hora_str: str) -> int | None:
    if not hora_str or ":" not in hora_str:
        return None
    try:
        partes = hora_str.split(":")
        horas, minutos = int(partes[0]), int(partes[1])
        return (horas * 60) + minutos
    except ValueError:
        return None

def minutos_a_horas_minutos(minutos: int) -> str:
    """
    Convierte un total de minutos a formato 'HH:MM' (ejemplo: 381 mins -> '06:21').
    """
    if not minutos or minutos <= 0:
        return "00:00"
        
    horas = minutos // 60
    mins_restantes = minutos % 60
    
    # :02d asegura que si las horas o minutos son de 1 dígito, se les agregue un '0' a la izquierda
    return f"{horas:02d}:{mins_restantes:02d}"

def parsear_fecha_ddmmaa(fecha_str: str) -> date | None:
    try:
        partes = fecha_str.split("/")
        if len(partes) != 3:
            return None
        dia = int(partes[0])
        mes = int(partes[1])
        anio = int(partes[2])
        if anio < 100:
            anio += 2000
        return date(anio, mes, dia)
    except Exception:
        return None

def obtener_rango_fechas_quincena(quincena: int, anio: int = 2026) -> tuple[date, date]:
    mes_index = (quincena - 1) // 2 + 1
    es_segunda_quincena = (quincena % 2 == 0)

    if es_segunda_quincena:
        dia_inicio = 16
        if mes_index == 12:
            dia_fin = 31
        else:
            siguiente_mes = datetime(anio, mes_index + 1, 1)
            dia_fin = (siguiente_mes - datetime(anio, mes_index, 16)).days + 15
    else:
        dia_inicio = 1
        dia_fin = 15

    fecha_inicio = date(anio, mes_index, dia_inicio)
    fecha_fin = date(anio, mes_index, dia_fin)
    return fecha_inicio, fecha_fin

def cumple_con_tolerancia(
    reg_e1: str | None,
    reg_s1: str | None,
    reg_s2: str | None,
    entrada_oficial_str: str | None,
    salida_oficial_str: str | None,
    fecha_reg: date
) -> bool:
    dia_semana = fecha_reg.weekday()  # 5 = Sábado, 6 = Domingo
    es_fin_de_semana = dia_semana in (5, 6)

    if es_fin_de_semana:
        tiene_entrada = bool(reg_e1 and reg_e1.strip())
        tiene_salida = bool((reg_s1 and reg_s1.strip()) or (reg_s2 and reg_s2.strip()))
        return tiene_entrada and tiene_salida

    if not entrada_oficial_str or not salida_oficial_str:
        return False

    minutos_entrada_oficial = hora_a_minutos(entrada_oficial_str)
    minutos_salida_oficial = hora_a_minutos(salida_oficial_str)

    cumple_entrada = False
    cumple_salida = False

    if minutos_entrada_oficial is not None and reg_e1:
        minutos_reg_e1 = hora_a_minutos(reg_e1)
        if minutos_reg_e1 is not None and minutos_reg_e1 <= (minutos_entrada_oficial - 30):
            cumple_entrada = True

    if not (reg_s1 and reg_s1.strip()) and not (reg_s2 and reg_s2.strip()):
        return False

    if minutos_salida_oficial is not None:
        minutos_reg_s1 = hora_a_minutos(reg_s1) if reg_s1 else None
        minutos_reg_s2 = hora_a_minutos(reg_s2) if reg_s2 else None
        umbral_salida = minutos_salida_oficial + 30

        if (minutos_reg_s1 is not None and minutos_reg_s1 >= umbral_salida) or \
           (minutos_reg_s2 is not None and minutos_reg_s2 >= umbral_salida):
            cumple_salida = True

    return cumple_entrada or cumple_salida