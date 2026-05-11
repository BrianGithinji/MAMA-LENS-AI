import { useState } from "react";
import { motion } from "framer-motion";
import { Video, Mic, MessageCircle, ExternalLink, Shield, Globe, Cpu, Heart, ChevronRight, Phone } from "lucide-react";

const MEDILINK_URL = "https://medilinkhealth.co.ke";

const CONSULTATION_TYPES = [
  { icon: Video, label: "Video Consultation", description: "Face-to-face with a doctor via secure video call", color: "bg-calm-100 text-calm-600" },
  { icon: Mic, label: "Voice Consultation", description: "Audio-only call with a healthcare provider", color: "bg-secondary-100 text-secondary-600" },
  { icon: MessageCircle, label: "Chat Consultation", description: "Text-based consultation at your own pace", color: "bg-warm-100 text-warm-600" },
];

const FEATURES = [
  { icon: Globe, title: "Global Provider Network", description: "Connect with doctors and specialists worldwide, anytime" },
  { icon: Shield, title: "HIPAA & GDPR Compliant", description: "Military-grade encryption protects your health data" },
  { icon: Cpu, title: "AI Health Assistants", description: "Meet Lora & Josh — 24/7 AI-powered medical guidance" },
  { icon: Heart, title: "Maternal Specialists", description: "OB/GYN, midwives, and maternal-fetal medicine experts" },
];

const HOW_IT_WORKS = [
  { step: "1", title: "Register on MediLink", desc: "Create your free secure account at medilinkhealth.co.ke" },
  { step: "2", title: "Choose a Provider", desc: "Browse doctors, OB/GYNs, and maternal health specialists" },
  { step: "3", title: "Book & Connect", desc: "Schedule or start an instant secure video consultation" },
  { step: "4", title: "Receive Care", desc: "Get diagnosis, prescriptions, and follow-up from anywhere" },
];

export default function TelemedicinePage() {
  const [launching, setLaunching] = useState(false);

  const openMediLink = () => {
    setLaunching(true);
    window.open(MEDILINK_URL, "_blank", "noopener,noreferrer");
    setTimeout(() => setLaunching(false), 1500);
  };

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-gradient-to-br from-calm-500 to-calm-700 px-6 pt-10 pb-16">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="max-w-lg mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-full mb-4">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Powered by MediLink Health
          </div>
          <h1 className="text-white text-2xl font-bold">Telemedicine</h1>
          <p className="text-calm-100 text-sm mt-2 max-w-xs mx-auto">
            Connect with doctors and maternal health specialists from anywhere — secure, private, and instant.
          </p>
        </motion.div>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-8 space-y-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-3xl shadow-card overflow-hidden">
          <div className="bg-gradient-to-r from-calm-500 to-calm-600 px-5 py-3 flex items-center justify-between">
            <div>
              <p className="text-white font-bold text-sm">MediLink Health</p>
              <p className="text-calm-100 text-xs">medilinkhealth.co.ke</p>
            </div>
            <div className="w-8 h-8 bg-white/20 rounded-xl flex items-center justify-center">
              <Video className="w-4 h-4 text-white" />
            </div>
          </div>

          <div className="p-5">
            <p className="text-gray-600 text-sm mb-4">
              Start a secure consultation with a doctor or maternal health specialist right now.
            </p>
            <div className="space-y-2 mb-4">
              {CONSULTATION_TYPES.map(({ icon: Icon, label, description, color }) => (
                <button key={label} onClick={openMediLink}
                  className="w-full flex items-center gap-4 p-3.5 bg-gray-50 hover:bg-gray-100 rounded-2xl transition-all active:scale-95 text-left">
                  <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-900 text-sm">{label}</p>
                    <p className="text-gray-400 text-xs truncate">{description}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-300 flex-shrink-0" />
                </button>
              ))}
            </div>
            <button onClick={openMediLink} disabled={launching}
              className="w-full flex items-center justify-center gap-2 py-4 bg-calm-500 hover:bg-calm-600 text-white font-bold rounded-2xl transition-all active:scale-95 disabled:opacity-70">
              <ExternalLink className="w-4 h-4" />
              {launching ? "Opening MediLink..." : "Open MediLink Health"}
            </button>
            <p className="text-center text-gray-400 text-xs mt-3">Opens medilinkhealth.co.ke in a new tab</p>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <a href="tel:999" className="flex items-center gap-4 bg-emergency-50 border border-emergency-200 rounded-3xl p-4 active:scale-95 transition-all">
            <div className="w-10 h-10 bg-emergency-100 rounded-2xl flex items-center justify-center flex-shrink-0">
              <Phone className="w-5 h-5 text-emergency-600" />
            </div>
            <div>
              <p className="font-bold text-emergency-800 text-sm">Emergency? Call 999</p>
              <p className="text-emergency-600 text-xs">For life-threatening situations — don't wait</p>
            </div>
          </a>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-white rounded-3xl shadow-card p-5">
          <h2 className="font-bold text-gray-900 mb-4">How It Works</h2>
          <div className="space-y-3">
            {HOW_IT_WORKS.map(({ step, title, desc }) => (
              <div key={step} className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-full bg-calm-100 text-calm-600 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">{step}</div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">{title}</p>
                  <p className="text-gray-500 text-xs mt-0.5">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-white rounded-3xl shadow-card p-5">
          <h2 className="font-bold text-gray-900 mb-4">Why MediLink Health</h2>
          <div className="grid grid-cols-2 gap-3">
            {FEATURES.map(({ icon: Icon, title, description }) => (
              <div key={title} className="bg-calm-50 rounded-2xl p-3">
                <div className="w-8 h-8 bg-calm-100 rounded-xl flex items-center justify-center mb-2">
                  <Icon className="w-4 h-4 text-calm-600" />
                </div>
                <p className="font-semibold text-gray-900 text-xs leading-tight">{title}</p>
                <p className="text-gray-500 text-xs mt-1 leading-tight">{description}</p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="bg-gradient-to-br from-calm-500 to-calm-700 rounded-3xl p-5 text-center">
          <p className="text-white font-bold mb-1">New to MediLink?</p>
          <p className="text-calm-100 text-xs mb-4">Create a free account to access doctors, specialists, and AI health assistants worldwide.</p>
          <button onClick={openMediLink}
            className="w-full py-3 bg-white text-calm-600 font-bold rounded-2xl text-sm active:scale-95 transition-all flex items-center justify-center gap-2">
            <ExternalLink className="w-4 h-4" />
            Register on MediLink Health
          </button>
          <p className="text-calm-200 text-xs mt-2">medilinkhealth.co.ke</p>
        </motion.div>

        <p className="text-center text-gray-400 text-xs pb-2">
          Telemedicine consultations are provided by MediLink Health. MAMA-LENS AI is not responsible for medical advice given during consultations.
        </p>
      </div>
    </div>
  );
}
