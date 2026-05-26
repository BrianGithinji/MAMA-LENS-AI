import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ChevronLeft, AlertTriangle, CheckCircle, Phone,
  Eye, Hand, Fingerprint, Smile, Activity, Droplets,
} from "lucide-react";
import { anemiaAPI } from "../../api/client";

const SITE_ICONS: Record<string, React.ElementType> = {
  conjunctiva: Eye,
  palm: Hand,
  nail: Fingerprint,
  tongue: Smile,
};

const ANEMIA_CONFIG = {
  none: {
    label: "No Anemia Detected",
    color: "bg-secondary-500",
    bg: "bg-secondary-50",
    border: "border-secondary-200",
    text: "text-secondary-700",
    badge: "bg-secondary-100 text-secondary-700",
    bar: "bg-secondary-500",
    emoji: "✅",
  },
  mild: {
    label: "Mild Anemia",
    color: "bg-warm-500",
    bg: "bg-warm-50",
    border: "border-warm-200",
    text: "text-warm-700",
    badge: "bg-warm-100 text-warm-700",
    bar: "bg-warm-500",
    emoji: "⚠️",
  },
  moderate: {
    label: "Moderate Anemia",
    color: "bg-orange-500",
    bg: "bg-orange-50",
    border: "border-orange-200",
    text: "text-orange-700",
    badge: "bg-orange-100 text-orange-700",
    bar: "bg-orange-500",
    emoji: "🔶",
  },
  severe: {
    label: "Severe Anemia",
    color: "bg-emergency-500",
    bg: "bg-emergency-50",
    border: "border-emergency-200",
    text: "text-emergency-700",
    badge: "bg-emergency-100 text-emergency-700",
    bar: "bg-emergency-500",
    emoji: "🚨",
  },
};

// WHO thresholds for pregnant women (g/dL)
const HB_SCALE = { min: 3, max: 18, normal: 11 };

