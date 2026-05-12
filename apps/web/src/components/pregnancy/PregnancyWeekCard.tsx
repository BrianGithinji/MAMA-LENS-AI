import { Baby } from "lucide-react";
import { useTranslation } from "react-i18next";

interface PregnancyWeekCardProps {
  week: number;
  dueDate?: string;
  status: string;
}

const WEEK_SIZES: Record<number, string> = {
  4: "poppy seed", 8: "raspberry", 12: "lime", 16: "avocado",
  20: "banana", 24: "ear of corn", 28: "eggplant", 32: "squash",
  36: "honeydew melon", 40: "watermelon",
};

function getBabySize(week: number): string {
  const keys = Object.keys(WEEK_SIZES).map(Number).sort((a, b) => a - b);
  const closest = keys.reduce((prev, curr) =>
    Math.abs(curr - week) < Math.abs(prev - week) ? curr : prev
  );
  return WEEK_SIZES[closest] || "growing beautifully";
}

export default function PregnancyWeekCard({ week, dueDate, status }: PregnancyWeekCardProps) {
  const { t } = useTranslation();
  const babySize = getBabySize(week);
  const progress = Math.min((week / 40) * 100, 100);

  const trimester = week <= 13
    ? t("first_trimester")
    : week <= 27
    ? t("second_trimester")
    : t("third_trimester");

  if (status === "miscarriage") {
    return (
      <div className="bg-gradient-to-br from-rose-50 to-pink-50 rounded-3xl p-5 shadow-card border border-rose-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-rose-100 flex items-center justify-center">
            <HeartIcon className="w-5 h-5 text-rose-500" />
          </div>
          <div>
            <p className="font-semibold text-rose-800">{t("grief_support")}</p>
            <p className="text-rose-600 text-xs">{t("you_are_not_alone")}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-primary-50 to-warm-50 rounded-3xl p-5 shadow-card border border-primary-100">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-primary-600 text-xs font-medium uppercase tracking-wide">{trimester}</p>
          <h2 className="text-gray-900 font-bold text-2xl mt-0.5">{t("week")} {week}</h2>
          <p className="text-gray-600 text-sm mt-1">
            {t("baby_size")} <span className="font-medium text-primary-600">{babySize}</span>
          </p>
          {dueDate && (
            <p className="text-gray-500 text-xs mt-1">
              {t("due_date_label")}: {new Date(dueDate).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" })}
            </p>
          )}
        </div>
        <div className="w-14 h-14 rounded-2xl bg-primary-100 flex items-center justify-center">
          <Baby className="w-7 h-7 text-primary-500" />
        </div>
      </div>

      <div className="mt-4">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>{t("week")} 1</span>
          <span>{Math.round(progress)}% {t("complete")}</span>
          <span>{t("week")} 40</span>
        </div>
        <div className="h-2 bg-primary-100 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-primary-400 to-primary-600 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }} />
        </div>
      </div>
    </div>
  );
}

function HeartIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 24 24">
      <path d="M12 21.593c-5.63-5.539-11-10.297-11-14.402 0-3.791 3.068-5.191 5.281-5.191 1.312 0 4.151.501 5.719 4.457 1.59-3.968 4.464-4.447 5.726-4.447 2.54 0 5.274 1.621 5.274 5.181 0 4.069-5.136 8.625-11 14.402z" />
    </svg>
  );
}
