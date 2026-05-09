/**
 * MAMA-LENS AI — Emergency Page
 * Quick access to emergency resources and danger sign information
 */
import { Phone, MapPin, AlertTriangle } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

const DANGER_SIGNS = [
  { sign: "Heavy vaginal bleeding", sw: "Kutoka damu nyingi ukeni", urgent: true },
  { sign: "Severe headache + vision changes", sw: "Maumivu makali ya kichwa + mabadiliko ya maono", urgent: true },
  { sign: "Baby not moving (after 28 weeks)", sw: "Mtoto hasogei (baada ya wiki 28)", urgent: true },
  { sign: "Seizures or fits", sw: "Degedege", urgent: true },
  { sign: "Severe abdominal pain", sw: "Maumivu makali ya tumbo", urgent: true },
  { sign: "Difficulty breathing", sw: "Ugumu wa kupumua", urgent: true },
  { sign: "High fever", sw: "Homa kali", urgent: false },
  { sign: "Severe swelling of face/hands", sw: "Uvimbe mkubwa wa uso/mikono", urgent: false },
];

export default function EmergencyPage() {
  return (
    <div className="min-h-screen bg-emergency-50 pb-20">
      {/* Header */}
      <div className="bg-emergency-500 px-4 pt-8 pb-12">
        <div className="max-w-lg mx-auto text-center">
          <AlertTriangle className="w-12 h-12 text-white mx-auto mb-3 animate-pulse" />
          <h1 className="text-white text-2xl font-bold">Emergency Help</h1>
          <p className="text-emergency-100 text-sm mt-1">If you are in danger, call immediately</p>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-6 space-y-4">
        {/* Emergency Call Buttons */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-3xl shadow-card p-5">
          <h2 className="font-bold text-gray-900 mb-4">Emergency Numbers</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              { number: "999", label: "Emergency Services" },
              { number: "112", label: "International Emergency" },
              { number: "0800 720 999", label: "Kenya Health Hotline" },
              { number: "+254 722 178 177", label: "Mental Health Crisis" },
            ].map(({ number, label }) => (
              <a key={number} href={`tel:${number.replace(/\s/g, "")}`}
                className="flex flex-col items-center gap-1 bg-emergency-50 border border-emergency-200 rounded-2xl p-3 active:scale-95 transition-all">
                <Phone className="w-5 h-5 text-emergency-500" />
                <span className="font-bold text-emergency-700 text-sm">{number}</span>
                <span className="text-gray-500 text-xs text-center">{label}</span>
              </a>
            ))}
          </div>
        </motion.div>

        {/* Find Nearest Emergency Facility */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Link to="/facilities?emergency=true"
            className="flex items-center gap-4 bg-white rounded-3xl shadow-card p-5 active:scale-95 transition-all">
            <div className="w-12 h-12 bg-calm-100 rounded-2xl flex items-center justify-center flex-shrink-0">
              <MapPin className="w-6 h-6 text-calm-600" />
            </div>
            <div>
              <p className="font-bold text-gray-900">Find Nearest Emergency Facility</p>
              <p className="text-gray-500 text-sm">Get directions to the closest hospital</p>
            </div>
          </Link>
        </motion.div>

        {/* Danger Signs */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-white rounded-3xl shadow-card p-5">
          <h2 className="font-bold text-gray-900 mb-4">⚠️ Pregnancy Danger Signs</h2>
          <p className="text-gray-500 text-sm mb-4">Go to hospital IMMEDIATELY if you have any of these:</p>
          <div className="space-y-2">
            {DANGER_SIGNS.map(({ sign, sw, urgent }) => (
              <div key={sign} className={`flex items-start gap-3 p-3 rounded-2xl ${urgent ? "bg-emergency-50" : "bg-warm-50"}`}>
                <span className={`text-sm flex-shrink-0 ${urgent ? "text-emergency-500" : "text-warm-500"}`}>
                  {urgent ? "🚨" : "⚠️"}
                </span>
                <div>
                  <p className="text-gray-800 text-sm font-medium">{sign}</p>
                  <p className="text-gray-500 text-xs">{sw}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Birth Preparedness */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="bg-secondary-50 border border-secondary-200 rounded-3xl p-5">
          <h3 className="font-bold text-secondary-800 mb-2">Birth Preparedness Checklist</h3>
          <ul className="space-y-1 text-secondary-700 text-sm">
            {[
              "Know your nearest health facility",
              "Have transport arranged in advance",
              "Save emergency contact numbers",
              "Prepare your birth bag",
              "Have money saved for birth costs",
              "Identify a birth companion",
            ].map((item) => (
              <li key={item} className="flex items-center gap-2">
                <span className="text-secondary-500">✓</span> {item}
              </li>
            ))}
          </ul>
        </motion.div>
      </div>
    </div>
  );
}
