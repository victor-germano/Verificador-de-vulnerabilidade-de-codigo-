import { Suspense, lazy } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "@/components/layout/app-shell";
import { ProtectedRoute } from "@/components/layout/protected-route";

const DashboardPage = lazy(() => import("@/pages/Dashboard"));
const FindingsPage = lazy(() => import("@/pages/Findings"));
const LoginPage = lazy(() => import("@/pages/Login"));
const NotFoundPage = lazy(() => import("@/pages/NotFound"));
const ProjectDetailPage = lazy(() => import("@/pages/ProjectDetail"));
const ProjectsPage = lazy(() => import("@/pages/Projects"));
const RegisterPage = lazy(() => import("@/pages/Register"));

function RouteFallback() {
  return (
    <div className="flex h-svh items-center justify-center text-sm text-muted-foreground">
      Carregando…
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<RouteFallback />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppShell />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
              <Route path="/findings" element={<FindingsPage />} />
            </Route>
          </Route>

          <Route path="/404" element={<NotFoundPage />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
