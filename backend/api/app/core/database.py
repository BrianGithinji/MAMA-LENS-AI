"""
MAMA-LENS AI — MongoDB Database Layer (Motor async driver)
"""
import structlog
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = structlog.get_logger(__name__)

# ─── Client singleton ────────────────────────────────────────────────────────

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.MONGODB_DB_NAME]


# Convenience alias used throughout the app
def get_db() -> AsyncIOMotorDatabase:
    return get_database()


# ─── Startup / Shutdown ──────────────────────────────────────────────────────

async def init_db():
    """Connect to MongoDB and create indexes."""
    db = get_database()

    # Users
    await db.users.create_index("phone_number", unique=True, sparse=True)
    await db.users.create_index("email", unique=True, sparse=True)
    await db.users.create_index("role")
    await db.users.create_index("status")

    # Pregnancy profiles
    await db.pregnancy_profiles.create_index("user_id")
    await db.pregnancy_profiles.create_index([("user_id", 1), ("is_active", 1)])

    # Risk assessments
    await db.risk_assessments.create_index("user_id")
    await db.risk_assessments.create_index("is_emergency")
    await db.risk_assessments.create_index([("user_id", 1), ("created_at", -1)])

    # Health records & vitals
    await db.health_records.create_index("user_id")
    await db.vital_signs.create_index("user_id")

    # Appointments & consultations
    await db.appointments.create_index("patient_id")
    await db.appointments.create_index("status")
    await db.consultations.create_index("patient_id")

    # Messages
    await db.messages.create_index("user_id")
    await db.messages.create_index("is_emergency")

    # Facilities — 2dsphere for geo queries
    await db.health_facilities.create_index([("location", "2dsphere")], sparse=True)
    await db.health_facilities.create_index("country")
    await db.health_facilities.create_index("is_active")

    # Notifications
    await db.notifications.create_index("user_id")
    await db.notifications.create_index([("user_id", 1), ("is_read", 1)])

    # Wearables
    await db.wearable_devices.create_index("user_id")
    await db.wearable_readings.create_index("user_id")
    await db.wearable_readings.create_index("is_abnormal")

    logger.info("MongoDB indexes created", db=settings.MONGODB_DB_NAME)


async def close_db():
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")
