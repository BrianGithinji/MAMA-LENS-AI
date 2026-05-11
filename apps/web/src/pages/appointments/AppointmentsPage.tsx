import { Calendar, Plus } from "lucide-react";

export default function AppointmentsPage() {
  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <h1 className="font-bold text-gray-900 text-lg">Appointments</h1>
          <button className="w-9 h-9 rounded-xl bg-primary-100 flex items-center justify-center">
            <Plus className="w-5 h-5 text-primary-600" />
          </button>
        </div>
      </div>
      <div className="max-w-lg mx-auto px-4 pt-4">
        <div className="text-center py-12 text-gray-400">
          <Calendar className="w-10 h-10 mx-auto mb-3 text-gray-200" />
          <p>No upcoming appointments.</p>
          <p className="text-sm mt-1">Book your next ANC visit to stay on track.</p>
        </div>
        <div className="bg-calm-50 border border-calm-200 rounded-3xl p-5">
          <h3 className="font-bold text-calm-800 mb-2">WHO ANC Schedule</h3>
          <p className="text-calm-700 text-sm">WHO recommends 8 antenatal care visits at weeks: 12, 20, 26, 30, 34, 36, 38, and 40.</p>
        </div>
      </div>
    </div>
  );
}
