"""Seed regulatory sources for monitoring."""
import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.regulatory_source import RegulatorySource

SOURCES = [
    {
        "name": "SEBI Circulars",
        "url": "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?dogl=circulars",
        "source_type": "html_index",
        "jurisdiction": "IN",
        "regulator": "SEBI",
    },
    {
        "name": "RBI Master Directions",
        "url": "https://www.rbi.org.in/Scripts/BS_ViewMasterDirections.aspx",
        "source_type": "html_index",
        "jurisdiction": "IN",
        "regulator": "RBI",
    },
    {
        "name": "RBI Notifications",
        "url": "https://www.rbi.org.in/Scripts/BS_ViewNotifications.aspx",
        "source_type": "html_index",
        "jurisdiction": "IN",
        "regulator": "RBI",
    },
    {
        "name": "IRDAI Circulars",
        "url": "https://www.irdai.gov.in/ADMINCMS/cms/Circulars.aspx",
        "source_type": "html_index",
        "jurisdiction": "IN",
        "regulator": "IRDAI",
    },
    {
        "name": "MCA Notifications",
        "url": "https://www.mca.gov.in/content/mca/global/en/notifications.html",
        "source_type": "html_index",
        "jurisdiction": "IN",
        "regulator": "MCA",
    },
    {
        "name": "SEBI Enforcement Orders (Sample PDF)",
        "url": "https://www.sebi.gov.in/enforcement.html",
        "source_type": "html_index",
        "jurisdiction": "IN",
        "regulator": "SEBI",
    },
]


async def seed() -> None:
    engine = create_async_engine(str(settings.database_url))
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        from sqlalchemy import select

        existing = await session.execute(select(RegulatorySource).limit(1))
        if existing.scalar_one_or_none():
            print("Sources already seeded, skipping.")
            await engine.dispose()
            return

        for source_data in SOURCES:
            source = RegulatorySource(
                id=str(uuid.uuid4()),
                name=source_data["name"],
                url=source_data["url"],
                source_type=source_data["source_type"],
                jurisdiction=source_data["jurisdiction"],
                regulator=source_data["regulator"],
                is_active=True,
            )
            session.add(source)

        await session.commit()
        print(f"Seeded {len(SOURCES)} regulatory sources.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
