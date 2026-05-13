import { AppShell } from "../../../components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/Card";

export function PlaceholderPage({ title, subtitle, note }: { title: string; subtitle: string; note: string }) {
  return (
    <AppShell title={title} subtitle={subtitle}>
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-[--muted-foreground]">{note}</p>
        </CardContent>
      </Card>
    </AppShell>
  );
}
