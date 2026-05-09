/**
 * MAMA-LENS AI — Telemedicine Page
 */
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Video, Mic, MessageCircle } from "lucide-react";
import toast from "react-hot-toast";
import { telemedicineAPI } from "../../api/client";

export default function TelemedicinePage() {
  const navigate = useNavigate();

  const startMutation = useMutation({
    mutationFn: (type: string) => telemedicineAPI.start({ consultation_type: type }),
    onSuccess: (response) => {
      navigate(`/telemedicine/room/${response.data.consultation_id}`);
    },
    onError: () => toast.error("Could not start consultation. Please try again."),
  });

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-gradient-to-br from-calm-500 to-calm-700 px-6 pt-10 pb-16 text-center">
        <h1 className="text-white text-2xl font-bold">Telemedicine</h1>
        <p className="text-calm-100 text-sm mt-1">Connect with a healthcare provider from anywhere</p>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-8 space-y-4">
        <div className="bg-white rounded-3xl shadow-card p-5">
          <h2 className="font-bold text-gray-900 mb-4">Start a Consultation</h2>
          <div className="space-y-3">
            {[
              { type: "video", icon: Video, label: "Video Consultation", desc: "Face-to-face with your provider", color: "bg-calm-100 text-calm-600" },
              { type: "voice", icon: Mic, label: "Voice Consultation", desc: "Audio call only", color: "bg-secondary-100 text-secondary-600" },
              { type: "chat", icon: MessageCircle, label: "Chat Consultation", desc: "Text-based consultation", color: "bg-warm-100 text-warm-600" },
            ].map(({ type, icon: Icon, label, desc, color }) => (
              <button key={type} onClick={() => startMutation.mutate(type)}
                disabled={startMutation.isPending}
                className="w-full flex items-center gap-4 p-4 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-all active:scale-95 disabled:opacity-60">
                <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="text-left">
                  <p className="font-semibold text-gray-900 text-sm">{label}</p>
                  <p className="text-gray-500 text-xs">{desc}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-calm-50 border border-calm-200 rounded-3xl p-5">
          <h3 className="font-bold text-calm-800 mb-2">How it works</h3>
          <ol className="space-y-2 text-calm-700 text-sm">
            {["Choose your consultation type", "Wait for a healthcare provider to join", "Discuss your health concerns", "Receive guidance and prescriptions"].map((step, i) => (
              <li key={i} className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-calm-200 text-calm-700 text-xs flex items-center justify-center font-bold flex-shrink-0">{i + 1}</span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  );
}
