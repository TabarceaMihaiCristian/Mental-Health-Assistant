import type { ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./Card";

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-[--muted-foreground]">{description}</p>
        {action}
      </CardContent>
    </Card>
  );
}
