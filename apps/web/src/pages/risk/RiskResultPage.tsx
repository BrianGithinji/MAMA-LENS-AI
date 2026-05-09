/**
 * MAMA-LENS AI — Risk Assessment Result Page
 */
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle, ChevronLeft, Phone } from "lucide-react";
import { riskAPI } from "../../api/client";
import RiskLevelBadge from "../../components/ui/RiskLevelBadge";

export default function RiskResultPage() {
  const { id } = useParams<{ id: string }>();
  const { data: assessment, isLoading } = useQuery({
    queryKey: ["risk", id],
    queryFn: () => riskAPI.getAssessment(id!).then((r) => r.data),
    enabled: !!id,
  });

  if (isLoading) return <div className="flex items-center justify-center min-h-screen"><div className="animate-spin text-4xl">⟳</div></div>;
  if (!assessment) return <div className="p-6 text-center text-gray-500">Assessment not found</div>;

  const riskScores = [
    { label: "Preeclampsia", score: assessment.preeclampsia_risk_score, color: "bg-orange-400" },
    { label: "Anemia", score: assessment.anemia_risk_score, color: "bg-red-400" },
    { label: "Gestational Diabetes", score: assessment.gestational_diabetes_risk_score, color: "bg-yellow-400" },
    { label: "Miscarriage", score: assessment.miscarriage_risk_score, color: "bg-pink-400" },
    { label: "Preterm Birth", score: assessment.preterm_birth_risk_score, color: "bg-purple-400" },
  ];

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <Link to="/risk-assessment" className="p-2 rounded-xl hover:bg-gray-100">
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <h1 className="font-bold text-gray-900">Assessment Results</h1>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-6 space-y-4">
        {/* Emergency Alert */}
        {assessment.is_emergency && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className="bg-emergency-500 text-white rounded-3xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <AlertTriangle className="w-6 h-6 animate-pulse" />
              <h2 className="font-bold text-lg">Emergency Detected</h2>
            </div>
            <p className="text-emergency-100 text-sm mb-4">
              {assessment.emergency_type?.replace(/_/g, " ")} — Please seek immediate medical care.
            </p>
            <a href="tel:999" className="flex items-center justify-center gap-2 bg-white text-emergency-600 font-bold py-3 rounded-2xl">
              <Phone className="w-4 h-4" /> Call Emergency (999)
            </a>
          </motion.div>
        )}

        {/* Overall Risk */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
          <p className="text-gray-500 text-xs font-medium uppercase tracking-wide mb-2">Overall Risk Level</p>
          <RiskLevelBadge level={assessment.overall_risk_level} large />
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Risk Score</span>
              <span>{Math.round(assessment.overall_risk_score * 100)}%</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all ${
                assessment.overall_risk_level === "emergency" ? "bg-emergency-500" :
                assessment.overall_risk_level === "high" ? "bg-orange-500" :
                assessment.overall_risk_level === "moderate" ? "bg-warm-500" : "bg-secondary-500"
              }`} style={{ width: `${assessment.overall_risk_score * 100}%` }} />
            </div>
          </div>
        </motion.div>

        {/* Condition Scores */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Condition Risk Scores</h3>
          <div className="space-y-3">
            {riskScores.map(({ label, score, color }) => (
              <div key={label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-700">{label}</span>
                  <span className="font-medium text-gray-900">{Math.round(score * 100)}%</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div className={`h-full ${color} rounded-full`} style={{ width: `${score * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Risk Factors */}
        {assessment.risk_factors?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Risk Factors</h3>
            <div className="space-y-2">
              {assessment.risk_factors.map((factor: any, i: number) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-orange-50 rounded-2xl">
                  <AlertTriangle className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
                  <p className="text-gray-700 text-sm">{factor.description}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Protective Factors */}
        {assessment.protective_factors?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Protective Factors</h3>
            <div className="space-y-2">
              {assessment.protective_factors.map((factor: string, i: number) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-secondary-50 rounded-2xl">
                  <CheckCircle className="w-4 h-4 text-secondary-500 flex-shrink-0 mt-0.5" />
                  <p className="text-gray-700 text-sm">{factor}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Recommendations */}
        {assessment.recommendations?.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card">
            <h3 className="font-semibold text-gray-900 mb-3">Recommendations</h3>
            <div className="space-y-2">
              {assessment.recommendations.map((rec: string, i: number) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="w-5 h-5 rounded-full bg-primary-100 text-primary-600 text-xs flex items-center justify-center flex-shrink-0 font-bold mt-0.5">{i + 1}</span>
                  <p className="text-gray-700 text-sm">{rec}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Disclaimer */}
        <div className="bg-calm-50 rounded-2xl p-4">
          <p className="text-calm-700 text-xs text-center">
            This assessment is AI-generated guidance, not a medical diagnosis. Always consult a qualified healthcare professional.
          </p>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-3 pb-4">
          <Link to="/telemedicine" className="flex items-center justify-center gap-2 py-4 bg-primary-500 text-white font-semibold rounded-2xl text-sm">
            Book Consultation
          </Link>
          <Link to="/facilities" className="flex items-center justify-center gap-2 py-4 border-2 border-gray-200 text-gray-700 font-semibold rounded-2xl text-sm">
            Find Clinic
          </Link>
        </div>
      </div>
    </div>
  );
}
