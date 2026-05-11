import { Outlet } from "react-router-dom";
import Logo from "../components/brand/Logo";

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 via-primary-600 to-earth-700 flex flex-col">
      <div className="flex items-center justify-center pt-10 pb-4">
        <div className="text-center">
          <div className="bg-white/95 backdrop-blur-sm rounded-3xl px-8 py-6 shadow-lg inline-block">
            <Logo variant="full" width={160} />
          </div>
        </div>
      </div>

      <div className="flex-1 bg-white rounded-t-[2.5rem] px-6 pt-8 pb-10 overflow-y-auto">
        <Outlet />
      </div>
    </div>
  );
}
