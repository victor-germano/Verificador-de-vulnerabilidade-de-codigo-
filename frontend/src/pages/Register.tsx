import { zodResolver } from "@hookform/resolvers/zod";
import axios from "axios";
import * as React from "react";
import { useForm } from "react-hook-form";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { z } from "zod";

import { ShieldCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { login as loginRequest, register as registerRequest } from "@/features/auth/api";
import { useAuth } from "@/features/auth/auth-context";

const schema = z.object({
  fullName: z.string().min(1, "Informe seu nome"),
  email: z.string().email("Informe um e-mail válido"),
  password: z.string().min(8, "A senha precisa ter no mínimo 8 caracteres"),
});

type FormValues = z.infer<typeof schema>;

export default function RegisterPage() {
  const { isAuthenticated, signIn } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = React.useState<string | null>(null);

  const {
    register: registerField,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  if (isAuthenticated) return <Navigate to="/" replace />;

  const onSubmit = async (values: FormValues) => {
    setServerError(null);
    try {
      await registerRequest(values.email, values.password, values.fullName);
      const tokens = await loginRequest(values.email, values.password);
      await signIn(tokens);
      navigate("/", { replace: true });
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 409) {
        setServerError("Já existe uma conta com este e-mail.");
      } else {
        setServerError("Não foi possível criar a conta. Tente novamente.");
      }
    }
  };

  return (
    <div className="flex min-h-svh items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="items-center text-center">
          <ShieldCheck className="mb-1 size-8 text-primary" />
          <CardTitle className="text-base text-foreground">Criar conta</CardTitle>
          <CardDescription>Comece a analisar seus projetos em minutos</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="fullName">Nome</Label>
              <Input id="fullName" autoComplete="name" {...registerField("fullName")} />
              {errors.fullName && (
                <p className="text-xs text-destructive">{errors.fullName.message}</p>
              )}
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">E-mail</Label>
              <Input id="email" type="email" autoComplete="email" {...registerField("email")} />
              {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                {...registerField("password")}
              />
              {errors.password && (
                <p className="text-xs text-destructive">{errors.password.message}</p>
              )}
            </div>
            {serverError && <p className="text-xs text-destructive">{serverError}</p>}
            <Button type="submit" disabled={isSubmitting} className="mt-1">
              {isSubmitting ? "Criando conta…" : "Criar conta"}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            Já tem conta?{" "}
            <Link to="/login" className="font-medium text-primary hover:underline">
              Entrar
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
