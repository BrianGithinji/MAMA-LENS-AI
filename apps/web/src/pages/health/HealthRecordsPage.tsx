import { useQuery } from "@tanstack/react-query";
import { Activity, Plus } from "lucide-react";
import { healthRecordsAPI } from "../../api/client";

export default function HealthRecordsPage() {
  const { data: records } = useQuery({ queryKey: ["health-records"], queryFn: () => healthRecordsAPI.getAll().then(r => r.data) });

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto flex items-center justify-between">
          <h1 className="font-bold text-gray-900 text-lg">Health Records</h1>
          <button className="w-9 h-9 rounded-xl bg-primary-100 flex items-center justify-center">
            <Plus className="w-5 h-5 text-primary-600" />
          </button>
        </div>
      </div>
      <div className="max-w-lg mx-auto px-4 pt-4 space-y-3">
        {records?.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <Activity className="w-10 h-10 mx-auto mb-3 text-gray-200" />
            <p>No health records yet. Log your vitals to get started.</p>
          </div>
        )}
        {records?.map((record: any) => (
          <div key={record.id} className="bg-white rounded-3xl shadow-card p-4">
            <p className="font-semibold text-gray-900 text-sm capitalize">{record.record_type?.replace(/_/g, " ")}</p>
            <p className="text-gray-400 text-xs mt-1">{new Date(record.created_at).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
