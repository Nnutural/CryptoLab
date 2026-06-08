import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import { login as apiLogin, register as apiRegister, logout as apiLogout, getMe } from "@/api/auth";

interface AuthState {
  token: string | null;
  username: string | null;
  userId: number | null;
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(() => {
    const token = localStorage.getItem("cryptolab.jwt");
    const username = localStorage.getItem("cryptolab.username");
    const userId = localStorage.getItem("cryptolab.userId");
    return {
      token,
      username,
      userId: userId ? Number(userId) : null,
    };
  });

  const login = useCallback(async (username: string, password: string) => {
    const resp = await apiLogin(username, password);
    if (resp.code === 1000 && resp.data) {
      localStorage.setItem("cryptolab.jwt", resp.data.access_token);
      localStorage.setItem("cryptolab.username", username);
      setState({ token: resp.data.access_token, username, userId: null });
    } else {
      throw new Error(resp.message || "登录失败");
    }
  }, []);

  const register = useCallback(async (username: string, password: string) => {
    const resp = await apiRegister(username, password);
    if (resp.code === 1000 && resp.data) {
      localStorage.setItem("cryptolab.userId", String(resp.data.user_id));
    } else {
      throw new Error(resp.message || "注册失败");
    }
  }, []);

  const logout = useCallback(async () => {
    try { await apiLogout(); } catch { /* ignore */ }
    localStorage.removeItem("cryptolab.jwt");
    localStorage.removeItem("cryptolab.username");
    localStorage.removeItem("cryptolab.userId");
    setState({ token: null, username: null, userId: null });
  }, []);

  const fetchMe = useCallback(async () => {
    try {
      const resp = await getMe();
      if (resp.code === 1000 && resp.data) {
        setState((s) => ({
          ...s,
          username: resp.data.username,
          userId: resp.data.user_id,
        }));
        localStorage.setItem("cryptolab.username", resp.data.username);
        localStorage.setItem("cryptolab.userId", String(resp.data.user_id));
      }
    } catch { /* ignore */ }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        fetchMe,
        isAuthenticated: !!state.token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
