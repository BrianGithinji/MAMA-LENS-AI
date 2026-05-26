import { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  ChevronLeft, ChevronRight, Camera, Eye, Hand, Fingerprint,
  Smile, CheckCircle, AlertCircle, RefreshCw, Activity,
} from "lucide-react";
import { anemiaAPI } from "../../api/client";

// ─── Site configuration ────────────────────────────────────────────────────
const SITES = [
  {
    id: "conjunctiva",
    label: "Inner Eyelid",
    subtitle: "Pull down your lower eyelid gently",
    icon: Eye,
    color: "bg-calm-100 text-calm-600",
    accent: "border-calm-400",
    tip: "In good lighting, gently pull down your lower eyelid and take a close-up photo of the pink inner surface.",
    example: "Healthy: bright pink/red · Anemic: pale pink or white",
    importance: "Most accurate indicator — 45% weight",
  },
  {
    id: "palm",
    label: "Palm of Hand",
    subtitle: "Open your hand flat in good light",
    icon: Hand,
    color: "bg-warm-100 text-warm-600",
    accent: "border-warm-400",
    tip: "Stretch your palm open under natural or bright light. Capture the full inner palm surface.",
    example: "Healthy: pink creases · Anemic: pale or white creases",
    importance: "WHO IMCI standard — 30% weight",
  },
  {
    id: "nail",
    label: "Fingernail Bed",
    subtitle: "Press and release your fingernail",
    icon: Fingerprint,
    color: "bg-secondary-100 text-secondary-600",
    accent: "border-secondary-400",
    tip: "Press your fingernail briefly, release, then immediately photograph the nail bed color.",
    example: "Healthy: pink returns quickly · Anemic: stays pale",
    importance: "Capillary refill indicator — 15% weight",
  },
  {
    id: "tongue",
    label: "Tongue",
    subtitle: "Stick out your tongue in bright light",
    icon: Smile,
    color: "bg-primary-100 text-primary-600",
    accent: "border-primary-400",
    tip: "Open your mouth wide, stick out your tongue, and photograph the top surface in good lighting.",
    example: "Healthy: deep pink/red · Anemic: pale pink or white",
    importance: "Oral mucosal pallor — 10% weight",
  },
];

const ANEMIA_SYMPTOMS = [
  "fatigue", "dizziness", "pale_skin", "shortness_of_breath",
  "rapid_heartbeat", "headache", "cold_hands", "difficulty_breathing",
];

type CapturedImages = Record<string, string>; // site -> base64

