"""
MAMA-LENS AI — Seed Healthcare Facilities
Seeds the database with real Kenyan healthcare facilities for demonstration
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend/api"))

SAMPLE_FACILITIES = [
    {
        "name": "Kenyatta National Hospital",
        "facility_type": "referral_hospital",
        "country": "Kenya",
        "region": "Nairobi",
        "district": "Nairobi Central",
        "address": "Hospital Road, Upper Hill, Nairobi",
        "latitude": -1.3006,
        "longitude": 36.8073,
        "phone_numbers": ["+254 20 272 6300"],
        "emergency_phone": "+254 20 272 6300",
        "has_maternity_ward": True,
        "has_emergency_services": True,
        "has_ambulance": True,
        "has_blood_bank": True,
        "has_ultrasound": True,
        "has_laboratory": True,
        "has_pharmacy": True,
        "accepts_nhif": True,
        "is_24_hours": True,
        "ownership": "public",
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "family_planning", "hiv_testing", "emergency"],
    },
    {
        "name": "Pumwani Maternity Hospital",
        "facility_type": "maternity_home",
        "country": "Kenya",
        "region": "Nairobi",
        "district": "Eastlands",
        "address": "Pumwani Road, Nairobi",
        "latitude": -1.2833,
        "longitude": 36.8500,
        "phone_numbers": ["+254 20 222 4000"],
        "emergency_phone": "+254 20 222 4000",
        "has_maternity_ward": True,
        "has_emergency_services": True,
        "has_ambulance": False,
        "has_blood_bank": True,
        "has_ultrasound": True,
        "has_laboratory": True,
        "has_pharmacy": True,
        "accepts_nhif": True,
        "is_24_hours": True,
        "ownership": "public",
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "family_planning"],
    },
    {
        "name": "Aga Khan University Hospital",
        "facility_type": "hospital",
        "country": "Kenya",
        "region": "Nairobi",
        "district": "Parklands",
        "address": "3rd Parklands Avenue, Nairobi",
        "latitude": -1.2641,
        "longitude": 36.8167,
        "phone_numbers": ["+254 20 366 2000"],
        "emergency_phone": "+254 20 366 2000",
        "has_maternity_ward": True,
        "has_emergency_services": True,
        "has_ambulance": True,
        "has_blood_bank": True,
        "has_ultrasound": True,
        "has_laboratory": True,
        "has_pharmacy": True,
        "accepts_nhif": False,
        "is_24_hours": True,
        "ownership": "private",
        "offers_telemedicine": True,
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "family_planning", "specialist_care"],
    },
    {
        "name": "Mombasa County Referral Hospital",
        "facility_type": "referral_hospital",
        "country": "Kenya",
        "region": "Coast",
        "district": "Mombasa",
        "address": "Moi Avenue, Mombasa",
        "latitude": -4.0435,
        "longitude": 39.6682,
        "phone_numbers": ["+254 41 231 1211"],
        "emergency_phone": "+254 41 231 1211",
        "has_maternity_ward": True,
        "has_emergency_services": True,
        "has_ambulance": True,
        "has_blood_bank": True,
        "has_ultrasound": True,
        "has_laboratory": True,
        "has_pharmacy": True,
        "accepts_nhif": True,
        "is_24_hours": True,
        "ownership": "public",
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "emergency"],
    },
    {
        "name": "Kisumu County Referral Hospital",
        "facility_type": "referral_hospital",
        "country": "Kenya",
        "region": "Nyanza",
        "district": "Kisumu",
        "address": "Kisumu-Kakamega Road, Kisumu",
        "latitude": -0.1022,
        "longitude": 34.7617,
        "phone_numbers": ["+254 57 202 2471"],
        "emergency_phone": "+254 57 202 2471",
        "has_maternity_ward": True,
        "has_emergency_services": True,
        "has_ambulance": True,
        "has_blood_bank": True,
        "has_ultrasound": True,
        "has_laboratory": True,
        "has_pharmacy": True,
        "accepts_nhif": True,
        "is_24_hours": True,
        "ownership": "public",
        "services_offered": ["antenatal_care", "delivery", "postnatal_care", "hiv_testing", "emergency"],
    },
]


async def seed_facilities():
    """Seed healthcare facilities into the database."""
    from app.core.database import AsyncSessionLocal
    from app.models.facility import HealthFacility, FacilityType

    async with AsyncSessionLocal() as session:
        for facility_data in SAMPLE_FACILITIES:
            facility = HealthFacility(
                name=facility_data["name"],
                facility_type=FacilityType(facility_data["facility_type"]),
                country=facility_data["country"],
                region=facility_data.get("region"),
                district=facility_data.get("district"),
                address=facility_data.get("address"),
                latitude=facility_data["latitude"],
                longitude=facility_data["longitude"],
                phone_numbers=facility_data.get("phone_numbers"),
                emergency_phone=facility_data.get("emergency_phone"),
                has_maternity_ward=facility_data.get("has_maternity_ward", False),
                has_emergency_services=facility_data.get("has_emergency_services", False),
                has_ambulance=facility_data.get("has_ambulance", False),
                has_blood_bank=facility_data.get("has_blood_bank", False),
                has_ultrasound=facility_data.get("has_ultrasound", False),
                has_laboratory=facility_data.get("has_laboratory", False),
                has_pharmacy=facility_data.get("has_pharmacy", False),
                accepts_nhif=facility_data.get("accepts_nhif", False),
                is_24_hours=facility_data.get("is_24_hours", False),
                ownership=facility_data.get("ownership"),
                offers_telemedicine=facility_data.get("offers_telemedicine", False),
                services_offered=facility_data.get("services_offered"),
                is_active=True,
            )
            session.add(facility)

        await session.commit()
        print(f"✅ Seeded {len(SAMPLE_FACILITIES)} healthcare facilities")


if __name__ == "__main__":
    asyncio.run(seed_facilities())
