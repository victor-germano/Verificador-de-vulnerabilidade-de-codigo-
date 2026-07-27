import { Slot } from "@radix-ui/react-slot";
import { type VariantProps, cva } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center justify-center gap-1 rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        outline: "border-border text-foreground",
        destructive: "border-transparent bg-destructive text-destructive-foreground",
        critical: "border-transparent bg-severity-critical/15 text-severity-critical",
        high: "border-transparent bg-severity-high/15 text-severity-high",
        medium: "border-transparent bg-severity-medium/20 text-severity-medium",
        low: "border-transparent bg-severity-low/15 text-severity-low",
        info: "border-transparent bg-severity-info/15 text-severity-info",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

interface BadgeProps extends React.ComponentProps<"span">, VariantProps<typeof badgeVariants> {
  asChild?: boolean;
}

function Badge({ className, variant, asChild = false, ...props }: BadgeProps) {
  const Comp = asChild ? Slot : "span";
  return (
    <Comp data-slot="badge" className={cn(badgeVariants({ variant, className }))} {...props} />
  );
}

export { Badge, badgeVariants };
