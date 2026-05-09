/**
 * MAMA-LENS AI — Main Dashboard
 * Personalized maternal health overview
 */

import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Heart, AlertTriangle, Calendar, MessageCircle,
  MapPin, BookOpen, Activity, Phone, Baby, Smile,
} from "lucide-react";
import { useAuthStore } from "../../store/authStore";
import { pregnancyAPI, riskAPI, notificationsAPI } from "../../api/client";
import RiskLevelBadge from "../../components/ui/RiskLevelBadge";
import PregnancyWeekCard from "../../components/pregnancy/PregnancyWeekCard";
import QuickActionCard from "../../components/dashboard/QuickActionCard";
import EmergencyBanner from "../../components/emergency/EmergencyBanner";
import Logo from "../../components/brand/Logo";

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: pregnancy } = useQuery({
    queryKey: ["pregnancy", "active"],
    queryFn: () => pregnancyAPI.getActive().then((r) => r.data),
  });

  const { data: latestRisk } = useQuery({
    queryKey: ["risk", "history"],
    queryFn: () => riskAPI.getHistory(1).then((r) => r.data[0]),
  });

  const { data: notifications } = useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: () => notificationsAPI.getAll(true).then((r) => r.data),
  });

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  const quickActions = [
    {
      icon: Activity,
      label: "Risk Assessment",
      description: "Check your health status",
      href: "/risk-assessment",
      color: "bg-primary-50 text-primary-600",
      urgent: latestRisk?.overall_risk_level === "high" || latestRisk?.overall_risk_level === "emergency",
    },
    {
      icon: MessageCircle,
      label: "Talk to MAMA",
      description: "AI avatar support",
      href: "/avatar",
      color: "bg-calm-50 text-calm-600",
    },
    {
      icon: Calendar,
      label: "Appointments",
      description: "Book or view visits",
      href: "/appointments",
      color: "bg-secondary-50 text-secondary-600",
    },
    {
      icon: Phone,
      label: "Telemedicine",
      description: "Video consultation",
      href: "/telemedicine",
      color: "bg-warm-50 text-warm-600",
    },
    {
      icon: MapPin,
      label: "Find Clinic",
      description: "Nearby facilities",
      href: "/facilities",
      color: "bg-earth-50 text-earth-600",
    },
    {
      icon: BookOpen,
      label: "Education",
      description: "Pregnancy guidance",
      href: "/education",
      color: "bg-purple-50 text-purple-600",
    },
    {
      icon: Smile,
      label: "Mental Health",
      description: "Emotional support",
      href: "/mental-health",
      color: "bg-pink-50 text-pink-600",
    },
    {
      icon: Heart,
      label: "Grief Support",
      description: "You are not alone",
      href: "/grief-support",
      color: "bg-rose-50 text-rose-600",
    },
  ];

  return (
    <div className="min-h-screen bg-warm-50 pb-20">
      {/* Emergency Banner */}
      {latestRisk?.is_emergency && <EmergencyBanner />}

      {/* Header */}
      <div className="bg-gradient-to-br from-primary-500 via-primary-600 to-earth-600 px-6 pt-8 pb-6">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl mx-auto"
        >
          {/* Logo in header — white pill so PNG background blends cleanly */}
          <div className="flex items-center justify-between mb-4">
            <div className="bg-white/95 rounded-2xl px-3 py-1.5 inline-block">
              <Logo variant="compact" width={100} />
            </div>
            <Link to="/notifications" className="relative">
              {notifications && notifications.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-warm-400 rounded-full text-white text-[9px] flex items-center justify-center font-bold">
                  {notifications.length}
                </span>
              )}
            </Link>
          </div>

          <p className="text-primary-100 text-sm font-medium">{greeting()},</p>
          <h1 className="text-white text-2xl font-bold mt-0.5">
            {user?.first_name} 💚
          </h1>
          <p className="text-primary-100 text-sm mt-1">
            Here to support you every step of the way
          </p>

          {/* Unread notifications badge */}
          {notifications && notifications.length > 0 && (
            <Link
              to="/notifications"
              className="inline-flex items-center gap-2 mt-3 bg-white/20 backdrop-blur-sm text-white text-xs px-3 py-1.5 rounded-full"
            >
              <span className="w-2 h-2 bg-warm-400 rounded-full animate-pulse" />
              {notifications.length} new notification{notifications.length > 1 ? "s" : ""}
            </Link>
          )}
        </motion.div>
      </div>

      <div className="max-w-2xl mx-auto px-4 pt-4">
        {/* Pregnancy Week Card */}
        {pregnancy && pregnancy.gestational_age_weeks && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <PregnancyWeekCard
              week={pregnancy.gestational_age_weeks}
              dueDate={pregnancy.estimated_due_date}
              status={pregnancy.status}
            />
          </motion.div>
        )}

        {/* Risk Status Card */}
        {latestRisk && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-3xl shadow-card p-5 mt-4"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-xs font-medium uppercase tracking-wide">
                  Latest Risk Assessment
                </p>
                <RiskLevelBadge level={latestRisk.overall_risk_level} large />
              </div>
              <Link
                to={`/risk-assessment/result/${latestRisk.id}`}
                className="text-primary-500 text-sm font-medium"
              >
                View details →
              </Link>
            </div>
            {latestRisk.is_emergency && (
              <div className="mt-3 bg-emergency-50 border border-emergency-200 rounded-2xl p-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-emergency-500 flex-shrink-0" />
                <p className="text-emergency-700 text-xs font-medium">
                  Emergency detected. Please seek medical care immediately.
                </p>
              </div>
            )}
          </motion.div>
        )}

        {/* Quick Actions Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-6"
        >
          <h2 className="text-gray-800 font-semibold text-base mb-3">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            {quickActions.map((action, index) => (
              <motion.div
                key={action.href}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 * index }}
              >
                <QuickActionCard {...action} />
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Emergency Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6"
        >
          <Link
            to="/emergency"
            className="flex items-center justify-center gap-3 w-full bg-emergency-500 hover:bg-emergency-600 text-white font-bold py-4 rounded-3xl shadow-glow-primary transition-all active:scale-95"
          >
            <AlertTriangle className="w-5 h-5" />
            Emergency Help
          </Link>
        </motion.div>

        {/* Footer note */}
        <p className="text-center text-gray-400 text-xs mt-6 pb-4">
          MAMA-LENS AI provides guidance, not medical diagnosis.
          Always consult a healthcare professional.
        </p>
      </div>
    </div>
  );
}
