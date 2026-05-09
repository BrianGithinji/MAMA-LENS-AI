"""
MAMA-LENS AI — MongoDB Database Layer (Motor async driver)
Handles both mongodb:// and mongodb+srv:// connection strings.
"""
import structlog
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = structlog.get_logger(__name__)

_client: AsyncIOMotorClient | None = None


def _normalise_uri(uri: str) -> str:
    """
    Convert old-style mongodb:// shard URIs to mongodb+srv:// format.
    Render / Atlas works best with SRV — it handles TLS automatically.
    """
    if uri.startswith("mongodb+srv://"):
        return uri  # already correct

    # If it's the old shard-list format, extract credentials and cluster name
    # e.g. mongodb://user:pass@ac-xxx-shard-00-00.yyy.mongodb.net:27017,...
    if "mongodb.net:27017" in uri and "shard-00-00" in uri:
        try:
            # Extract user:pass
            after_scheme = uri.replace("mongodb://", "")
            creds, rest = after_scheme.split("@", 1)
            # Extract cluster base from first shard host
            first_host = rest.split(",")[0]          # ac-xxx-shard-00-00.yyy.mongodb.net:27017
            host_no_port = first_host.split(":")[0]  # ac-xxx-shard-00-00.yyy.mongodb.net
            # Cluster SRV host = remove the shard suffix
            # ac-d88dmls-shard-00-00.e5o71yv.mongodb.net → ac-d88dmls.e5o71yv.mongodb.net
            parts = host_no_port.split(".")
            cluster_part = parts[0]  # ac-d88dmls-shard-00-00
            base_cluster = "-".join(cluster_part.split("-")[:-3])  # ac-d88dmls
            srv_host = f"{base_cluster}.{'.'.join(parts[1:])}"
            srv_uri = f"mongodb+srv://{creds}@{srv_host}/?retryWrites=true&w=majority&appName=MAMA"
            logger.info("Converted to SRV URI", srv_host=srv_host)
            return srv_uri
        except Exception as e:
            logger.warning("URI normalisation failed, using as-is", error=str(e))

    return uri


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        uri = _normalise_uri(settings.MONGODB_URI)
        # mongodb+srv:// handles TLS automatically — no extra flags needed
        _client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
        )
        logger.info("MongoDB client created", uri_scheme=uri.split("://")[0])
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.MONGODB_DB_NAME]


def get_db() -> AsyncIOMotorDatabase:
    return get_database()


async def init_db():
    """Connect to MongoDB and create indexes. Safe to call on every startup."""
    db = get_database()

    async def safe_index(collection, key, **kwargs):
        """Create index, ignore if it already exists with same options."""
        try:
            await collection.create_index(key, **kwargs)
        except Exception as e:
            # Index already exists with different options — skip silently
            logger.warning("Index creation skipped", key=str(key), error=str(e)[:100])

    await safe_index(db.users, "phone_number", unique=True, sparse=True)
    await safe_index(db.users, "email", unique=True, sparse=True)
    await safe_index(db.users, "google_id", unique=True, sparse=True)
    await safe_index(db.users, "role")
    await safe_index(db.users, "status")

    await safe_index(db.pregnancy_profiles, "user_id")
    await safe_index(db.pregnancy_profiles, [("user_id", 1), ("is_active", 1)])

    await safe_index(db.risk_assessments, "user_id")
    await safe_index(db.risk_assessments, "is_emergency")
    await safe_index(db.risk_assessments, [("user_id", 1), ("created_at", -1)])

    await safe_index(db.health_records, "user_id")
    await safe_index(db.vital_signs, "user_id")

    await safe_index(db.appointments, "patient_id")
    await safe_index(db.appointments, "status")
    await safe_index(db.consultations, "patient_id")

    await safe_index(db.messages, "user_id")
    await safe_index(db.messages, "is_emergency")

    await safe_index(db.health_facilities, "country")
    await safe_index(db.health_facilities, "is_active")

    await safe_index(db.notifications, "user_id")
    await safe_index(db.notifications, [("user_id", 1), ("is_read", 1)])

    await safe_index(db.wearable_devices, "user_id")
    await safe_index(db.wearable_readings, "user_id")

    logger.info("MongoDB indexes ready", db=settings.MONGODB_DB_NAME)

    await db.pregnancy_profiles.create_index("user_id")
    await db.pregnancy_profiles.create_index([("user_id", 1), ("is_active", 1)])

    await db.risk_assessments.create_index("user_id")
    await db.risk_assessments.create_index("is_emergency")
    await db.risk_assessments.create_index([("user_id", 1), ("created_at", -1)])

    await db.health_records.create_index("user_id")
    await db.vital_signs.create_index("user_id")

    await db.appointments.create_index("patient_id")
    await db.appointments.create_index("status")
    await db.consultations.create_index("patient_id")

    await db.messages.create_index("user_id")
    await db.messages.create_index("is_emergency")

    await db.health_facilities.create_index("country")
    await db.health_facilities.create_index("is_active")

    await db.notifications.create_index("user_id")
    await db.notifications.create_index([("user_id", 1), ("is_read", 1)])

    await db.wearable_devices.create_index("user_id")
    await db.wearable_readings.create_index("user_id")

    logger.info("MongoDB indexes created", db=settings.MONGODB_DB_NAME)


async def close_db():
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")
