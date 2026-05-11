import { useQuery } from "@tanstack/react-query";
import { Baby, Heart } from "lucide-react";
import { pregnancyAPI, educationAPI } from "../../api/client";
import { useAuthStore } from "../../store/authStore";

export default function PregnancyJourneyPage() {
  const { user } = useAuthStore();
  const { data: pregnancy } = useQuery({ queryKey: ["pregnancy", "active"], queryFn: () => pregnancyAPI.getActive().then(r => r.data) });
  const week = pregnancy?.gestational_age_weeks || 20;
  const { data: weeklyEd } = useQuery({ queryKey: ["education", week], queryFn: () => educationAPI.getWeekly(week, user?.preferred_language).then(r => r.data) });

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-gradient-to-br from-primary-400 to-primary-600 px-6 pt-10 pb-16">
        <Baby className="w-10 h-10 text-white mb-3" />
        <h1 className="text-white text-2xl font-bold">My Pregnancy Journey</h1>
        {pregnancy && <p className="text-primary-100 text-sm mt-1">Week {week} • {pregnancy.status}</p>}
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-8 space-y-4">
        {weeklyEd && (
          <div className="bg-white rounded-3xl shadow-card p-5">
            <h2 className="font-bold text-gray-900 mb-2">This Week</h2>
            <p className="text-gray-700 text-sm leading-relaxed">{weeklyEd.content}</p>
          </div>
        )}

        {pregnancy && (
          <div className="bg-white rounded-3xl shadow-card p-5">
            <h2 className="font-bold text-gray-900 mb-3">Pregnancy Summary</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Status</span><span className="font-medium text-gray-900 capitalize">{pregnancy.status}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Gestational Age</span><span className="font-medium text-gray-900">Week {week}</span></div>
              {pregnancy.estimated_due_date && <div className="flex justify-between"><span className="text-gray-500">Due Date</span><span className="font-medium text-gray-900">{new Date(pregnancy.estimated_due_date).toLocaleDateString()}</span></div>}
              <div className="flex justify-between"><span className="text-gray-500">Obstetric History</span><span className="font-medium text-gray-900">{pregnancy.obstetric_history}</span></div>
            </div>
          </div>
        )}

        {pregnancy?.grief_support_requested && (
          <div className="bg-rose-50 border border-rose-200 rounded-3xl p-5">
            <div className="flex items-center gap-2 mb-2">
              <Heart className="w-5 h-5 text-rose-500" fill="currentColor" />
              <h3 className="font-bold text-rose-800">Grief Support Available</h3>
            </div>
            <p className="text-rose-700 text-sm">We are here for you during this difficult time. Compassionate support is available whenever you need it.</p>
          </div>
        )}
      </div>
    </div>
  );
}
