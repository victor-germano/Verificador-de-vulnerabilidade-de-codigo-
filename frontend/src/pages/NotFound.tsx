import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-3 text-center">
      <p className="text-4xl font-semibold tracking-tight">404</p>
      <p className="text-sm text-muted-foreground">Página não encontrada.</p>
      <Button asChild size="sm">
        <Link to="/">Voltar ao início</Link>
      </Button>
    </div>
  );
}
