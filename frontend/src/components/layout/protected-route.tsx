import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "@/features/auth/auth-context";

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex h-svh items-center justify-center text-sm text-muted-foreground">Carregando…</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
