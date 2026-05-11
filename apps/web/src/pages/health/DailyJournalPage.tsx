import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { BookHeart, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";
import { dailyJournalAPI } from "../../api/client";

const MOODS = [
  { value: "great", emoji: "😄", label: "Great" },
  { value: "good", emoji: "🙂", label: "Good" },
  { value: "okay", emoji: "😐", label: "Okay" },
  { value: "low", emoji: "😔", label: "Low" },
  { value: "bad", emoji: "😢", label: "Bad" },
];

const COMMON_SYMPTOMS = [
  "Nausea", "Vomiting", "Headache", "Back pain", "Swelling",
  "Fatigue", "Dizziness", "Cramps", "Spotting", "Shortness of breath",
  "Heartburn", "Insomnia", "Reduced fetal movement",
];

const MOOD_COLORS: Record<string, string> = {
  great: "bg-green-100 text-green-700 border-green-300",
  good: "bg-teal-100 text-teal-700 border-teal-300",
  okay: "bg-yellow-100 text-yellow-700 border-yellow-300",
  low: "bg-orange-100 text-orange-700 border-orange-300",
  bad: "bg-red-100 text-red-700 border-red-300",
};

export default function DailyJournalPage() {
  const qc = useQueryClient();
  const [mood, setMood] = useState("");
  const [energy, setEnergy] = useState(5);
  const [symptoms, setSymptoms] = useState<string[]>([]);
  const [pain, setPain] = useState<number | "">("");
  const [sleep, setSleep] = useState<number | "">("");
  const [notes, setNotes] = useState("");
  const [concerns, setConcerns] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: entries = [] } = useQuery({
    queryKey: ["daily-journal"],
    queryFn: () => dailyJournalAPI.getEntries().then((r) => r.data),
  });

  const { mutate, isPending } = useMutation({
    mutationFn: (data: object) => dailyJournalAPI.logEntry(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["daily-journal"] });
      setMood(""); setEnergy(5); setSymptoms([]); setPain(""); setSleep(""); setNotes(""); setConcerns("");
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
    },
  });

  const toggleSymptom = (s: string) =>
    setSymptoms((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!mood) return;
    mutate({ mood, energy_level: energy, symptoms, pain_level: pain || null, sleep_hours: sleep || null, notes: notes || null, concerns: concerns || null });
  };

  return (
    <div className="min-h-screen bg-warm-50 pb-24">
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center gap-3">
          <BookHeart className="w-5 h-5 text-primary-500" />
          <h1 className="font-bold text-gray-900 text-lg">Daily Journal</h1>
        </div>
        <p className="max-w-lg mx-auto text-xs text-gray-400 mt-0.5 pl-8">
          How are you feeling today? Your entries help your doctor care for you better.
        </p>
      </div>

      <div className="max-w-lg mx-auto px-4 pt-5 space-y-5">
        {/* Entry Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-3xl shadow-card p-5 space-y-5">
          {/* Mood */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-2">How are you feeling? *</p>
            <div className="flex gap-2 flex-wrap">
              {MOODS.map((m) => (
                <button
                  key={m.value}
                  type="button"
                  onClick={() => setMood(m.value)}
                  className={`flex flex-col items-center px-3 py-2 rounded-2xl border-2 transition-all text-sm ${
                    mood === m.value ? MOOD_COLORS[m.value] + " border-2" : "border-gray-100 text-gray-500 hover:border-gray-200"
                  }`}
                >
                  <span className="text-xl">{m.emoji}</span>
                  <span className="text-xs mt-0.5">{m.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Energy */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-1">
              Energy level: <span className="text-primary-600">{energy}/10</span>
            </p>
            <input
              type="range" min={1} max={10} value={energy}
              onChange={(e) => setEnergy(Number(e.target.value))}
              className="w-full accent-primary-500"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-0.5">
              <span>Very tired</span><span>Full of energy</span>
            </div>
          </div>

          {/* Symptoms */}
          <div>
            <p className="text-sm font-semibold text-gray-700 mb-2">Any symptoms today?</p>
            <div className="flex flex-wrap gap-2">
              {COMMON_SYMPTOMS.map((s) => (
                <button
                  key={s} type="button" onClick={() => toggleSymptom(s)}
                  className={`px-3 py-1 rounded-full text-xs border transition-all ${
                    symptoms.includes(s)
                      ? "bg-primary-100 text-primary-700 border-primary-300"
                      : "bg-gray-50 text-gray-500 border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Pain & Sleep */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">Pain level (0–10)</label>
              <input
                type="number" min={0} max={10} placeholder="0 = none"
                value={pain} onChange={(e) => setPain(e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">Sleep (hours)</label>
              <input
                type="number" min={0} max={24} step={0.5} placeholder="e.g. 7.5"
                value={sleep} onChange={(e) => setSleep(e.target.value === "" ? "" : Number(e.target.value))}
                className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-300"
              />
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="text-xs font-medium text-gray-600 block mb-1">Notes for your doctor</label>
            <textarea
              rows={3} placeholder="Describe how you're feeling in your own words..."
              value={notes} onChange={(e) => setNotes(e.target.value)}
              className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-300"
            />
          </div>

          {/* Concerns */}
          <div>
            <label className="text-xs font-medium text-gray-600 flex items-center gap-1 mb-1">
              <AlertCircle className="w-3.5 h-3.5 text-orange-400" />
              Concerns to flag for doctor
            </label>
            <textarea
              rows={2} placeholder="Anything worrying you? Your doctor will see this."
              value={concerns} onChange={(e) => setConcerns(e.target.value)}
              className="w-full border border-orange-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-orange-300"
            />
          </div>

          <button
            type="submit" disabled={!mood || isPending}
            className="w-full bg-primary-600 text-white py-3 rounded-2xl font-semibold text-sm disabled:opacity-50 hover:bg-primary-700 transition-colors"
          >
            {isPending ? "Saving…" : "Save Today's Entry"}
          </button>

          {submitted && (
            <p className="text-center text-sm text-green-600 font-medium">✓ Entry saved! Your doctor can now see this.</p>
          )}
        </form>

        {/* Past Entries */}
        {entries.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-gray-600 mb-3">Past Entries</p>
            <div className="space-y-2">
              {entries.map((e: any) => {
                const moodInfo = MOODS.find((m) => m.value === e.mood);
                const isOpen = expandedId === e.id;
                return (
                  <div key={e.id} className="bg-white rounded-2xl shadow-card overflow-hidden">
                    <button
                      className="w-full flex items-center justify-between px-4 py-3 text-left"
                      onClick={() => setExpandedId(isOpen ? null : e.id)}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xl">{moodInfo?.emoji ?? "📝"}</span>
                        <div>
                          <p className="text-sm font-semibold text-gray-800">{e.date}</p>
                          <p className="text-xs text-gray-400">
                            {moodInfo?.label} · Energy {e.energy_level}/10
                            {e.symptoms?.length > 0 && ` · ${e.symptoms.length} symptom${e.symptoms.length > 1 ? "s" : ""}`}
                          </p>
                        </div>
                      </div>
                      {isOpen ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                    </button>

                    {isOpen && (
                      <div className="px-4 pb-4 space-y-2 border-t border-gray-50 pt-3">
                        {e.symptoms?.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {e.symptoms.map((s: string) => (
                              <span key={s} className="px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full text-xs">{s}</span>
                            ))}
                          </div>
                        )}
                        {e.pain_level != null && <p className="text-xs text-gray-600">Pain: <strong>{e.pain_level}/10</strong></p>}
                        {e.sleep_hours != null && <p className="text-xs text-gray-600">Sleep: <strong>{e.sleep_hours}h</strong></p>}
                        {e.notes && <p className="text-xs text-gray-600 bg-gray-50 rounded-xl p-2">{e.notes}</p>}
                        {e.concerns && (
                          <p className="text-xs text-orange-700 bg-orange-50 rounded-xl p-2 flex gap-1">
                            <AlertCircle className="w-3.5 h-3.5 mt-0.5 shrink-0" />{e.concerns}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
