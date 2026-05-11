import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { MapPin, Phone, AlertTriangle, SlidersHorizontal } from "lucide-react";
import { facilitiesAPI } from "../../api/client";

const RADIUS_OPTIONS = [50, 100, 200, 500, 1000];

export default function FacilitiesMapPage() {
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locationError, setLocationError] = useState(false);
  const [radiusKm, setRadiusKm] = useState(500);
  const [showRadiusPicker, setShowRadiusPicker] = useState(false);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (pos) => setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {
        setLocationError(true);
        setUserLocation({ lat: -1.2921, lng: 36.8219 });
      },
      { timeout: 8000 }
    );
  }, []);

  const { data: facilities, isLoading } = useQuery({
    queryKey: ["facilities", userLocation, radiusKm],
    queryFn: () =>
      facilitiesAPI
        .findNearby(userLocation!.lat, userLocation!.lng, { radius_km: radiusKm })
        .then((r) => r.data),
    enabled: !!userLocation,
  });

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-bold text-gray-900 text-lg">Find Nearby Clinics</h1>
              {locationError && (
                <p className="text-warm-600 text-xs mt-0.5">Showing results near Nairobi</p>
              )}
            </div>
            <button
              onClick={() => setShowRadiusPicker((v) => !v)}
              className="flex items-center gap-1.5 bg-primary-50 text-primary-600 text-xs font-semibold px-3 py-2 rounded-2xl"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              {radiusKm} km
            </button>
          </div>

          {showRadiusPicker && (
            <div className="mt-3 bg-gray-50 rounded-2xl p-3">
              <p className="text-gray-500 text-xs mb-2 font-medium">Search radius</p>
              <div className="flex gap-2 flex-wrap">
                {RADIUS_OPTIONS.map((r) => (
                  <button
                    key={r}
                    onClick={() => { setRadiusKm(r); setShowRadiusPicker(false); }}
                    className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
                      radiusKm === r ? "bg-primary-500 text-white" : "bg-white text-gray-600 border border-gray-200"
                    }`}
                  >
                    {r} km
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-4 space-y-3">
        <a href="tel:999" className="flex items-center gap-3 bg-emergency-500 text-white rounded-3xl p-4 active:scale-95 transition-all">
          <AlertTriangle className="w-5 h-5 animate-pulse" />
          <div>
            <p className="font-bold">Emergency? Call 999</p>
            <p className="text-emergency-100 text-xs">For life-threatening situations</p>
          </div>
        </a>

        {isLoading && (
          <div className="text-center py-10 text-gray-500">
            <p className="text-sm">Searching within {radiusKm} km...</p>
          </div>
        )}

        {!isLoading && facilities?.map((facility: any) => (
          <div key={facility.id} className="bg-white rounded-3xl shadow-card p-5">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="font-bold text-gray-900 text-sm leading-tight">{facility.name}</h3>
                <p className="text-gray-500 text-xs mt-0.5 capitalize">
                  {facility.facility_type.replace(/_/g, " ")}
                </p>
              </div>
              <div className="flex items-center gap-1 text-warm-500 text-xs font-semibold flex-shrink-0">
                <MapPin className="w-3 h-3" />
                {facility.distance_km} km
              </div>
            </div>

            <div className="flex flex-wrap gap-1.5 mt-3">
              {facility.has_maternity_ward && <span className="text-xs bg-secondary-100 text-secondary-700 px-2 py-0.5 rounded-full">Maternity</span>}
              {facility.has_emergency_services && <span className="text-xs bg-emergency-100 text-emergency-700 px-2 py-0.5 rounded-full">Emergency</span>}
              {facility.is_24_hours && <span className="text-xs bg-calm-100 text-calm-700 px-2 py-0.5 rounded-full">24 Hours</span>}
              {facility.accepts_nhif && <span className="text-xs bg-warm-100 text-warm-700 px-2 py-0.5 rounded-full">NHIF</span>}
              {facility.offers_telemedicine && <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">Telemedicine</span>}
            </div>

            {facility.phone_numbers?.[0] && (
              <a href={`tel:${facility.phone_numbers[0]}`} className="flex items-center gap-2 mt-3 text-primary-500 text-sm font-medium">
                <Phone className="w-4 h-4" />
                {facility.phone_numbers[0]}
              </a>
            )}

            <a
              href={`https://maps.google.com/?q=${facility.latitude},${facility.longitude}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 mt-3 py-2.5 border border-primary-200 text-primary-600 rounded-2xl text-sm font-medium active:scale-95 transition-all"
            >
              <MapPin className="w-4 h-4" /> Get Directions
            </a>
          </div>
        ))}

        {!isLoading && facilities?.length === 0 && (
          <div className="text-center py-10">
            <MapPin className="w-10 h-10 mx-auto mb-3 text-gray-200" />
            <p className="text-gray-600 font-medium text-sm">No facilities found within {radiusKm} km</p>
            <p className="text-gray-400 text-xs mt-1 mb-4">Try a larger search radius</p>
            <div className="flex gap-2 justify-center flex-wrap">
              {RADIUS_OPTIONS.filter((r) => r > radiusKm).map((r) => (
                <button key={r} onClick={() => setRadiusKm(r)}
                  className="px-4 py-2 bg-primary-500 text-white rounded-2xl text-sm font-semibold active:scale-95 transition-all">
                  Try {r} km
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
