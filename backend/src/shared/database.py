from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from src.shared.config import settings

# Asegúrate de que la URL en tus settings comience con 'postgresql+asyncpg://'
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Ponlo en False en producción si no quieres ver las consultas SQL en consola
    future=True
)

# Fábrica de sesiones asíncronas para las transacciones (QUITAMOS class_ = AsyncAttrs)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# Base declarativa para los modelos ORM (Si quieres usar AsyncAttrs para atributos asíncronos, ponlo aquí)
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Dependencia útil para FastAPI (para inyectar sesiones en los adaptadores o casos de uso)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()