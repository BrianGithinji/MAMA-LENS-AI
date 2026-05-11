import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone_number?: string;
  role: string;
  preferred_language: string;
  country?: string;
  onboarding_completed: boolean;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;

  login: (tokens: { access_token: string; refresh_token: string }, user: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  setTokens: (access_token: string, refresh_token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null,

      login: (tokens, user) =>
        set({
          isAuthenticated: true,
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
        }),

      logout: () =>
        set({
          isAuthenticated: false,
          user: null,
          accessToken: null,
          refreshToken: null,
        }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),

      setTokens: (access_token, refresh_token) =>
        set({ accessToken: access_token, refreshToken: refresh_token }),
    }),
    {
      name: "mamalens-auth",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
