import json
from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base


def convert_dates(data):
    for key, value in data.items():
        if isinstance(value, str) and key.endswith("_at"):
            try:
                data[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
    return data


@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")  # , echo=True
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


@pytest.fixture(scope="session")
async def db_session_with_data(db_engine):
    async with db_engine.connect() as conn:
        async with conn.begin():
            Session = sessionmaker(
                bind=conn, class_=AsyncSession, expire_on_commit=False
            )
            async with Session() as session:
                filepath = Path(__file__).parent / "fixtures.json"
                with open(filepath, "r") as f:
                    fixtures = json.load(f)
                    for table, rows in fixtures.items():
                        for mapper in Base.registry.mappers:
                            model = mapper.class_
                            if model.__tablename__ == table:
                                for row in rows:
                                    row = convert_dates(row)
                                    session.add(model(**row))
                                break
                    await session.commit()
    yield session


@pytest.fixture(scope="function")
async def db_session(db_engine, db_session_with_data):
    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        Session = sessionmaker(
            bind=connection, class_=AsyncSession, expire_on_commit=False
        )
        async with Session() as session:
            yield session
            await transaction.rollback()
