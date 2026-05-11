import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ExternalLink } from "lucide-react";

export default function ConsultationRoomPage() {
  const navigate = useNavigate();

  useEffect(() => {
    window.open("https://medilinkhealth.co.ke", "_blank", "noopener,noreferrer");
    navigate("/telemedicine", { replace: true });
  }, [navigate]);

  return (
    <div className="min-h-screen bg-calm-50 flex items-center justify-center px-6">
      <div className="text-center">
        <div className="w-16 h-16 bg-calm-100 rounded-3xl flex items-center justify-center mx-auto mb-4">
          <ExternalLink className="w-8 h-8 text-calm-600" />
        </div>
        <p className="font-bold text-gray-900 text-lg">Opening MediLink Health...</p>
        <p className="text-gray-500 text-sm mt-2">Your consultation is launching in a new tab.</p>
      </div>
    </div>
  );
}
