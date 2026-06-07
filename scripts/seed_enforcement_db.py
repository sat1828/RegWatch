"""Seed enforcement action database with SEBI/RBI enforcement data."""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.models.enforcement import EnforcementAction

SEED_DATA = [
    {
        "regulator": "SEBI",
        "entity_name": "Reliance Securities Ltd",
        "action_type": "penalty",
        "penalty_amount": 25000000,
        "regulation_type": "Securities Contracts Regulations",
        "description": "Failed to maintain proper segregation of client securities",
        "action_date": datetime(2025, 6, 15, tzinfo=timezone.utc),
    },
    {
        "regulator": "SEBI",
        "entity_name": "ICICI Securities Ltd",
        "action_type": "penalty",
        "penalty_amount": 15000000,
        "regulation_type": "Stock Broker Regulations",
        "description": "Non-compliance with trade confirmation requirements",
        "action_date": datetime(2025, 4, 10, tzinfo=timezone.utc),
    },
    {
        "regulator": "RBI",
        "entity_name": "HDFC Bank Ltd",
        "action_type": "penalty",
        "penalty_amount": 5000000,
        "regulation_type": "Banking Regulation Act",
        "description": "Deficiencies in KYC/AML compliance framework",
        "action_date": datetime(2025, 8, 22, tzinfo=timezone.utc),
    },
    {
        "regulator": "RBI",
        "entity_name": "Axis Bank Ltd",
        "action_type": "direction",
        "penalty_amount": 0,
        "regulation_type": "Payment and Settlement Systems",
        "description": "Directed to strengthen cybersecurity framework",
        "action_date": datetime(2025, 3, 5, tzinfo=timezone.utc),
    },
    {
        "regulator": "SEBI",
        "entity_name": "Motilal Oswal Financial Services",
        "action_type": "penalty",
        "penalty_amount": 7500000,
        "regulation_type": "Investment Adviser Regulations",
        "description": "Unauthorized portfolio management services",
        "action_date": datetime(2025, 9, 1, tzinfo=timezone.utc),
    },
    {
        "regulator": "SEBI",
        "entity_name": "Angel One Ltd",
        "action_type": "warning",
        "penalty_amount": 0,
        "regulation_type": "Research Analyst Regulations",
        "description": "Inadequate disclosure of conflict of interest",
        "action_date": datetime(2025, 7, 18, tzinfo=timezone.utc),
    },
    {
        "regulator": "RBI",
        "entity_name": "State Bank of India",
        "action_type": "penalty",
        "penalty_amount": 10000000,
        "regulation_type": "Foreign Exchange Management Act",
        "description": "Violation of FEMA reporting requirements",
        "action_date": datetime(2025, 2, 28, tzinfo=timezone.utc),
    },
    {
        "regulator": "SEBI",
        "entity_name": "Zerodha Broking Ltd",
        "action_type": "penalty",
        "penalty_amount": 3000000,
        "regulation_type": "SEBI Broker Regulations 2023",
        "description": "Algorithmic trading compliance failures",
        "action_date": datetime(2025, 10, 12, tzinfo=timezone.utc),
    },
    {
        "regulator": "RBI",
        "entity_name": "Kotak Mahindra Bank",
        "action_type": "restriction",
        "penalty_amount": 0,
        "regulation_type": "Banking Regulation Act",
        "description": "Restricted from onboarding new customers via digital channels",
        "action_date": datetime(2025, 5, 20, tzinfo=timezone.utc),
    },
    {
        "regulator": "SEBI",
        "entity_name": "Aditya Birla Capital Ltd",
        "action_type": "penalty",
        "penalty_amount": 22000000,
        "regulation_type": "Mutual Fund Regulations",
        "description": "Front-running in mutual fund transactions",
        "action_date": datetime(2025, 11, 8, tzinfo=timezone.utc),
    },
]


async def seed() -> None:
    engine = create_async_engine(str(settings.database_url))
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        existing = await session.execute(select(EnforcementAction).limit(1))
        if existing.scalar_one_or_none():
            print("Enforcement data already seeded, skipping.")
            await engine.dispose()
            return

        for record in SEED_DATA:
            action = EnforcementAction(
                id=str(uuid.uuid4()),
                regulator=record["regulator"],
                entity_name=record["entity_name"],
                action_type=record["action_type"],
                penalty_amount=record["penalty_amount"],
                regulation_type=record["regulation_type"],
                description=record["description"],
                action_date=record["action_date"],
                is_active=True,
            )
            session.add(action)

        await session.commit()
        print(f"Seeded {len(SEED_DATA)} enforcement records.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
