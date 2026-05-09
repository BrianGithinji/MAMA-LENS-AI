"""MAMA-LENS AI — MongoDB Seeder"""
import uuid
from app.core.database import get_db

FACILITIES = [
    {
        "_id": str(uuid.uuid4()),
        "name": "Kenyatta National Hospital",
        "facility_type": "referral_hospital",
        "country": "Kenya", "region": "Nairobi", "district": "Nairobi Central",
        "address": "Hospital Road, Upper Hill, Nairobi",
        "latitude": -1.3006, "longitude": 36.8073,
        "phone_numbers": ["+254 20 272 6300"],
        "emergency_phone": "+254 20 272 6300",
        "has_maternity_ward": True, "has_emergency_services": True,
        "has_ambulance": True, "has_blood_bank": True, "has_ultrasound": True,
        "has_laboratory": True, "has_pharmacy": True, "accepts_nhif": True,
        "is_24_hours": True, "ownership": "public", "is_active": True,
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "emergency"],
    },
    {
        "_id": str(uuid.uuid4()),
        "name": "Pumwani Maternity Hospital",
        "facility_type": "maternity_home",
        "country": "Kenya", "region": "Nairobi", "district": "Eastlands",
        "address": "Pumwani Road, Nairobi",
        "latitude": -1.2833, "longitude": 36.8500,
        "phone_numbers": ["+254 20 222 4000"],
        "emergency_phone": "+254 20 222 4000",
        "has_maternity_ward": True, "has_emergency_services": True,
        "has_ambulance": False, "has_blood_bank": True, "has_ultrasound": True,
        "has_laboratory": True, "has_pharmacy": True, "accepts_nhif": True,
        "is_24_hours": True, "ownership": "public", "is_active": True,
        "services_offered": ["antenatal_care", "delivery", "postnatal_care"],
    },
    {
        "_id": str(uuid.uuid4()),
        "name": "Aga Khan University Hospital",
        "facility_type": "hospital",
        "country": "Kenya", "region": "Nairobi", "district": "Parklands",
        "address": "3rd Parklands Avenue, Nairobi",
        "latitude": -1.2641, "longitude": 36.8167,
        "phone_numbers": ["+254 20 366 2000"],
        "emergency_phone": "+254 20 366 2000",
        "has_maternity_ward": True, "has_emergency_services": True,
        "has_ambulance": True, "has_blood_bank": True, "has_ultrasound": True,
        "has_laboratory": True, "has_pharmacy": True, "accepts_nhif": False,
        "is_24_hours": True, "ownership": "private", "is_active": True,
        "offers_telemedicine": True,
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "specialist_care"],
    },
    {
        "_id": str(uuid.uuid4()),
        "name": "Mombasa County Referral Hospital",
        "facility_type": "referral_hospital",
        "country": "Kenya", "region": "Coast", "district": "Mombasa",
        "address": "Moi Avenue, Mombasa",
        "latitude": -4.0435, "longitude": 39.6682,
        "phone_numbers": ["+254 41 231 1211"],
        "emergency_phone": "+254 41 231 1211",
        "has_maternity_ward": True, "has_emergency_services": True,
        "has_ambulance": True, "has_blood_bank": True, "has_ultrasound": True,
        "has_laboratory": True, "has_pharmacy": True, "accepts_nhif": True,
        "is_24_hours": True, "ownership": "public", "is_active": True,
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "emergency"],
    },
    {
        "_id": str(uuid.uuid4()),
        "name": "Kisumu County Referral Hospital",
        "facility_type": "referral_hospital",
        "country": "Kenya", "region": "Nyanza", "district": "Kisumu",
        "address": "Kisumu-Kakamega Road, Kisumu",
        "latitude": -0.1022, "longitude": 34.7617,
        "phone_numbers": ["+254 57 202 2471"],
        "emergency_phone": "+254 57 202 2471",
        "has_maternity_ward": True, "has_emergency_services": True,
        "has_ambulance": True, "has_blood_bank": True, "has_ultrasound": True,
        "has_laboratory": True, "has_pharmacy": True, "accepts_nhif": True,
        "is_24_hours": True, "ownership": "public", "is_active": True,
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "hiv_testing"],
    },
]


async def seed_if_empty():
    """Seed facilities only if the collection is empty."""
    db = get_db()
    count = await db.health_facilities.count_documents({})
    if count > 0:
        return
    await db.health_facilities.insert_many(FACILITIES)
    print(f"✅ Seeded {len(FACILITIES)} healthcare facilities into MongoDB")
