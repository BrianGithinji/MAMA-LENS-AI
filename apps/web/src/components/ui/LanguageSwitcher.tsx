import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { LANGUAGES } from "../../i18n";
import { useAuthStore } from "../../store/authStore";

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const current = LANGUAGES.find((l) => l.code === i18n.language) ?? LANGUAGES[0];

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const { setLanguage } = useAuthStore();

  const select = (code: string) => {
    i18n.changeLanguage(code);
    localStorage.setItem("mama_lang", code);
    setLanguage(code);
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white/80 backdrop-blur-sm border border-gray-200 shadow-sm hover:bg-white transition-all text-sm font-medium text-gray-700"
      >
        <span className="text-base leading-none">{current.flag}</span>
        <span className="hidden sm:inline">{current.nativeLabel}</span>
        <svg className={`w-3.5 h-3.5 text-gray-400 transition-transform ${open ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute right-0 mt-1.5 w-44 bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden z-50">
          {LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              onClick={() => select(lang.code)}
              className={`w-full flex items-center gap-2.5 px-3.5 py-2.5 text-sm transition-colors hover:bg-primary-50 ${
                lang.code === i18n.language
                  ? "bg-primary-50 text-primary-700 font-semibold"
                  : "text-gray-700"
              }`}
            >
              <span className="text-base">{lang.flag}</span>
              <div className="text-left">
                <div className="leading-tight">{lang.nativeLabel}</div>
                <div className="text-xs text-gray-400 leading-tight">{lang.label}</div>
              </div>
              {lang.code === i18n.language && (
                <svg className="w-3.5 h-3.5 text-primary-500 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
