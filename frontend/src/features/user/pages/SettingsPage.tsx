
import { useEffect, useState } from "react";
import { useAuth } from "../../../app/use-auth";
import { AppShell } from "../../../components/layout/AppShell";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { TextField, TextareaField } from "../../../components/ui/Fields";
import type { User } from "../../../types/auth";
import { changeCurrentUserPassword, getCurrentUserAccount, updateCurrentUserProfile } from "../userApi";

function readPreferredActivities(user: User | null) {
  return (user?.profile?.preferred_activities ?? []).join(", ");
}

export function SettingsPage() {
  const { token, user, logout, refreshUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [ageRange, setAgeRange] = useState(user?.profile?.age_range ?? "");
  const [occupation, setOccupation] = useState(user?.profile?.occupation ?? "");
  const [goals, setGoals] = useState(user?.profile?.goals ?? "");
  const [preferredActivities, setPreferredActivities] = useState(readPreferredActivities(user));
  const [timezone, setTimezone] = useState(user?.profile?.timezone ?? "Europe/Bucharest");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  function applyUserToForm(nextUser: User) {
    setFullName(nextUser.full_name ?? "");
    setAgeRange(nextUser.profile?.age_range ?? "");
    setOccupation(nextUser.profile?.occupation ?? "");
    setGoals(nextUser.profile?.goals ?? "");
    setPreferredActivities((nextUser.profile?.preferred_activities ?? []).join(", "));
    setTimezone(nextUser.profile?.timezone ?? "Europe/Bucharest");
  }

  useEffect(() => {
    if (!token) {
      return;
    }
    let cancelled = false;
    void getCurrentUserAccount(token)
      .then(async (nextUser) => {
        if (cancelled) {
          return;
        }
        applyUserToForm(nextUser);
        await refreshUser();
      })
      .catch(() => undefined);

    return () => {
      cancelled = true;
    };
  }, [refreshUser, token]);

  async function handleSaveProfile() {
    if (!token) return;
    setSavingProfile(true);
    setError(null);
    setMessage(null);
    try {
      const updatedUser = await updateCurrentUserProfile(token, {
        full_name: fullName,
        age_range: ageRange || null,
        occupation: occupation || null,
        goals: goals || null,
        preferred_activities: preferredActivities.split(",").map((item) => item.trim()).filter(Boolean),
        timezone,
      });
      applyUserToForm(updatedUser);
      await refreshUser();
      setMessage("Profile updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update profile.");
    } finally {
      setSavingProfile(false);
    }
  }

  async function handleChangePassword() {
    if (!token) return;
    if (newPassword !== confirmPassword) {
      setError("New password and confirmation do not match.");
      return;
    }
    setSavingPassword(true);
    setError(null);
    setMessage(null);
    try {
      await changeCurrentUserPassword(token, {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setMessage("Password updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to change password.");
    } finally {
      setSavingPassword(false);
    }
  }

  return (
    <AppShell title="Settings" subtitle="Update your live account profile and local password from here.">
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      {message ? <div className="rounded-[28px] border border-[--teal-200] bg-[--teal-50] px-5 py-4 text-sm">{message}</div> : null}
      <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Account profile</CardTitle>
            <CardDescription>Manage your personal profile details and support preferences.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4">
            <TextField label="Full name" value={fullName} onChange={(event) => setFullName(event.target.value)} />
            <TextField label="Email" value={user?.email ?? ""} disabled />
            <TextField label="Age range" value={ageRange} onChange={(event) => setAgeRange(event.target.value)} />
            <TextField label="Occupation" value={occupation} onChange={(event) => setOccupation(event.target.value)} />
            <TextField label="Timezone" value={timezone} onChange={(event) => setTimezone(event.target.value)} />
            <TextField label="Preferred activities" value={preferredActivities} onChange={(event) => setPreferredActivities(event.target.value)} placeholder="Walking, journaling, meditation" />
            <TextareaField label="Goals" value={goals} onChange={(event) => setGoals(event.target.value)} />
            <Button onClick={() => void handleSaveProfile()} disabled={savingProfile}>{savingProfile ? "Saving..." : "Save profile"}</Button>
          </CardContent>
        </Card>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Password</CardTitle>
              <CardDescription>Change the password for your local account.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <TextField label="Current password" type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} />
              <TextField label="New password" type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} />
              <TextField label="Confirm new password" type="password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} />
              <Button onClick={() => void handleChangePassword()} disabled={savingPassword}>{savingPassword ? "Updating..." : "Update password"}</Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Session</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-[--muted-foreground]">
              <p>Use logout to clear the current authenticated workspace on this device.</p>
              <Button variant="ghost" onClick={logout}>Logout</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
