import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Toaster } from "sonner";

import App from "@/App.tsx";
import { AuthProvider } from "@/features/auth/auth-context";
import "@/index.css";
import { queryClient } from "@/lib/query-client";
import { ThemeProvider } from "@/lib/theme-provider";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <App />
          <Toaster theme="system" richColors position="top-right" />
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
);
