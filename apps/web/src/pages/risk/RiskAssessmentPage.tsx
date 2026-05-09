/**
 * MAMA-LENS AI — Risk Assessment Form
 * Multi-step maternal health risk assessment
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { ChevronRight, ChevronLeft, Activity, Heart, Baby, Leaf } from "lucide-react";
import { riskAPI } from "../../api/client";

const riskSchema = z.object({
  // Step 1: Basic info
  age: z.number().min(10).max(60),
  gestational_age_weeks: z.number().min(1).max(42),
  weight_kg: z.number().min(30).max(200),
  height_cm: z.number().min(100).max(220),

  // Step 2: Vitals
  systolic_bp: z.number().min(60).max(250),
  diastolic_bp: z.number().min(40).max(150),
  heart_rate: z.number().min(40).max(200),
  blood_glucose: z.number().min(40).max(500),
  hemoglobin: z.number().min(3).max(20),

  // Step 3: History
  previous_miscarriages: z.number().min(0).max(20).default(0),
  previous_preeclampsia: z.boolean().default(false),
  previous_gestational_diabetes: z.boolean().default(false),
  previous_preterm_birth: z.boolean().default(false),
  is_multiple_pregnancy: z.boolean().default(false),

  // Step 4: Lifestyle
  smoking: z.boolean().default(false),
  alcohol_use: z.boolean().default(false),
  stress_level: z.number().min(1).max(10).default(5),
  nutrition_status: z.enum(["poor", "fair", "good", "excellent"]).default("fair"),

  // Step 5: Symptoms
  reported_symptoms: z.array(z.string()).default([]),
  pre_existing_conditions: z.array(z.string()).default([]),
});

type RiskFormData = z.infer<typeof riskSchema>;

const STEPS = [
  { id: 1, title: "Basic Information", icon: Baby, description: "Your age and pregnancy details" },
  { id: 2, title: "Vital Signs", icon: Activity, description: "Blood pressure, glucose, and more" },
  { id: 3, title: "Medical History", icon: Heart, description: "Previous pregnancies and conditions" },
  { id: 4, title: "Lifestyle", icon: Leaf, description: "Diet, stress, and habits" },
  { id: 5, title: "Symptoms", icon: Activity, description: "Current symptoms you're experiencing" },
];

const COMMON_SYMPTOMS = [
  "headache", "vision_changes", "swelling_hands", "swelling_face",
  "abdominal_pain", "bleeding", "spotting", "nausea", "vomiting",
  "fever", "difficulty_breathing", "chest_pain", "no_fetal_movement",
  "contractions", "back_pain", "fatigue", "dizziness",
];

const COMMON_CONDITIONS = [
  "hypertension", "diabetes", "anemia", "malaria", "hiv",
  "sickle_cell", "thyroid_disorder", "kidney_disease", "heart_disease",
];

export default function RiskAssessmentPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [selectedConditions, setSelectedConditions] = useState<string[]>([]);

  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm<RiskFormData>({
    resolver: zodResolver(riskSchema),
    defaultValues: {
      stress_level: 5,
      nutrition_status: "fair",
      previous_miscarriages: 0,
    },
  });

  const assessMutation = useMutation({
    mutationFn: (data: RiskFormData) => riskAPI.assess({
      ...data,
      reported_symptoms: selectedSymptoms,
      pre_existing_conditions: selectedConditions,
    }),
    onSuccess: (response) => {
      const { assessment_id, is_emergency } = response.data;
      if (is_emergency) {
        toast.error("⚠️ Emergency detected! Please seek immediate medical care.", { duration: 8000 });
      } else {
        toast.success("Assessment complete!");
      }
      navigate(`/risk-assessment/result/${assessment_id}`);
    },
    onError: () => {
      toast.error("Assessment failed. Please try again.");
    },
  });

  const toggleSymptom = (symptom: string) => {
    setSelectedSymptoms((prev) =>
      prev.includes(symptom) ? prev.filter((s) => s !== symptom) : [...prev, symptom]
    );
  };

  const toggleCondition = (condition: string) => {
    setSelectedConditions((prev) =>
      prev.includes(condition) ? prev.filter((c) => c !== condition) : [...prev, condition]
    );
  };

  const onSubmit = (data: RiskFormData) => {
    assessMutation.mutate(data);
  };

  const progress = (currentStep / STEPS.length) * 100;

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto">
          <div className="flex items-center gap-3 mb-3">
            <button onClick={() => currentStep > 1 ? setCurrentStep(s => s - 1) : navigate(-1)}
              className="p-2 rounded-xl hover:bg-gray-100">
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex-1">
              <h1 className="font-bold text-gray-900 text-base">Risk Assessment</h1>
              <p className="text-gray-500 text-xs">Step {currentStep} of {STEPS.length}</p>
            </div>
          </div>
          {/* Progress bar */}
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary-400 to-primary-600 rounded-full"
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="max-w-lg mx-auto px-4 pt-6">
        <AnimatePresence mode="wait">
          {/* Step 1: Basic Info */}
          {currentStep === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <StepHeader step={STEPS[0]} />
              <div className="space-y-4 mt-6">
                <FormField label="Your Age" error={errors.age?.message}>
                  <input type="number" {...register("age", { valueAsNumber: true })}
                    className="form-input" placeholder="e.g. 28" />
                </FormField>
                <FormField label="Weeks Pregnant" error={errors.gestational_age_weeks?.message}>
                  <input type="number" {...register("gestational_age_weeks", { valueAsNumber: true })}
                    className="form-input" placeholder="e.g. 24" />
                </FormField>
                <div className="grid grid-cols-2 gap-3">
                  <FormField label="Weight (kg)" error={errors.weight_kg?.message}>
                    <input type="number" step="0.1" {...register("weight_kg", { valueAsNumber: true })}
                      className="form-input" placeholder="e.g. 65" />
                  </FormField>
                  <FormField label="Height (cm)" error={errors.height_cm?.message}>
                    <input type="number" {...register("height_cm", { valueAsNumber: true })}
                      className="form-input" placeholder="e.g. 162" />
                  </FormField>
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 2: Vitals */}
          {currentStep === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <StepHeader step={STEPS[1]} />
              <div className="bg-calm-50 border border-calm-200 rounded-2xl p-4 mt-4 mb-6">
                <p className="text-calm-700 text-sm">
                  💡 If you don't have these readings, visit your nearest clinic or community health worker.
                </p>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <FormField label="Systolic BP (mmHg)" error={errors.systolic_bp?.message}>
                    <input type="number" {...register("systolic_bp", { valueAsNumber: true })}
                      className="form-input" placeholder="e.g. 120" />
                  </FormField>
                  <FormField label="Diastolic BP (mmHg)" error={errors.diastolic_bp?.message}>
                    <input type="number" {...register("diastolic_bp", { valueAsNumber: true })}
                      className="form-input" placeholder="e.g. 80" />
                  </FormField>
                </div>
                <FormField label="Heart Rate (bpm)" error={errors.heart_rate?.message}>
                  <input type="number" {...register("heart_rate", { valueAsNumber: true })}
                    className="form-input" placeholder="e.g. 80" />
                </FormField>
                <FormField label="Fasting Blood Glucose (mg/dL)" error={errors.blood_glucose?.message}>
                  <input type="number" {...register("blood_glucose", { valueAsNumber: true })}
                    className="form-input" placeholder="e.g. 88" />
                </FormField>
                <FormField label="Hemoglobin (g/dL)" error={errors.hemoglobin?.message}>
                  <input type="number" step="0.1" {...register("hemoglobin", { valueAsNumber: true })}
                    className="form-input" placeholder="e.g. 11.5" />
                </FormField>
              </div>
            </motion.div>
          )}

          {/* Step 3: History */}
          {currentStep === 3 && (
            <motion.div key="step3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <StepHeader step={STEPS[2]} />
              <div className="space-y-4 mt-6">
                <FormField label="Previous Miscarriages" error={errors.previous_miscarriages?.message}>
                  <input type="number" {...register("previous_miscarriages", { valueAsNumber: true })}
                    className="form-input" placeholder="0" />
                </FormField>
                <div className="space-y-3">
                  {[
                    { key: "previous_preeclampsia", label: "Previous preeclampsia (high BP in pregnancy)" },
                    { key: "previous_gestational_diabetes", label: "Previous gestational diabetes" },
                    { key: "previous_preterm_birth", label: "Previous preterm birth (before 37 weeks)" },
                    { key: "is_multiple_pregnancy", label: "Current multiple pregnancy (twins/triplets)" },
                  ].map(({ key, label }) => (
                    <label key={key} className="flex items-center gap-3 bg-white rounded-2xl p-4 cursor-pointer border border-gray-100">
                      <input type="checkbox" {...register(key as keyof RiskFormData)}
                        className="w-5 h-5 rounded-lg text-primary-500" />
                      <span className="text-gray-700 text-sm">{label}</span>
                    </label>
                  ))}
                </div>
                <div>
                  <p className="text-gray-700 text-sm font-medium mb-2">Pre-existing conditions</p>
                  <div className="flex flex-wrap gap-2">
                    {COMMON_CONDITIONS.map((condition) => (
                      <button key={condition} type="button"
                        onClick={() => toggleCondition(condition)}
                        className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                          selectedConditions.includes(condition)
                            ? "bg-primary-500 text-white"
                            : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                        }`}>
                        {condition.replace(/_/g, " ")}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 4: Lifestyle */}
          {currentStep === 4 && (
            <motion.div key="step4" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <StepHeader step={STEPS[3]} />
              <div className="space-y-4 mt-6">
                <div className="space-y-3">
                  {[
                    { key: "smoking", label: "I smoke cigarettes" },
                    { key: "alcohol_use", label: "I drink alcohol" },
                  ].map(({ key, label }) => (
                    <label key={key} className="flex items-center gap-3 bg-white rounded-2xl p-4 cursor-pointer border border-gray-100">
                      <input type="checkbox" {...register(key as keyof RiskFormData)}
                        className="w-5 h-5 rounded-lg text-primary-500" />
                      <span className="text-gray-700 text-sm">{label}</span>
                    </label>
                  ))}
                </div>
                <FormField label={`Stress Level: ${watch("stress_level") || 5}/10`}>
                  <input type="range" min="1" max="10" {...register("stress_level", { valueAsNumber: true })}
                    className="w-full accent-primary-500" />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>Very low</span><span>Very high</span>
                  </div>
                </FormField>
                <FormField label="Nutrition Status">
                  <select {...register("nutrition_status")} className="form-input">
                    <option value="poor">Poor — often skip meals, limited variety</option>
                    <option value="fair">Fair — some balanced meals</option>
                    <option value="good">Good — mostly balanced diet</option>
                    <option value="excellent">Excellent — very balanced diet</option>
                  </select>
                </FormField>
              </div>
            </motion.div>
          )}

          {/* Step 5: Symptoms */}
          {currentStep === 5 && (
            <motion.div key="step5" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <StepHeader step={STEPS[4]} />
              <p className="text-gray-500 text-sm mt-2 mb-4">Select all symptoms you are currently experiencing:</p>
              <div className="flex flex-wrap gap-2">
                {COMMON_SYMPTOMS.map((symptom) => (
                  <button key={symptom} type="button"
                    onClick={() => toggleSymptom(symptom)}
                    className={`px-3 py-2 rounded-full text-sm font-medium transition-all ${
                      selectedSymptoms.includes(symptom)
                        ? "bg-primary-500 text-white shadow-glow-primary"
                        : "bg-white text-gray-600 border border-gray-200 hover:border-primary-300"
                    }`}>
                    {symptom.replace(/_/g, " ")}
                  </button>
                ))}
              </div>
              {selectedSymptoms.some(s => ["heavy_bleeding", "seizure", "no_fetal_movement", "chest_pain"].includes(s)) && (
                <div className="mt-4 bg-emergency-50 border border-emergency-200 rounded-2xl p-4">
                  <p className="text-emergency-700 text-sm font-medium">
                    ⚠️ You have selected emergency symptoms. Please seek medical care immediately after completing this assessment.
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation */}
        <div className="flex gap-3 mt-8">
          {currentStep > 1 && (
            <button type="button" onClick={() => setCurrentStep(s => s - 1)}
              className="flex-1 py-4 rounded-2xl border-2 border-gray-200 text-gray-600 font-semibold flex items-center justify-center gap-2">
              <ChevronLeft className="w-4 h-4" /> Back
            </button>
          )}
          {currentStep < STEPS.length ? (
            <button type="button" onClick={() => setCurrentStep(s => s + 1)}
              className="flex-1 py-4 rounded-2xl bg-primary-500 text-white font-semibold flex items-center justify-center gap-2 shadow-glow-primary">
              Next <ChevronRight className="w-4 h-4" />
            </button>
          ) : (
            <button type="submit" disabled={assessMutation.isPending}
              className="flex-1 py-4 rounded-2xl bg-primary-500 text-white font-bold flex items-center justify-center gap-2 shadow-glow-primary disabled:opacity-60">
              {assessMutation.isPending ? (
                <><span className="animate-spin">⟳</span> Analyzing...</>
              ) : (
                <><Activity className="w-4 h-4" /> Get Assessment</>
              )}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

function StepHeader({ step }: { step: typeof STEPS[0] }) {
  const Icon = step.icon;
  return (
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-2xl bg-primary-100 flex items-center justify-center">
        <Icon className="w-5 h-5 text-primary-600" />
      </div>
      <div>
        <h2 className="font-bold text-gray-900">{step.title}</h2>
        <p className="text-gray-500 text-xs">{step.description}</p>
      </div>
    </div>
  );
}

function FormField({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-gray-700 text-sm font-medium mb-1.5">{label}</label>
      {children}
      {error && <p className="text-emergency-500 text-xs mt-1">{error}</p>}
    </div>
  );
}
