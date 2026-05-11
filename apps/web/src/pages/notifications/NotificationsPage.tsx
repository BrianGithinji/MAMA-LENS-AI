import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Bell } from "lucide-react";
import { notificationsAPI } from "../../api/client";

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const { data: notifications } = useQuery({ queryKey: ["notifications"], queryFn: () => notificationsAPI.getAll().then(r => r.data) });
  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationsAPI.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-white border-b border-gray-100 px-4 py-4 sticky top-0 z-10">
        <div className="max-w-lg mx-auto">
          <h1 className="font-bold text-gray-900 text-lg">Notifications</h1>
        </div>
      </div>
      <div className="max-w-lg mx-auto px-4 pt-4 space-y-2">
        {notifications?.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <Bell className="w-10 h-10 mx-auto mb-3 text-gray-200" />
            <p>No notifications yet.</p>
          </div>
        )}
        {notifications?.map((notif: any) => (
          <div key={notif.id} onClick={() => !notif.is_read && markReadMutation.mutate(notif.id)}
            className={`bg-white rounded-2xl p-4 cursor-pointer transition-all ${!notif.is_read ? "border-l-4 border-primary-500" : ""}`}>
            <p className="font-semibold text-gray-900 text-sm">{notif.title}</p>
            <p className="text-gray-500 text-xs mt-1">{notif.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
