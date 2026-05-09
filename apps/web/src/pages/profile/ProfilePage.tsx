/**
 * MAMA-LENS AI — Profile Page
 */
import { useAuthStore } from "../../store/authStore";
import { useNavigate } from "react-router-dom";
import { User, Globe, Bell, Shield, LogOut, ChevronRight } from "lucide-react";
import { authAPI } from "../../api/client";
import toast from "react-hot-toast";

export default function ProfilePage() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try { await authAPI.logout(); } catch {}
    logout();
    navigate("/login");
    toast.success("Logged out successfully");
  };

  const menuItems = [
    { icon: User, label: "Personal Information", href: "/profile/edit" },
    { icon: Globe, label: "Language & Accessibility", href: "/profile/language" },
    { icon: Bell, label: "Notification Preferences", href: "/profile/notifications" },
    { icon: Shield, label: "Privacy & Data", href: "/profile/privacy" },
  ];

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-gradient-to-br from-earth-500 to-earth-700 px-6 pt-10 pb-16">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-3xl bg-white/20 flex items-center justify-center">
            <User className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-white text-xl font-bold">{user?.first_name} {user?.last_name}</h1>
            <p className="text-earth-100 text-sm">{user?.role?.replace(/_/g, " ")}</p>
            <p className="text-earth-200 text-xs">{user?.phone_number || user?.email}</p>
          </div>
        </div>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-6 space-y-3">
        <div className="bg-white rounded-3xl shadow-card overflow-hidden">
          {menuItems.map(({ icon: Icon, label }, i) => (
            <div key={label}>
              <button className="w-full flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-all">
                <div className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-gray-600" />
                </div>
                <span className="flex-1 text-left text-gray-800 text-sm font-medium">{label}</span>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </button>
              {i < menuItems.length - 1 && <div className="h-px bg-gray-50 mx-5" />}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-3xl shadow-card p-4">
          <p className="text-gray-500 text-xs text-center">
            MAMA-LENS AI v1.0.0 • Your data is encrypted and protected
          </p>
        </div>

        <button onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 py-4 bg-emergency-50 text-emergency-600 font-semibold rounded-3xl border border-emergency-200">
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
