import { AlertTriangle, Phone } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function EmergencyBanner() {
  const { t } = useTranslation();
  return (
    <div className="bg-emergency-500 text-white px-4 py-3">
      <div className="max-w-lg mx-auto flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 animate-pulse" />
          <p className="text-sm font-semibold">{t("emergency_detected")}</p>
        </div>
        <a href="tel:999" className="flex items-center gap-1 bg-white text-emergency-600 text-xs font-bold px-3 py-1.5 rounded-full flex-shrink-0">
          <Phone className="w-3 h-3" /> 999
        </a>
      </div>
    </div>
  );
}
