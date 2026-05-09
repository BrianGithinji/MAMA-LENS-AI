/**
 * MAMA-LENS AI — OTP Verification Page
 */
import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { authAPI, userAPI } from "../../api/client";
import { useAuthStore } from "../../store/authStore";

export default function VerifyOTPPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuthStore();
  const [otp, setOtp] = useState("");
  const identifier = location.state?.identifier || "";

  const verifyMutation = useMutation({
    mutationFn: () => authAPI.verifyOTP({ identifier, otp, otp_type: identifier.includes("@") ? "email" : "phone" }),
    onSuccess: async (response) => {
      const tokens = response.data;
      const profileResponse = await userAPI.getProfile();
      login(tokens, profileResponse.data);
      toast.success("Account verified! Welcome to MAMA-LENS 💚");
      navigate("/dashboard");
    },
    onError: () => toast.error("Invalid OTP. Please try again."),
  });

  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-primary-100 rounded-3xl flex items-center justify-center mx-auto mb-4">
        <span className="text-3xl">📱</span>
      </div>
      <h2 className="text-2xl font-bold text-gray-900">Verify your number</h2>
      <p className="text-gray-500 text-sm mt-2">
        Enter the 6-digit code sent to<br />
        <span className="font-medium text-gray-700">{identifier}</span>
      </p>

      <div className="mt-8">
        <input
          type="number"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          placeholder="000000"
          maxLength={6}
          className="w-full text-center text-3xl font-bold tracking-widest px-4 py-4 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-primary-400"
        />
      </div>

      <button
        onClick={() => verifyMutation.mutate()}
        disabled={otp.length !== 6 || verifyMutation.isPending}
        className="w-full mt-6 py-4 bg-primary-500 text-white font-bold rounded-2xl disabled:opacity-60"
      >
        {verifyMutation.isPending ? "Verifying..." : "Verify"}
      </button>

      <button
        onClick={() => authAPI.requestOTP(identifier).then(() => toast.success("New OTP sent!"))}
        className="mt-4 text-primary-500 text-sm font-medium"
      >
        Resend code
      </button>
    </div>
  );
}
