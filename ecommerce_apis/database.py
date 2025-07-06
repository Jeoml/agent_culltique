from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import ssl
from sqlalchemy.ext.asyncio import create_async_engine

ssl_context = ssl.create_default_context()

# Replace with your NeonDB connection string (get it from Neon dashboard)
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_evU75bXRiufQ@ep-calm-forest-a1n2cmuj-pooler.ap-southeast-1.aws.neon.tech/neondb"
# psql 'postgresql://neondb_owner:npg_evU75bXRiufQ@ep-calm-forest-a1n2cmuj-pooler.ap-southeast-1.aws.neon.tech/neondb'
# psql 'postgresql://neondb_owner:npg_rPsfVD15cCIH@ep-lively-sea-a1jy7jdi-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session