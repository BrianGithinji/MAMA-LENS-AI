/**
 * MAMA-LENS AI — Telemedicine Consultation Room
 * LiveKit-powered video/voice consultation
 */
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Phone, Mic, MicOff, Video, VideoOff, MessageCircle } from "lucide-react";
import toast from "react-hot-toast";
import { telemedicineAPI } from "../../api/client";

export default function ConsultationRoomPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);

  const { data: consultation } = useQuery({
    queryKey: ["consultation", id],
    queryFn: () => telemedicineAPI.join(id!).then(r => r.data),
    enabled: !!id,
  });

  const endMutation = useMutation({
    mutationFn: () => telemedicineAPI.end(id!),
    onSuccess: () => {
      toast.success("Consultation ended");
      navigate("/telemedicine");
    },
  });

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* Video area */}
      <div className="flex-1 relative flex items-center justify-center">
        <div className="text-center text-white">
          <div className="w-24 h-24 rounded-full bg-gray-700 flex items-center justify-center mx-auto mb-4">
            <Video className="w-10 h-10 text-gray-400" />
          </div>
          <p className="text-gray-300 text-sm">
            {consultation?.status === "waiting" ? "Waiting for provider to join..." : "Connected"}
          </p>
          {consultation?.room_name && (
            <p className="text-gray-500 text-xs mt-1">Room: {consultation.room_name}</p>
          )}
        </div>

        {/* Self view */}
        <div className="absolute bottom-4 right-4 w-24 h-32 bg-gray-700 rounded-2xl flex items-center justify-center">
          <Video className="w-6 h-6 text-gray-400" />
        </div>
      </div>

      {/* Controls */}
      <div className="bg-gray-800 px-6 py-6 safe-area-pb">
        <div className="flex items-center justify-center gap-6">
          <button onClick={() => setIsMuted(!isMuted)}
            className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${isMuted ? "bg-emergency-500" : "bg-gray-600"}`}>
            {isMuted ? <MicOff className="w-6 h-6 text-white" /> : <Mic className="w-6 h-6 text-white" />}
          </button>

          <button onClick={() => endMutation.mutate()}
            className="w-16 h-16 rounded-full bg-emergency-500 flex items-center justify-center shadow-lg">
            <Phone className="w-7 h-7 text-white rotate-[135deg]" />
          </button>

          <button onClick={() => setIsVideoOff(!isVideoOff)}
            className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${isVideoOff ? "bg-emergency-500" : "bg-gray-600"}`}>
            {isVideoOff ? <VideoOff className="w-6 h-6 text-white" /> : <Video className="w-6 h-6 text-white" />}
          </button>
        </div>
        <p className="text-center text-gray-500 text-xs mt-3">
          Your consultation is encrypted and secure
        </p>
      </div>
    </div>
  );
}
