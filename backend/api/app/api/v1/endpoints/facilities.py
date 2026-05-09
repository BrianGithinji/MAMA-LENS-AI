"""MAMA-LENS AI — Healthcare Facility Endpoints (MongoDB)"""
import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from app.core.database import get_db

router = APIRouter()


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.get("/nearby")
async def find_nearby(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(default=500),
    has_maternity: bool = False,
    has_emergency: bool = False,
    limit: int = Query(default=20),
):
    db = get_db()
    query: dict = {"is_active": True}
    if has_maternity:
        query["has_maternity_ward"] = True
    if has_emergency:
        query["has_emergency_services"] = True

    cursor = db.health_facilities.find(query)
    facilities = await cursor.to_list(length=500)

    nearby = []
    for f in facilities:
        dist = haversine(latitude, longitude, f["latitude"], f["longitude"])
        if dist <= radius_km:
            nearby.append({
                "id": f["_id"],
                "name": f["name"],
                "facility_type": f["facility_type"],
                "distance_km": round(dist, 2),
                "latitude": f["latitude"],
                "longitude": f["longitude"],
                "address": f.get("address"),
                "phone_numbers": f.get("phone_numbers", []),
                "emergency_phone": f.get("emergency_phone"),
                "has_maternity_ward": f.get("has_maternity_ward", False),
                "has_emergency_services": f.get("has_emergency_services", False),
                "has_ambulance": f.get("has_ambulance", False),
                "is_24_hours": f.get("is_24_hours", False),
                "accepts_nhif": f.get("accepts_nhif", False),
                "offers_telemedicine": f.get("offers_telemedicine", False),
                "average_rating": f.get("average_rating"),
            })

    nearby.sort(key=lambda x: x["distance_km"])
    return nearby[:limit]


@router.get("/emergency-nearest")
async def find_emergency_nearest(
    latitude: float = Query(...),
    longitude: float = Query(...),
):
    db = get_db()
    cursor = db.health_facilities.find({"is_active": True, "has_emergency_services": True})
    facilities = await cursor.to_list(length=200)

    if not facilities:
        return {"message": "No emergency facilities found. Call 999 or 112.", "emergency_numbers": ["999", "112"]}

    nearest = min(facilities, key=lambda f: haversine(latitude, longitude, f["latitude"], f["longitude"]))
    dist = haversine(latitude, longitude, nearest["latitude"], nearest["longitude"])
    phones = nearest.get("phone_numbers", [])
    return {
        "id": nearest["_id"],
        "name": nearest["name"],
        "distance_km": round(dist, 2),
        "phone": nearest.get("emergency_phone") or (phones[0] if phones else None),
        "address": nearest.get("address"),
        "latitude": nearest["latitude"],
        "longitude": nearest["longitude"],
        "has_ambulance": nearest.get("has_ambulance", False),
        "directions_url": f"https://maps.google.com/?q={nearest['latitude']},{nearest['longitude']}",
        "emergency_numbers": ["999", "112"],
    }


@router.get("/{facility_id}")
async def get_facility(facility_id: str):
    db = get_db()
    f = await db.health_facilities.find_one({"_id": facility_id})
    if not f:
        raise HTTPException(status_code=404, detail="Facility not found")
    return {
        "id": f["_id"], "name": f["name"], "facility_type": f["facility_type"],
        "country": f.get("country"), "region": f.get("region"), "district": f.get("district"),
        "address": f.get("address"), "latitude": f["latitude"], "longitude": f["longitude"],
        "phone_numbers": f.get("phone_numbers", []),
        "emergency_phone": f.get("emergency_phone"),
        "services_offered": f.get("services_offered", []),
        "has_maternity_ward": f.get("has_maternity_ward", False),
        "has_emergency_services": f.get("has_emergency_services", False),
        "has_ambulance": f.get("has_ambulance", False),
        "has_ultrasound": f.get("has_ultrasound", False),
        "has_laboratory": f.get("has_laboratory", False),
        "has_pharmacy": f.get("has_pharmacy", False),
        "accepts_nhif": f.get("accepts_nhif", False),
        "is_24_hours": f.get("is_24_hours", False),
        "offers_telemedicine": f.get("offers_telemedicine", False),
        "average_rating": f.get("average_rating"),
        "ownership": f.get("ownership"),
    }
