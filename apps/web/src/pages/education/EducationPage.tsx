import { useQuery } from "@tanstack/react-query";
import { BookOpen, Baby, Apple, AlertTriangle, Calendar } from "lucide-react";
import { educationAPI } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import { useTranslation } from "react-i18next";

export default function EducationPage() {
  const { user, language } = useAuthStore();
  const { t } = useTranslation();
  const lang = language || user?.preferred_language || "en";

  const { data: dangerSigns } = useQuery({
    queryKey: ["danger-signs", lang],
    queryFn: () => educationAPI.getDangerSigns(lang).then(r => r.data),
  });

  const topics = [
    { icon: Baby,          title: t("week_by_week"),      desc: t("education_subtitle"),  color: "bg-primary-100 text-primary-600" },
    { icon: Apple,         title: t("nutrition_guide"),   desc: t("education_subtitle"),  color: "bg-secondary-100 text-secondary-600" },
    { icon: AlertTriangle, title: t("danger_signs_title"),desc: t("seek_care_now"),       color: "bg-emergency-100 text-emergency-600" },
    { icon: Calendar,      title: t("anc_schedule"),      desc: t("next_anc"),            color: "bg-calm-100 text-calm-600" },
  ];

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      <div className="bg-gradient-to-br from-secondary-500 to-secondary-700 px-6 pt-10 pb-16">
        <BookOpen className="w-10 h-10 text-white mb-3" />
        <h1 className="text-white text-2xl font-bold">{t("education_title")}</h1>
        <p className="text-secondary-100 text-sm mt-1">{t("education_subtitle")}</p>
      </div>

      <div className="max-w-lg mx-auto px-4 -mt-8 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          {topics.map(({ icon: Icon, title, desc, color }) => (
            <div key={title} className="bg-white rounded-3xl shadow-card p-4">
              <div className={`w-10 h-10 rounded-2xl flex items-center justify-center mb-3 ${color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <p className="font-semibold text-gray-900 text-sm">{title}</p>
              <p className="text-gray-400 text-xs mt-0.5">{desc}</p>
            </div>
          ))}
        </div>

        {dangerSigns && (
          <div className="bg-white rounded-3xl shadow-card p-5">
            <h2 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-emergency-500" />
              {dangerSigns.title}
            </h2>
            <p className="text-gray-500 text-sm mb-3">{dangerSigns.subtitle}</p>
            <div className="space-y-2">
              {dangerSigns.signs?.map((sign: string, i: number) => (
                <div key={i} className="flex items-center gap-2 p-2 bg-emergency-50 rounded-xl">
                  <AlertTriangle className="w-4 h-4 text-emergency-500 flex-shrink-0" />
                  <p className="text-gray-700 text-sm">{sign}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 flex gap-2">
              {dangerSigns.emergency_numbers?.map((num: string) => (
                <a key={num} href={`tel:${num}`}
                  className="flex-1 text-center py-2 bg-emergency-500 text-white rounded-2xl text-sm font-bold">
                  Call {num}
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
