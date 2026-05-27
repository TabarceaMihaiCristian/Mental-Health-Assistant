import { useEffect, useMemo, useState } from "react";
import { MapPin, Star, Video } from "lucide-react";
import { useAuth } from "../../../app/use-auth";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { ButtonLink } from "../../../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/Card";
import { EmptyState } from "../../../components/ui/EmptyState";
import { TextField } from "../../../components/ui/Fields";
import { listSpecialists } from "../specialistsApi";
import type { Specialist } from "../../../types/specialist";

export function SpecialistsListPage() {
  const { token } = useAuth();
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const items = await listSpecialists(token);
        if (!cancelled) {
          setSpecialists(items);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load specialists.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return specialists;
    }

    return specialists.filter((item) =>
      [item.full_name, item.specialty, item.city ?? "", ...(item.consultation_modes ?? [])]
        .join(" ")
        .toLowerCase()
        .includes(normalized),
    );
  }, [query, specialists]);

  return (
    <AppShell title="Active specialists" subtitle="Explore available specialists and find the right fit for your next conversation.">
      <div className="max-w-xl">
        <TextField label="Search directory" type="search" placeholder="Search by name, specialty, city, or consultation mode" value={query} onChange={(event) => setQuery(event.target.value)} />
      </div>

      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      {loading ? <div className="rounded-[28px] border border-[--border] bg-white px-5 py-8 text-sm text-[--muted-foreground] shadow-[var(--shadow-sm)]">Loading specialist directory...</div> : null}

      {!loading && filtered.length === 0 ? (
        <EmptyState
          title={specialists.length === 0 ? "No specialists available" : "No specialists match your filters"}
          description={specialists.length === 0 ? "No specialists are available right now. Please check back soon." : "Try a broader query or clear the current search term."}
        />
      ) : null}

      <div className="grid gap-6 xl:grid-cols-2">
        {filtered.map((specialist) => (
          <Card key={specialist.id} className="flex h-full flex-col">
            <CardHeader>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <CardTitle>{specialist.full_name}</CardTitle>
                  <p className="mt-2 text-sm text-[--muted-foreground]">{specialist.specialty}</p>
                </div>
                <Badge variant="success">{specialist.status}</Badge>
              </div>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col gap-5">
              <p className="text-sm leading-7 text-[--muted-foreground]">{specialist.bio ?? "Profile details are available, but this specialist has not added a bio yet."}</p>
              <div className="grid gap-3 text-sm text-[--muted-foreground] md:grid-cols-2">
                <div className="flex items-center gap-2"><MapPin className="size-4 text-[--primary]" /> {specialist.city ?? "City not set"}</div>
                <div className="flex items-center gap-2"><Star className="size-4 text-[--amber-700]" /> {specialist.average_rating?.toFixed(1) ?? "No rating yet"} ({specialist.review_count} reviews)</div>
                <div className="flex items-center gap-2 md:col-span-2"><Video className="size-4 text-[--primary]" /> {(specialist.consultation_modes ?? []).join(", ") || "Consultation modes not set"}</div>
              </div>
              <ButtonLink to={`/specialists/${specialist.id}`} size="md" className="mt-auto self-start">View specialist profile</ButtonLink>
            </CardContent>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
