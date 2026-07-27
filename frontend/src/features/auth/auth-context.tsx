import * as React from "react";

import { fetchCurrentUser } from "@/features/auth/api";
import { clearTokens, getAccessToken, setTokens } from "@/lib/auth-storage";
import type { TokenResponse, User } from "@/types/api";

interface AuthContextState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signIn: (tokens: TokenResponse) => Promise<void>;
  signOut: () => void;
}

const AuthContext = React.createContext<AuthContextState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<User | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const loadUser = React.useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void loadUser();
  }, [loadUser]);

  const signIn = React.useCallback(
    async (tokens: TokenResponse) => {
      setTokens(tokens.access_token, tokens.refresh_token);
      await loadUser();
    },
    [loadUser],
  );

  const signOut = React.useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: Boolean(user), signIn, signOut }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
