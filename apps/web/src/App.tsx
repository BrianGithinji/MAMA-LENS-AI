import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "./store/authStore";
import AuthLayout from "./layouts/AuthLayout";
import DashboardLayout from "./layouts/DashboardLayout";

import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import VerifyOTPPage from "./pages/auth/VerifyOTPPage";

import DashboardPage from "./pages/dashboard/DashboardPage";
import RiskAssessmentPage from "./pages/risk/RiskAssessmentPage";
import RiskResultPage from "./pages/risk/RiskResultPage";
import PregnancyJourneyPage from "./pages/pregnancy/PregnancyJourneyPage";
import TelemedicinePage from "./pages/telemedicine/TelemedicinePage";
import ConsultationRoomPage from "./pages/telemedicine/ConsultationRoomPage";
import AvatarChatPage from "./pages/avatar/AvatarChatPage";
import FacilitiesMapPage from "./pages/facilities/FacilitiesMapPage";
import EducationPage from "./pages/education/EducationPage";
import HealthRecordsPage from "./pages/health/HealthRecordsPage";
import AppointmentsPage from "./pages/appointments/AppointmentsPage";
import NotificationsPage from "./pages/notifications/NotificationsPage";
import ProfilePage from "./pages/profile/ProfilePage";
import EmergencyPage from "./pages/emergency/EmergencyPage";
import GriefSupportPage from "./pages/support/GriefSupportPage";
import MentalHealthPage from "./pages/support/MentalHealthPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify" element={<VerifyOTPPage />} />
      </Route>
      <Route
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/risk-assessment" element={<RiskAssessmentPage />} />
        <Route path="/risk-assessment/result/:id" element={<RiskResultPage />} />
        <Route path="/pregnancy" element={<PregnancyJourneyPage />} />
        <Route path="/telemedicine" element={<TelemedicinePage />} />
        <Route path="/telemedicine/room/:id" element={<ConsultationRoomPage />} />
        <Route path="/avatar" element={<AvatarChatPage />} />
        <Route path="/facilities" element={<FacilitiesMapPage />} />
        <Route path="/education" element={<EducationPage />} />
        <Route path="/health-records" element={<HealthRecordsPage />} />
        <Route path="/appointments" element={<AppointmentsPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/emergency" element={<EmergencyPage />} />
        <Route path="/grief-support" element={<GriefSupportPage />} />
        <Route path="/mental-health" element={<MentalHealthPage />} />
      </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