export default function AnemiaDetectionPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<"intro" | "capture" | "symptoms">("intro");
  const [activeSiteIdx, setActiveSiteIdx] = useState(0);
  const [captured, setCaptured] = useState<CapturedImages>({});
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [gestationalAge, setGestationalAge] = useState<number | "">("");
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const detectMutation = useMutation({
    mutationFn: (data: object) => anemiaAPI.detect(data),
    onSuccess: (res) => {
      toast.success("Analysis complete!");
      navigate(`/anemia/result/${res.data.detection_id}`);
    },
    onError: () => toast.error("Analysis failed. Please try again."),
  });

  // ─── Camera helpers ──────────────────────────────────────────────────────
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: 1280, height: 720 },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setCameraActive(true);
    } catch {
      toast.error("Camera access denied. Please allow camera permissions.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setCameraActive(false);
  }, []);

  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    const canvas = canvasRef.current;
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    canvas.getContext("2d")!.drawImage(videoRef.current, 0, 0);
    const b64 = canvas.toDataURL("image/jpeg", 0.85);
    const site = SITES[activeSiteIdx].id;
    setCaptured((prev) => ({ ...prev, [site]: b64 }));
    stopCamera();
  }, [activeSiteIdx, stopCamera]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const b64 = ev.target?.result as string;
      const site = SITES[activeSiteIdx].id;
      setCaptured((prev) => ({ ...prev, [site]: b64 }));
    };
    reader.readAsDataURL(file);
  };

  const retake = () => {
    const site = SITES[activeSiteIdx].id;
    setCaptured((prev) => { const n = { ...prev }; delete n[site]; return n; });
  };

  const toggleSymptom = (s: string) =>
    setSelectedSymptoms((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );

  const handleSubmit = () => {
    const images = Object.entries(captured).map(([site, image_b64]) => ({
      site,
      image_b64,
    }));
    if (images.length === 0) {
      toast.error("Please capture at least one image.");
      return;
    }
    detectMutation.mutate({
      images,
      gestational_age_weeks: gestationalAge || undefined,
      reported_symptoms: selectedSymptoms,
    });
  };

  const currentSite = SITES[activeSiteIdx];
  const SiteIcon = currentSite.icon;
  const capturedCount = Object.keys(captured).length;

  // ─── Intro screen ────────────────────────────────────────────────────────
  if (step === "intro") {
    return (
      <div className="min-h-screen bg-warm-50 pb-20">
        <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
          <div className="max-w-lg mx-auto flex items-center gap-3">
            <button onClick={() => navigate(-1)} className="p-2 rounded-xl hover:bg-gray-100">
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h1 className="font-bold text-gray-900">Anemia Detection</h1>
          </div>
        </div>

        <div className="max-w-lg mx-auto px-4 pt-6 space-y-5">
          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-br from-red-500 to-red-700 rounded-3xl p-6 text-white"
          >
            <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mb-4">
              <Activity className="w-7 h-7 text-white" />
            </div>
            <h2 className="text-xl font-bold mb-2">AI Anemia Screening</h2>
            <p className="text-red-100 text-sm leading-relaxed">
              Detect maternal anemia using your phone camera — no blood test needed.
              Analyzes pallor in your eyelid, palm, nails, and tongue.
            </p>
          </motion.div>

          {/* How it works */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="bg-white rounded-3xl p-5 shadow-soft"
          >
            <h3 className="font-semibold text-gray-900 mb-4">How it works</h3>
            <div className="space-y-3">
              {SITES.map((site, i) => {
                const Icon = site.icon;
                return (
                  <div key={site.id} className="flex items-start gap-3">
                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${site.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-gray-900 text-sm font-medium">{site.label}</p>
                      <p className="text-gray-500 text-xs">{site.importance}</p>
                    </div>
                    <span className="ml-auto text-xs text-gray-400 font-medium">Step {i + 1}</span>
                  </div>
                );
              })}
            </div>
          </motion.div>

          {/* Dataset note */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="bg-calm-50 border border-calm-200 rounded-2xl p-4"
          >
            <p className="text-calm-700 text-xs leading-relaxed">
              <strong>Validated datasets:</strong> WHO IMCI pallor grading · ShenZhen Anemia Dataset ·
              MADC palmar pallor corpus · Kaggle Anemia Detection Dataset (nail/conjunctiva).
              Calibrated for Sub-Saharan African skin tones.
            </p>
          </motion.div>

          <button
            onClick={() => setStep("capture")}
            className="w-full py-4 bg-red-500 text-white font-bold rounded-2xl flex items-center justify-center gap-2 shadow-glow-primary"
          >
            <Camera className="w-5 h-5" /> Start Screening
          </button>
        </div>
      </div>
    );
  }

  // ─── Capture screen ──────────────────────────────────────────────────────
  if (step === "capture") {
    return (
      <div className="min-h-screen bg-warm-50 pb-20">
        {/* Header */}
        <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
          <div className="max-w-lg mx-auto">
            <div className="flex items-center gap-3 mb-3">
              <button
                onClick={() => { stopCamera(); setStep("intro"); }}
                className="p-2 rounded-xl hover:bg-gray-100"
              >
                <ChevronLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex-1">
                <h1 className="font-bold text-gray-900 text-base">Capture Images</h1>
                <p className="text-gray-500 text-xs">
                  Site {activeSiteIdx + 1} of {SITES.length} · {capturedCount} captured
                </p>
              </div>
            </div>
            {/* Site tabs */}
            <div className="flex gap-2 overflow-x-auto pb-1">
              {SITES.map((site, i) => {
                const Icon = site.icon;
                const done = !!captured[site.id];
                return (
                  <button
                    key={site.id}
                    onClick={() => { stopCamera(); setActiveSiteIdx(i); }}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all border-2 ${
                      i === activeSiteIdx
                        ? `${site.accent} bg-white text-gray-900`
                        : done
                        ? "border-secondary-300 bg-secondary-50 text-secondary-700"
                        : "border-gray-200 bg-gray-50 text-gray-500"
                    }`}
                  >
                    {done ? <CheckCircle className="w-3 h-3 text-secondary-500" /> : <Icon className="w-3 h-3" />}
                    {site.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div className="max-w-lg mx-auto px-4 pt-4 space-y-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeSiteIdx}
              initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
            >
              {/* Site info */}
              <div className={`flex items-center gap-3 p-4 rounded-2xl ${currentSite.color.replace("text-", "border-").replace("bg-", "bg-")} bg-white border mb-4`}>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${currentSite.color}`}>
                  <SiteIcon className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">{currentSite.label}</p>
                  <p className="text-gray-500 text-xs">{currentSite.subtitle}</p>
                </div>
              </div>

              {/* Tip */}
              <div className="bg-calm-50 border border-calm-200 rounded-2xl p-3 mb-4">
                <p className="text-calm-700 text-xs leading-relaxed">{currentSite.tip}</p>
                <p className="text-calm-600 text-xs mt-1 font-medium">{currentSite.example}</p>
              </div>

              {/* Camera / Preview */}
              {captured[currentSite.id] ? (
                <div className="relative rounded-3xl overflow-hidden bg-black aspect-video mb-4">
                  <img
                    src={captured[currentSite.id]}
                    alt="Captured"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 right-3 bg-secondary-500 text-white text-xs px-3 py-1 rounded-full flex items-center gap-1">
                    <CheckCircle className="w-3 h-3" /> Captured
                  </div>
                  <button
                    onClick={retake}
                    className="absolute bottom-3 right-3 bg-white/90 text-gray-700 text-xs px-3 py-1.5 rounded-full flex items-center gap-1 font-medium"
                  >
                    <RefreshCw className="w-3 h-3" /> Retake
                  </button>
                </div>
              ) : cameraActive ? (
                <div className="relative rounded-3xl overflow-hidden bg-black aspect-video mb-4">
                  <video ref={videoRef} className="w-full h-full object-cover" playsInline muted />
                  {/* Guide overlay */}
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="border-2 border-white/60 rounded-2xl w-2/3 h-2/3 flex items-center justify-center">
                      <p className="text-white/80 text-xs text-center px-2">Position {currentSite.label} here</p>
                    </div>
                  </div>
                  <button
                    onClick={capturePhoto}
                    className="absolute bottom-4 left-1/2 -translate-x-1/2 w-16 h-16 bg-white rounded-full border-4 border-gray-300 flex items-center justify-center shadow-lg"
                  >
                    <div className="w-12 h-12 bg-red-500 rounded-full" />
                  </button>
                  <button
                    onClick={stopCamera}
                    className="absolute top-3 right-3 bg-black/50 text-white text-xs px-3 py-1.5 rounded-full"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="rounded-3xl border-2 border-dashed border-gray-200 bg-white aspect-video mb-4 flex flex-col items-center justify-center gap-3">
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${currentSite.color}`}>
                    <SiteIcon className="w-8 h-8" />
                  </div>
                  <p className="text-gray-500 text-sm">No image captured yet</p>
                </div>
              )}

              <canvas ref={canvasRef} className="hidden" />

              {/* Capture buttons */}
              {!captured[currentSite.id] && !cameraActive && (
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={startCamera}
                    className="py-4 bg-red-500 text-white font-semibold rounded-2xl flex items-center justify-center gap-2"
                  >
                    <Camera className="w-4 h-4" /> Use Camera
                  </button>
                  <label className="py-4 border-2 border-gray-200 text-gray-700 font-semibold rounded-2xl flex items-center justify-center gap-2 cursor-pointer">
                    <input type="file" accept="image/*" className="hidden" onChange={handleFileUpload} />
                    Upload Photo
                  </label>
                </div>
              )}

              {/* Navigation */}
              <div className="flex gap-3 mt-4">
                {activeSiteIdx > 0 && (
                  <button
                    onClick={() => { stopCamera(); setActiveSiteIdx((i) => i - 1); }}
                    className="flex-1 py-3 rounded-2xl border-2 border-gray-200 text-gray-600 font-semibold flex items-center justify-center gap-2"
                  >
                    <ChevronLeft className="w-4 h-4" /> Previous
                  </button>
                )}
                {activeSiteIdx < SITES.length - 1 ? (
                  <button
                    onClick={() => { stopCamera(); setActiveSiteIdx((i) => i + 1); }}
                    className="flex-1 py-3 rounded-2xl bg-gray-900 text-white font-semibold flex items-center justify-center gap-2"
                  >
                    Next <ChevronRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => { stopCamera(); setStep("symptoms"); }}
                    disabled={capturedCount === 0}
                    className="flex-1 py-3 rounded-2xl bg-red-500 text-white font-bold flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    Continue <ChevronRight className="w-4 h-4" />
                  </button>
                )}
              </div>

              {capturedCount > 0 && activeSiteIdx === SITES.length - 1 && (
                <p className="text-center text-gray-500 text-xs mt-2">
                  {capturedCount} of {SITES.length} sites captured
                  {capturedCount < SITES.length && " — more sites = higher accuracy"}
                </p>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    );
  }

  // ─── Symptoms screen ─────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <button onClick={() => setStep("capture")} className="p-2 rounded-xl hover:bg-gray-100">
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="font-bold text-gray-900 text-base">Symptoms & Details</h1>
            <p className="text-gray-500 text-xs">Improves detection accuracy</p>
          </div>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-6 space-y-5">
        {/* Captured summary */}
        <div className="bg-white rounded-2xl p-4 shadow-soft">
          <p className="text-gray-700 text-sm font-medium mb-3">Images captured</p>
          <div className="flex gap-2 flex-wrap">
            {SITES.map((site) => (
              <div
                key={site.id}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${
                  captured[site.id]
                    ? "bg-secondary-100 text-secondary-700"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                {captured[site.id]
                  ? <CheckCircle className="w-3 h-3" />
                  : <AlertCircle className="w-3 h-3" />}
                {site.label}
              </div>
            ))}
          </div>
        </div>

        {/* Gestational age */}
        <div className="bg-white rounded-2xl p-4 shadow-soft">
          <label className="block text-gray-700 text-sm font-medium mb-2">
            Weeks pregnant (optional)
          </label>
          <input
            type="number"
            min={1} max={42}
            value={gestationalAge}
            onChange={(e) => setGestationalAge(e.target.value ? Number(e.target.value) : "")}
            className="form-input"
            placeholder="e.g. 24"
          />
        </div>

        {/* Symptoms */}
        <div className="bg-white rounded-2xl p-4 shadow-soft">
          <p className="text-gray-700 text-sm font-medium mb-3">
            Are you experiencing any of these?
          </p>
          <div className="flex flex-wrap gap-2">
            {ANEMIA_SYMPTOMS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => toggleSymptom(s)}
                className={`px-3 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedSymptoms.includes(s)
                    ? "bg-red-500 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {s.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        {selectedSymptoms.includes("difficulty_breathing") && (
          <div className="bg-emergency-50 border border-emergency-200 rounded-2xl p-4">
            <p className="text-emergency-700 text-sm font-medium">
              ⚠️ Difficulty breathing with anemia may be an emergency. Seek care immediately after this screening.
            </p>
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={detectMutation.isPending || capturedCount === 0}
          className="w-full py-4 bg-red-500 text-white font-bold rounded-2xl flex items-center justify-center gap-2 shadow-glow-primary disabled:opacity-60"
        >
          {detectMutation.isPending ? (
            <><span className="animate-spin">⏳</span> Analyzing images...</>
          ) : (
            <><Activity className="w-5 h-5" /> Analyze for Anemia</>
          )}
        </button>

        <p className="text-center text-gray-400 text-xs pb-4">
          AI screening only — not a medical diagnosis. Always confirm with a blood test.
        </p>
      </div>
    </div>
  );
}