function HbGauge({ hb, level }: { hb: number; level: string }) {
  const config = ANEMIA_CONFIG[level as keyof typeof ANEMIA_CONFIG] ?? ANEMIA_CONFIG.none;
  const pct = ((hb - HB_SCALE.min) / (HB_SCALE.max - HB_SCALE.min)) * 100;
  const normalPct = ((HB_SCALE.normal - HB_SCALE.min) / (HB_SCALE.max - HB_SCALE.min)) * 100;

  return (
    <div className="mt-4">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>3 g/dL (severe)</span>
        <span className="font-bold text-gray-900 text-sm">{hb} g/dL</span>
        <span>18 g/dL (high)</span>
      </div>
      <div className="relative h-4 bg-gray-100 rounded-full overflow-hidden">
        {/* Normal threshold marker */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-secondary-500 z-10"
          style={{ left: `${normalPct}%` }}
        />
        {/* Hb bar */}
        <motion.div
          className={`h-full rounded-full ${config.bar}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-400 mt-1">
        <span />
        <span className="text-secondary-600 font-medium">↑ Normal ≥11 g/dL</span>
        <span />
      </div>
    </div>
  );
}

export default function AnemiaResultPage() {
  const { id } = useParams<{ id: string }>();
  const { data: result, isLoading } = useQuery({
    queryKey: ["anemia", id],
    queryFn: () => anemiaAPI.getDetection(id!).then((r) => r.data),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center animate-pulse">
          <Droplets className="w-8 h-8 text-red-500" />
        </div>
        <p className="text-gray-500 text-sm">Analyzing your images...</p>
      </div>
    );
  }

  if (!result) {
    return <div className="p-6 text-center text-gray-500">Result not found</div>;
  }

  const config = ANEMIA_CONFIG[result.anemia_level as keyof typeof ANEMIA_CONFIG] ?? ANEMIA_CONFIG.none;

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <Link to="/anemia" className="p-2 rounded-xl hover:bg-gray-100">
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <h1 className="font-bold text-gray-900">Anemia Screening Result</h1>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-6 space-y-4">

        {/* Emergency alert */}
        {result.is_emergency && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className="bg-emergency-500 text-white rounded-3xl p-5"
          >
            <div className="flex items-center gap-3 mb-3">
              <AlertTriangle className="w-6 h-6 animate-pulse" />
              <h2 className="font-bold text-lg">Severe Anemia — Emergency</h2>
            </div>
            <p className="text-emergency-100 text-sm mb-4">
              Estimated hemoglobin is critically low. Please seek immediate medical care.
              You may need a blood transfusion.
            </p>
            <a
              href="tel:999"
              className="flex items-center justify-center gap-2 bg-white text-emergency-600 font-bold py-3 rounded-2xl"
            >
              <Phone className="w-4 h-4" /> Call Emergency (999)
            </a>
          </motion.div>
        )}

        {/* Main result card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-3xl p-5 shadow-soft"
        >
          <div className="flex items-center gap-3 mb-1">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${config.bg}`}>
              <Droplets className={`w-6 h-6 ${config.text}`} />
            </div>
            <div>
              <p className="text-gray-500 text-xs font-medium uppercase tracking-wide">Anemia Level</p>
              <div className="flex items-center gap-2">
                <span className="text-xl">{config.emoji}</span>
                <h2 className={`font-bold text-lg ${config.text}`}>{config.label}</h2>
              </div>
            </div>
          </div>

          <HbGauge hb={result.estimated_hemoglobin} level={result.anemia_level} />

          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{result.estimated_hemoglobin}</p>
              <p className="text-gray-500 text-xs">Est. Hb (g/dL)</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{Math.round(result.confidence * 100)}%</p>
              <p className="text-gray-500 text-xs">Confidence</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{result.sites_analyzed?.length ?? 0}</p>
              <p className="text-gray-500 text-xs">Sites analyzed</p>
            </div>
          </div>
        </motion.div>

        {/* Site-by-site breakdown */}
        {result.sites_analyzed?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="bg-white rounded-3xl p-5 shadow-soft"
          >
            <h3 className="font-semibold text-gray-900 mb-4">Site Analysis</h3>
            <div className="space-y-4">
              {result.sites_analyzed.map((site: any) => {
                const Icon = SITE_ICONS[site.site] ?? Activity;
                const pallor = Math.round(site.pallor_score * 100);
                const qualityColor = site.quality === "good"
                  ? "text-secondary-600 bg-secondary-50"
                  : site.quality === "fair"
                  ? "text-warm-600 bg-warm-50"
                  : "text-gray-500 bg-gray-100";
                return (
                  <div key={site.site}>
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 rounded-xl bg-gray-100 flex items-center justify-center">
                        <Icon className="w-4 h-4 text-gray-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-800 text-sm font-medium capitalize">{site.site}</span>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${qualityColor}`}>
                            {site.quality}
                          </span>
                        </div>
                        <p className="text-gray-500 text-xs">
                          Pallor: {pallor}% · RI: {site.redness_index.toFixed(3)}
                        </p>
                      </div>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <motion.div
                        className={`h-full rounded-full ${pallor > 60 ? "bg-emergency-400" : pallor > 35 ? "bg-warm-400" : "bg-secondary-400"}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${pallor}%` }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}

        {/* Risk factors */}
        {result.risk_factors?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="bg-white rounded-3xl p-5 shadow-soft"
          >
            <h3 className="font-semibold text-gray-900 mb-3">Risk Factors</h3>
            <div className="space-y-2">
              {result.risk_factors.map((f: string, i: number) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-orange-50 rounded-2xl">
                  <AlertTriangle className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
                  <p className="text-gray-700 text-sm">{f}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Recommendations */}
        {result.recommendations?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="bg-white rounded-3xl p-5 shadow-soft"
          >
            <h3 className="font-semibold text-gray-900 mb-3">Recommendations</h3>
            <div className="space-y-2">
              {result.recommendations.map((rec: string, i: number) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="w-5 h-5 rounded-full bg-red-100 text-red-600 text-xs flex items-center justify-center flex-shrink-0 font-bold mt-0.5">
                    {i + 1}
                  </span>
                  <p className="text-gray-700 text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Confidence note */}
        {result.confidence < 0.6 && (
          <div className={`${config.bg} ${config.border} border rounded-2xl p-4`}>
            <p className={`${config.text} text-xs`}>
              <strong>Low confidence ({Math.round(result.confidence * 100)}%):</strong> Image quality was limited.
              For best results, capture all 4 sites in bright natural light and confirm with a blood test.
            </p>
          </div>
        )}

        {/* Disclaimer */}
        <div className="bg-calm-50 rounded-2xl p-4">
          <p className="text-calm-700 text-xs text-center">
            This is an AI-based screening tool, not a medical diagnosis.
            Always confirm anemia with a laboratory hemoglobin test.
          </p>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-3 pb-4">
          <Link
            to="/telemedicine"
            className="flex items-center justify-center gap-2 py-4 bg-red-500 text-white font-semibold rounded-2xl text-sm"
          >
            Book Consultation
          </Link>
          <Link
            to="/facilities"
            className="flex items-center justify-center gap-2 py-4 border-2 border-gray-200 text-gray-700 font-semibold rounded-2xl text-sm"
          >
            Find Clinic
          </Link>
        </div>
      </div>
    </div>
  );
}
