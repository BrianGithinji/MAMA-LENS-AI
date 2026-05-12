import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { GoogleLogin } from "@react-oauth/google";
import { authAPI } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import { useTranslation } from "react-i18next";
import { LANGUAGES } from "../../i18n";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const { t } = useTranslation();
  const { register, handleSubmit } = useForm();

  const handleAuthSuccess = (data: any) => {
    login(
      { access_token: data.access_token, refresh_token: data.refresh_token },
      {
        id: data.user_id,
        first_name: data.first_name || "",
        last_name: data.last_name || "",
        role: data.role,
        preferred_language: data.preferred_language || "en",
        onboarding_completed: false,
      }
    );
  };

  const registerMutation = useMutation({
    mutationFn: (data: object) => authAPI.register(data),
    onSuccess: (response) => {
      handleAuthSuccess(response.data);
      toast.success("Welcome to MAMA-LENS AI! 💚");
      navigate("/dashboard");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t("error"));
    },
  });

  const googleMutation = useMutation({
    mutationFn: (credential: string) => authAPI.googleLogin(credential),
    onSuccess: (response) => {
      handleAuthSuccess(response.data);
      toast.success("Welcome to MAMA-LENS AI! 💚");
      navigate("/dashboard");
    },
    onError: () => toast.error(t("error")),
  });

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900">{t("create_account")}</h2>
      <p className="text-gray-500 text-sm mt-1">{t("tagline")}</p>

      <div className="mt-6 flex flex-col items-center gap-3">
        <GoogleLogin
          onSuccess={(cr) => cr.credential && googleMutation.mutate(cr.credential)}
          onError={() => toast.error(t("error"))}
          shape="rectangular" size="large" text="signup_with" logo_alignment="left"
        />
        {googleMutation.isPending && <p className="text-gray-400 text-xs">{t("creating_account")}</p>}
      </div>

      <div className="flex items-center gap-3 my-5">
        <div className="flex-1 h-px bg-gray-200" />
        <span className="text-gray-400 text-xs font-medium">or sign up with phone</span>
        <div className="flex-1 h-px bg-gray-200" />
      </div>

      <form onSubmit={handleSubmit((data) => registerMutation.mutate({ ...data, data_consent_given: true }))} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1.5">{t("first_name")}</label>
            <input {...register("first_name", { required: true })} placeholder="Jane"
              className="w-full px-4 py-3.5 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-300" />
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1.5">{t("last_name")}</label>
            <input {...register("last_name", { required: true })} placeholder="Doe"
              className="w-full px-4 py-3.5 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-300" />
          </div>
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-medium mb-1.5">{t("phone_number")}</label>
          <input {...register("phone_number", { required: true })} placeholder="+254 700 000 000"
            className="w-full px-4 py-3.5 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-300" />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-medium mb-1.5">{t("password")}</label>
          <input {...register("password", { required: true, minLength: 8 })} type="password" placeholder="Min. 8 characters"
            className="w-full px-4 py-3.5 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-300" />
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-medium mb-1.5">{t("preferred_language")}</label>
          <select {...register("preferred_language")}
            className="w-full px-4 py-3.5 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-300">
            {LANGUAGES.map(({ code, flag, nativeLabel, label }) => (
              <option key={code} value={code}>{flag} {nativeLabel} ({label})</option>
            ))}
          </select>
        </div>

        <div className="bg-warm-50 rounded-2xl p-4">
          <p className="text-gray-600 text-xs">
            By creating an account, you agree to our Terms of Service and Privacy Policy. Your health data is encrypted and protected.
          </p>
        </div>

        <button type="submit" disabled={registerMutation.isPending}
          className="w-full py-4 bg-primary-500 text-white font-bold rounded-2xl shadow-glow-primary disabled:opacity-60">
          {registerMutation.isPending ? t("creating_account") : t("create_account")}
        </button>
      </form>

      <p className="text-center text-gray-500 text-sm mt-6">
        {t("already_account")}{" "}
        <Link to="/login" className="text-primary-500 font-semibold">{t("sign_in")}</Link>
      </p>
    </div>
  );
}
