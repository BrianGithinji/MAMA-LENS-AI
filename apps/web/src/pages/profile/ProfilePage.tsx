import { useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { useNavigate } from "react-router-dom";
import { User, Globe, Bell, Shield, LogOut, ChevronRight, ChevronLeft, Check } from "lucide-react";
import { authAPI, userAPI } from "../../api/client";
import { useTranslation } from "react-i18next";
import { LANGUAGES } from "../../i18n";
import toast from "react-hot-toast";

export default function ProfilePage() {
  const { user, logout, setLanguage, language } = useAuthStore();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [showLanguagePage, setShowLanguagePage] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleLogout = async () => {
    try { await authAPI.logout(); } catch {}
    logout();
    navigate("/login");
    toast.success("Logged out successfully");
  };

  const handleLanguageSelect = async (code: string) => {
    setSaving(true);
    setLanguage(code);
    try {
      await userAPI.updateProfile({ preferred_language: code });
    } catch {}
    setSaving(false);
    toast.success(t("language_saved"));
    setShowLanguagePage(false);
  };

  if (showLanguagePage) {
    return (
      <div className="min-h-screen bg-warm-50 pb-20">
        <div className="bg-gradient-to-br from-earth-500 to-earth-700 px-6 pt-10 pb-16">
          <button onClick={() => setShowLanguagePage(false)}
            className="flex items-center gap-2 text-white/80 mb-4">
            <ChevronLeft className="w-5 h-5" />
            <span className="text-sm">{t("back")}</span>
          </button>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center">
              <Globe className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-white text-xl font-bold">{t("language_accessibility")}</h1>
              <p className="text-earth-100 text-sm">{t("choose_language")}</p>
            </div>
          </div>
        </div>

        <div className="max-w-lg mx-auto px-4 -mt-6">
          <div className="bg-white rounded-3xl shadow-card overflow-hidden">
            {LANGUAGES.map(({ code, nativeLabel, label, flag }, i) => (
              <div key={code}>
                <button
                  onClick={() => handleLanguageSelect(code)}
                  disabled={saving}
                  className="w-full flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-all"
                >
                  <span className="text-2xl">{flag}</span>
                  <div className="flex-1 text-left">
                    <p className="text-gray-800 text-sm font-medium">{nativeLabel}</p>
                    <p className="text-gray-400 text-xs">{label}</p>
                  </div>
                  {language === code && (
                    <div className="w-6 h-6 rounded-full bg-primary-500 flex items-center justify-center">
                      <Check className="w-3.5 h-3.5 text-white" />
                    </div>
                  )}
                </button>
                {i < LANGUAGES.length - 1 && <div className="h-px bg-gray-50 mx-5" />}
              </div>
            ))}
          </div>

          <div className="mt-4 bg-primary-50 rounded-2xl p-4">
            <p className="text-primary-700 text-xs text-center">
              🌍 Changing language updates the entire app and MAMA chatbot responses
            </p>
          </div>
        </div>
      </div>
    );
  }

  const menuItems = [
    { icon: User,   label: "Personal Information",      action: () => {} },
    { icon: Globe,  label: t("language_accessibility"), action: () => setShowLanguagePage(true) },
    { icon: Bell,   label: "Notification Preferences",  action: () => {} },
    { icon: Shield, label: "Privacy & Data",            action: () => {} },
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
          {menuItems.map(({ icon: Icon, label, action }, i) => (
            <div key={label}>
              <button onClick={action} className="w-full flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-all">
                <div className="w-9 h-9 rounded-xl bg-gray-100 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-gray-600" />
                </div>
                <span className="flex-1 text-left text-gray-800 text-sm font-medium">{label}</span>
                {label === t("language_accessibility") && (
                  <span className="text-xs text-primary-500 font-medium mr-1">
                    {LANGUAGES.find(l => l.code === language)?.nativeLabel}
                  </span>
                )}
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
