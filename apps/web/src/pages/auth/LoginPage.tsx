import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { Eye, EyeOff, Phone } from "lucide-react";
import { GoogleLogin } from "@react-oauth/google";
import { authAPI } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import aphrcLogo from "../../assets/aphrc.png";

interface LoginForm {
  identifier: string;
  password: string;
}

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

  const handleAuthSuccess = (data: any) => {
    login(
      { access_token: data.access_token, refresh_token: data.refresh_token },
      {
        id: data.user_id,
        first_name: data.first_name || "",
        last_name: data.last_name || "",
        role: data.role,
        preferred_language: "en",
        onboarding_completed: false,
      }
    );
  };

  const loginMutation = useMutation({
    mutationFn: (data: LoginForm) => authAPI.login(data),
    onSuccess: (response) => {
      handleAuthSuccess(response.data);
      toast.success("Welcome back!");
      navigate("/dashboard");
    },
    onError: (error: any) => {
      const msg =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Invalid credentials. Please check your phone number and password.";
      toast.error(msg);
    },
  });

  const googleMutation = useMutation({
    mutationFn: (credential: string) => authAPI.googleLogin(credential),
    onSuccess: (response) => {
      handleAuthSuccess(response.data);
      toast.success("Welcome!");
      navigate("/dashboard");
    },
    onError: () => toast.error("Google sign-in failed. Please try again."),
  });

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900">Welcome back</h2>
      <p className="text-gray-500 text-sm mt-1">Sign in to your MAMA-LENS account</p>

      <div className="mt-6 flex flex-col items-center gap-3">
        <GoogleLogin
          onSuccess={(credentialResponse) => {
            if (credentialResponse.credential) {
              googleMutation.mutate(credentialResponse.credential);
            }
          }}
          onError={() => toast.error("Google sign-in failed.")}
          useOneTap
          shape="rectangular"
          size="large"
          text="signin_with"
          logo_alignment="left"
        />
        {googleMutation.isPending && (
          <p className="text-gray-400 text-xs">Signing in with Google...</p>
        )}
      </div>

      <div className="flex items-center gap-3 my-5">
        <div className="flex-1 h-px bg-gray-200" />
        <span className="text-gray-400 text-xs font-medium">or sign in with phone</span>
        <div className="flex-1 h-px bg-gray-200" />
      </div>

      <form onSubmit={handleSubmit((data) => loginMutation.mutate(data))} className="space-y-4">
        <div>
          <label className="block text-gray-700 text-sm font-medium mb-1.5">
            Phone number or email
          </label>
          <div className="relative">
            <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              {...register("identifier", { required: "Phone or email is required" })}
              type="text"
              placeholder="+254 700 000 000 or email"
              className="w-full pl-10 pr-4 py-3.5 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-300 focus:border-transparent"
            />
          </div>
          {errors.identifier && (
            <p className="text-emergency-500 text-xs mt-1">{errors.identifier.message}</p>
          )}
        </div>

        <div>
          <label className="block text-gray-700 text-sm font-medium mb-1.5">Password</label>
          <div className="relative">
            <input
              {...register("password", { required: "Password is required" })}
              type={showPassword ? "text" : "password"}
              placeholder="Your password"
              className="w-full px-4 py-3.5 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-300 focus:border-transparent pr-12"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          {errors.password && (
            <p className="text-emergency-500 text-xs mt-1">{errors.password.message}</p>
          )}
        </div>

        <div className="flex justify-end">
          <Link to="/forgot-password" className="text-primary-500 text-sm font-medium">
            Forgot password?
          </Link>
        </div>

        <button
          type="submit"
          disabled={loginMutation.isPending}
          className="w-full py-4 bg-primary-500 text-white font-bold rounded-2xl shadow-glow-primary disabled:opacity-60 transition-all active:scale-95"
        >
          {loginMutation.isPending ? "Signing in..." : "Sign In"}
        </button>
      </form>

      <p className="text-center text-gray-500 text-sm mt-6">
        Don't have an account?{" "}
        <Link to="/register" className="text-primary-500 font-semibold">
          Create account
        </Link>
      </p>

      <div className="mt-6 p-4 bg-calm-50 rounded-2xl">
        <p className="text-calm-700 text-xs text-center">
          Your health data is encrypted and protected. We never share your information without consent.
        </p>
        <div className="flex items-center justify-center gap-3 mt-3 pt-3 border-t border-calm-200">
          <span className="text-gray-500 text-xs whitespace-nowrap">Developed in collaboration with</span>
          <div className="bg-white border border-gray-200 rounded-lg p-1.5 flex items-center justify-center">
            <img
              src={aphrcLogo}
              alt="APHRC — African Population and Health Research Center"
              className="h-8 w-auto object-contain block"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
