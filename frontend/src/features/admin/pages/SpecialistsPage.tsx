import { useEffect, useMemo, useState } from "react";
import { Plus, RefreshCw, Search } from "lucide-react";
import { useAuth } from "../../../app/use-auth";
import { AppShell } from "../../../components/layout/AppShell";
import { Badge } from "../../../components/ui/Badge";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { SelectField, TextField, TextareaField } from "../../../components/ui/Fields";
import { toTitleCase } from "../../../lib/format";
import type { AdminSpecialist } from "../../../types/admin";
import {
  createAdminSpecialist,
  listAdminSpecialists,
  updateAdminSpecialist,
  updateAdminSpecialistStatus,
} from "../adminApi";

function parseModes(value: string) {
  return value.split(",").map((item) => item.trim().toLowerCase()).filter(Boolean);
}

function badgeVariant(status: string) {
  return status === "active" ? "success" : "danger";
}

export function AdminSpecialistsPage() {
  const { token } = useAuth();
  const [specialists, setSpecialists] = useState<AdminSpecialist[]>([]);
  const [selectedSpecialistId, setSelectedSpecialistId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [statusTargetId, setStatusTargetId] = useState<string | null>(null);
  const [directorySearch, setDirectorySearch] = useState("");
  const [directoryStatus, setDirectoryStatus] = useState<"" | "active" | "inactive">("");
  const [directoryCity, setDirectoryCity] = useState("");

  const [createEmail, setCreateEmail] = useState("");
  const [createPassword, setCreatePassword] = useState("");
  const [createFullName, setCreateFullName] = useState("");
  const [createSpecialty, setCreateSpecialty] = useState("");
  const [createBio, setCreateBio] = useState("");
  const [createModes, setCreateModes] = useState("online, onsite");
  const [createCity, setCreateCity] = useState("");

  const [editFullName, setEditFullName] = useState("");
  const [editSpecialty, setEditSpecialty] = useState("");
  const [editBio, setEditBio] = useState("");
  const [editModes, setEditModes] = useState("");
  const [editCity, setEditCity] = useState("");

  const selectedSpecialist = useMemo(
    () => specialists.find((item) => item.id === selectedSpecialistId) ?? null,
    [selectedSpecialistId, specialists],
  );

  const filteredSpecialists = useMemo(() => {
    const search = directorySearch.trim().toLowerCase();
    const city = directoryCity.trim().toLowerCase();

    return specialists.filter((specialist) => {
      const matchesSearch =
        search.length === 0
        || specialist.full_name.toLowerCase().includes(search)
        || specialist.specialty.toLowerCase().includes(search)
        || (specialist.email ?? "").toLowerCase().includes(search);
      const matchesStatus = directoryStatus.length === 0 || specialist.status === directoryStatus;
      const matchesCity = city.length === 0 || (specialist.city ?? "").toLowerCase().includes(city);
      return matchesSearch && matchesStatus && matchesCity;
    });
  }, [directoryCity, directorySearch, directoryStatus, specialists]);

  function applySelectedSpecialist(specialist: AdminSpecialist | null) {
    setSelectedSpecialistId(specialist?.id ?? null);
    setEditFullName(specialist?.full_name ?? "");
    setEditSpecialty(specialist?.specialty ?? "");
    setEditBio(specialist?.bio ?? "");
    setEditModes(specialist?.consultation_modes.join(", ") ?? "");
    setEditCity(specialist?.city ?? "");
  }

  async function loadSpecialists(focusSpecialistId?: string | null) {
    if (!token) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const payload = await listAdminSpecialists(token);
      setSpecialists(payload.items);
      const nextSelected = payload.items.find((item) => item.id === (focusSpecialistId ?? selectedSpecialistId))
        ?? payload.items[0]
        ?? null;
      applySelectedSpecialist(nextSelected);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load specialists.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    void listAdminSpecialists(token)
      .then((payload) => {
        setSpecialists(payload.items);
        applySelectedSpecialist(payload.items[0] ?? null);
      })
      .catch((err: Error) => setError(err.message));
  }, [token]);

  async function handleCreateSpecialist() {
    if (!token) {
      return;
    }
    setCreating(true);
    setError(null);
    setMessage(null);
    try {
      const specialist = await createAdminSpecialist(token, {
        email: createEmail,
        password: createPassword,
        full_name: createFullName,
        specialty: createSpecialty,
        bio: createBio || null,
        consultation_modes: parseModes(createModes),
        city: createCity || null,
      });
      setCreateEmail("");
      setCreatePassword("");
      setCreateFullName("");
      setCreateSpecialty("");
      setCreateBio("");
      setCreateModes("online, onsite");
      setCreateCity("");
      setMessage(`Created specialist account for ${specialist.full_name}.`);
      await loadSpecialists(specialist.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create specialist.");
    } finally {
      setCreating(false);
    }
  }

  async function handleUpdateSpecialist() {
    if (!token || !selectedSpecialist) {
      return;
    }
    setUpdating(true);
    setError(null);
    setMessage(null);
    try {
      await updateAdminSpecialist(token, selectedSpecialist.id, {
        full_name: editFullName,
        specialty: editSpecialty,
        bio: editBio || null,
        consultation_modes: parseModes(editModes),
        city: editCity || null,
      });
      setMessage(`Updated ${selectedSpecialist.full_name}.`);
      await loadSpecialists(selectedSpecialist.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update specialist.");
    } finally {
      setUpdating(false);
    }
  }

  async function handleToggleStatus(specialist: AdminSpecialist) {
    if (!token) {
      return;
    }
    setStatusTargetId(specialist.id);
    setError(null);
    setMessage(null);
    try {
      const nextStatus = specialist.status === "active" ? "inactive" : "active";
      await updateAdminSpecialistStatus(token, specialist.id, { status: nextStatus });
      setMessage(`${specialist.full_name} is now ${nextStatus}.`);
      await loadSpecialists(specialist.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update specialist status.");
    } finally {
      setStatusTargetId(null);
    }
  }

  return (
    <AppShell
      role="admin"
      title="Specialist management"
      subtitle="Create specialist accounts, update directory details, and control public visibility."
      actions={<Button variant="ghost" onClick={() => void loadSpecialists(selectedSpecialistId)}><RefreshCw className="size-4" /> Refresh</Button>}
    >
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      {message ? <div className="rounded-[28px] border border-[--teal-200] bg-[--teal-50] px-5 py-4 text-sm">{message}</div> : null}
      <div className="grid gap-6 xl:grid-cols-[1.1fr_1.1fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Onboard specialist</CardTitle>
            <CardDescription>Create a real specialist account and linked directory profile.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <TextField label="Full name" value={createFullName} onChange={(event) => setCreateFullName(event.target.value)} />
            <TextField label="Email" type="email" value={createEmail} onChange={(event) => setCreateEmail(event.target.value)} />
            <TextField label="Password" type="password" value={createPassword} onChange={(event) => setCreatePassword(event.target.value)} />
            <TextField label="Specialty" value={createSpecialty} onChange={(event) => setCreateSpecialty(event.target.value)} />
            <TextField label="Consultation modes" value={createModes} onChange={(event) => setCreateModes(event.target.value)} helpText="Comma-separated, e.g. online, onsite" />
            <TextField label="City" value={createCity} onChange={(event) => setCreateCity(event.target.value)} />
            <TextareaField label="Bio" value={createBio} onChange={(event) => setCreateBio(event.target.value)} />
            <Button onClick={() => void handleCreateSpecialist()} disabled={creating}><Plus className="size-4" /> {creating ? "Creating..." : "Create specialist"}</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Edit selected specialist</CardTitle>
            <CardDescription>Update profile details for the specialist currently selected from the list.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            {!selectedSpecialist ? <p className="text-sm text-[--muted-foreground]">Select a specialist from the filtered directory to edit.</p> : null}
            {selectedSpecialist ? (
              <>
                <TextField label="Email" value={selectedSpecialist.email ?? ""} disabled />
                <TextField label="Full name" value={editFullName} onChange={(event) => setEditFullName(event.target.value)} />
                <TextField label="Specialty" value={editSpecialty} onChange={(event) => setEditSpecialty(event.target.value)} />
                <TextField label="Consultation modes" value={editModes} onChange={(event) => setEditModes(event.target.value)} helpText="Comma-separated, e.g. online, onsite" />
                <TextField label="City" value={editCity} onChange={(event) => setEditCity(event.target.value)} />
                <TextareaField label="Bio" value={editBio} onChange={(event) => setEditBio(event.target.value)} />
                <Button onClick={() => void handleUpdateSpecialist()} disabled={updating}>{updating ? "Saving..." : "Save specialist"}</Button>
              </>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Current directory</CardTitle>
            <CardDescription>{loading ? "Loading specialist records..." : `Showing ${filteredSpecialists.length} of ${specialists.length} specialist records.`}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 rounded-[22px] border border-[--border] bg-[--sand-50] p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-[--foreground]">
                <Search className="size-4 text-[--primary]" /> Filter directory records
              </div>
              <TextField
                label="Search by name, specialty, or email"
                value={directorySearch}
                onChange={(event) => setDirectorySearch(event.target.value)}
                placeholder="Ana Pavel, CBT, specialist@example.com"
              />
              <div className="grid gap-4 md:grid-cols-2">
                <SelectField label="Status" value={directoryStatus} onChange={(event) => setDirectoryStatus(event.target.value as "" | "active" | "inactive") }>
                  <option value="">All statuses</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </SelectField>
                <TextField
                  label="City"
                  value={directoryCity}
                  onChange={(event) => setDirectoryCity(event.target.value)}
                  placeholder="Bucharest"
                />
              </div>
            </div>
            {!loading && filteredSpecialists.length === 0 ? <p className="text-sm text-[--muted-foreground]">No specialists matched the current filters.</p> : null}
            {filteredSpecialists.map((specialist) => (
              <div key={specialist.id} className="rounded-[22px] border border-[--border] p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold tracking-[-0.02em]">{specialist.full_name}</p>
                    <p className="mt-1 text-sm text-[--muted-foreground]">{specialist.specialty}</p>
                    <p className="mt-1 text-sm text-[--muted-foreground]">{specialist.city ?? "City not set"} · {specialist.email ?? "No email"}</p>
                  </div>
                  <Badge variant={badgeVariant(specialist.status)}>{toTitleCase(specialist.status)}</Badge>
                </div>
                <p className="mt-3 text-sm text-[--muted-foreground]">Modes: {specialist.consultation_modes.join(", ")} · Reviews: {specialist.review_count}</p>
                <div className="mt-4 flex flex-wrap gap-3">
                  <Button variant="secondary" size="sm" onClick={() => applySelectedSpecialist(specialist)}>Edit</Button>
                  <Button
                    variant={specialist.status === "active" ? "danger" : "success"}
                    size="sm"
                    onClick={() => void handleToggleStatus(specialist)}
                    disabled={statusTargetId === specialist.id}
                  >
                    {statusTargetId === specialist.id ? "Updating..." : specialist.status === "active" ? "Deactivate" : "Activate"}
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
