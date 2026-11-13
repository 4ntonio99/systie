import io
import re
import polars as pl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from src.shared.models import UserModel, AttendanceModel, HorariosModel

class BulkRepository:
    
    @staticmethod
    async def process_and_insert_txt(file_content: bytes, db: AsyncSession) -> dict:
        """
        Procesa e inserta masivamente los usuarios desde un archivo TXT.
        """
        try:
            df = pl.read_csv(
                io.BytesIO(file_content),
                separator="\t",
                has_header=False,
                new_columns=["nombre", "curp", "rfc", "adsc"],
                infer_schema_length=10000
            )

            # Limpiar espacios en blanco en columnas de texto
            df = df.with_columns(
                pl.col("nombre").str.strip_chars(),
                pl.col("curp").str.strip_chars(),
                pl.col("rfc").str.strip_chars(),
                pl.col("adsc").str.strip_chars()
            )

            records = df.to_dicts()

            if not records:
                return {"inserted": 0, "message": "El archivo está vacío o no tiene el formato correcto."}

            stmt = insert(UserModel).values(records)
            await db.execute(stmt)
            await db.commit()

            return {
                "inserted": len(records),
                "message": f"Se importaron {len(records)} registros de usuarios exitosamente."
            }

        except Exception as e:
            await db.rollback()
            raise RuntimeError(f"Error procesando el archivo masivo de usuarios: {str(e)}")

    @staticmethod
    async def process_and_insert_attendance_txt(file_content: bytes, db: AsyncSession) -> dict:
        """
        Procesa e inserta masivamente las asistencias desde el archivo TXT 
        mapeando correctamente las columnas según el modelo.
        """
        try:
            import re
            records = []
            text_stream = io.TextIOWrapper(io.BytesIO(file_content), encoding="utf-8")
            
            for line in text_stream:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                # Extraer tokens manejando cadenas entrecomilladas y espacios
                partes = re.findall(r'"[^"]*"|\S+', line_stripped)

                if len(partes) < 2:
                    continue

                # Mapeo exacto basado en la posición real de tus datos en el TXT:
                curp = partes[0] if len(partes) > 0 else ""
                fecha = partes[1] if len(partes) > 1 else ""
                horario_e1 = partes[2] if len(partes) > 2 else ""
                reg_e1 = partes[3] if len(partes) > 3 else ""
                edo_e1 = partes[4] if len(partes) > 4 else ""
                
                # Mapeo correcto para las salidas:
                horario_s1 = ""                                     # Se mantiene vacío
                reg_s1 = partes[6] if len(partes) > 6 else ""       # Toma "18:32" (Primera checada de salida real)
                edo_s1 = partes[7] if len(partes) > 7 else ""       # Toma el estado "O"
                reg_s2 = ""                                         # Se mantiene vacío ya que no hay segunda checada

                records.append({
                    "curp": curp.strip('" '),
                    "fecha": fecha.strip('" '),
                    "horario_e1": horario_e1.strip('" '),
                    "reg_e1": reg_e1.strip('" '),
                    "edo_e1": edo_e1.strip('" '),
                    "horario_s1": horario_s1.strip('" '),
                    "reg_s1": reg_s1.strip('" '),
                    "edo_s1": edo_s1.strip('" '),
                    "reg_s2": reg_s2.strip('" ')
                })

            if not records:
                return {"inserted": 0, "message": "El archivo de asistencias está vacío o no tiene el formato correcto."}

            # Inserción por lotes (Batches de 1000)
            batch_size = 1000
            total_inserted = 0

            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                stmt = insert(AttendanceModel).values(batch)
                await db.execute(stmt)
                total_inserted += len(batch)

            await db.commit()

            return {
                "inserted": total_inserted,
                "message": f"Se importaron {total_inserted} registros de asistencia exitosamente por lotes."
            }

        except Exception as e:
            await db.rollback()
            raise RuntimeError(f"Error procesando el archivo masivo de asistencias: {str(e)}")

    @staticmethod
    async def process_and_insert_horarios_txt(file_content: bytes, db: AsyncSession) -> dict:
        try:
            records = []
            text_stream = io.TextIOWrapper(io.BytesIO(file_content), encoding="utf-8")
            
            for line in text_stream:
                parts = line.strip().split('"')
                clean_parts = [p.strip() for p in parts if p and p != " "]
                
                if len(clean_parts) >= 4:
                    curp = clean_parts[0]
                    raw_entrada = clean_parts[2] # Ejemplo: "09000000"
                    raw_salida = clean_parts[3]  # Ejemplo: "00001800"
                    
                    # Transformar formato de entrada ("09000000" -> "09:00")
                    entrada = f"{raw_entrada[0:2]}:{raw_entrada[2:4]}" if len(raw_entrada) >= 4 else raw_entrada
                    
                    # Transformar formato de salida ("00001800" -> "18:00")
                    salida = f"{raw_salida[4:6]}:{raw_salida[6:8]}" if len(raw_salida) >= 8 else raw_salida

                    records.append({
                        "curp": curp,
                        "entrada": entrada,
                        "salida": salida
                    })

            if not records:
                return {"inserted": 0, "message": "El archivo de horarios está vacío o no tiene el formato correcto."}

            # Inserción por lotes optimizada (Batches de 1000)
            batch_size = 1000
            total_inserted = 0

            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                stmt = insert(HorariosModel).values(batch)
                await db.execute(stmt)
                total_inserted += len(batch)

            await db.commit()

            return {
                "inserted": total_inserted,
                "message": f"Se importaron {total_inserted} registros de horarios exitosamente."
            }

        except Exception as e:
            await db.rollback()
            raise RuntimeError(f"Error procesando el archivo masivo de horarios: {str(e)}")