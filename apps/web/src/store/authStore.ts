import { create } from "zustand";
import { persist } from "zustand/middleware";
import i18n from "../i18n";

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
  language: string;

  login: (tokens: { access_token: string; refresh_token: string }, user: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  setTokens: (access_token: string, refresh_token: string) => void;
  setLanguage: (lang: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      accessToken: null,
      refreshToken: null,
      language: "en",

      login: (tokens, user) => {
        const lang = user.preferred_language || "en";
        i18n.changeLanguage(lang);
        set({
          isAuthenticated: true,
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          language: lang,
        });
      },

      logout: () =>
        set({
          isAuthenticated: false,
          user: null,
          accessToken: null,
          refreshToken: null,
          language: "en",
        }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),

      setTokens: (access_token, refresh_token) =>
        set({ accessToken: access_token, refreshToken: refresh_token }),

      setLanguage: (lang: string) => {
        i18n.changeLanguage(lang);
        set((state) => ({
          language: lang,
          user: state.user ? { ...state.user, preferred_language: lang } : null,
        }));
      },
    }),
    {
      name: "mamalens-auth",
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        language: state.language,
      }),
      onRehydrateStorage: () => (state) => {
        if (state?.language) i18n.changeLanguage(state.language);
      },
    }
  )
);
