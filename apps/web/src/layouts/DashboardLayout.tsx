import { Outlet, NavLink } from "react-router-dom";
import { Home, Activity, MessageCircle, Calendar, User, BookHeart } from "lucide-react";
import { clsx } from "clsx";
import { useTranslation } from "react-i18next";

export default function DashboardLayout() {
  const { t } = useTranslation();

  const NAV_ITEMS = [
    { icon: Home,          label: t("home"),    href: "/dashboard" },
    { icon: Activity,      label: t("risk"),    href: "/risk-assessment" },
    { icon: MessageCircle, label: t("mama_ai"), href: "/avatar" },
    { icon: BookHeart,     label: t("journal"), href: "/daily-journal" },
    { icon: User,          label: t("profile"), href: "/profile" },
  ];

  return (
    <div className="min-h-screen bg-warm-50">
      <main className="pb-20">
        <Outlet />
      </main>

      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 safe-area-pb z-50">
        <div className="flex items-center justify-around px-2 py-2 max-w-lg mx-auto">
          {NAV_ITEMS.map(({ icon: Icon, label, href }) => (
            <NavLink
              key={href}
              to={href}
              className={({ isActive }) =>
                clsx(
                  "flex flex-col items-center gap-0.5 px-3 py-2 rounded-2xl transition-all",
                  isActive
                    ? "text-primary-600 bg-primary-50"
                    : "text-gray-400 hover:text-gray-600"
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={clsx("w-5 h-5", isActive && "stroke-[2.5]")} />
                  <span className={clsx("text-xs font-medium", isActive && "font-semibold")}>
                    {label}
                  </span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  );
}
