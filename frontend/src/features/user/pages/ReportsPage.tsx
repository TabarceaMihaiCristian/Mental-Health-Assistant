import { useEffect, useState } from "react";
import { BarChart3, RefreshCcw } from "lucide-react";
import { AppShell } from "../../../components/layout/AppShell";
import { Button } from "../../../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../components/ui/Card";
import { useAuth } from "../../../app/use-auth";
import { generateReport, getReport, listDailyMoodSummaries } from "../../reports/reportsApi";
import type { DailyMoodSummary, ReportResponse } from "../../../types/report";
import { formatDateOnly, toTitleCase } from "../../../lib/format";

export function ReportsPage() {
  const { token } = useAuth();
  const [dailySummaries, setDailySummaries] = useState<DailyMoodSummary[]>([]);
  const [weeklyReport, setWeeklyReport] = useState<ReportResponse | null>(null);
  const [monthlyReport, setMonthlyReport] = useState<ReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;

    void (async () => {
      setError(null);
      try {
        const summaries = await listDailyMoodSummaries(token);
        const [weekly, monthly] = await Promise.allSettled([getReport(token, "weekly"), getReport(token, "monthly")]);

        if (cancelled) {
          return;
        }

        setDailySummaries(summaries);
        setWeeklyReport(weekly.status === "fulfilled" ? weekly.value : null);
        setMonthlyReport(monthly.status === "fulfilled" ? monthly.value : null);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unable to load report data.");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function ensureReport(period: "weekly" | "monthly") {
    if (!token) return;
    const report = await generateReport(token, period);
    if (period === "weekly") setWeeklyReport(report);
    else setMonthlyReport(report);
  }

  return (
    <AppShell title="Reports" subtitle="Daily summaries and generated weekly/monthly reports are now backed by the real reporting endpoints.">
      {error ? <div className="rounded-[28px] border border-[--destructive] bg-[--red-100] px-5 py-4 text-sm">{error}</div> : null}
      <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Daily mood summaries</CardTitle>
            <CardDescription>Stored daily analysis summaries from the backend.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {dailySummaries.length === 0 ? <p className="text-sm text-[--muted-foreground]">No daily summaries yet.</p> : null}
            {dailySummaries.map((summary) => (
              <div key={summary.id} className="rounded-[20px] border border-[--border] p-4">
                <p className="font-semibold">{formatDateOnly(summary.summary_date)}</p>
                <p className="mt-1 text-sm text-[--muted-foreground]">{toTitleCase(summary.dominant_mood)} · risk {summary.risk}</p>
                <p className="mt-1 text-sm text-[--muted-foreground]">Intensity {summary.average_intensity.toFixed(1)}</p>
                {summary.summary_text ? <p className="mt-2 text-sm text-[--muted-foreground]">{summary.summary_text}</p> : null}
              </div>
            ))}
          </CardContent>
        </Card>

        {[{ key: "weekly", report: weeklyReport }, { key: "monthly", report: monthlyReport }].map(({ key, report }) => (
          <Card key={key}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <div>
                  <CardTitle>{toTitleCase(key)} report</CardTitle>
                  <CardDescription>{report ? `${formatDateOnly(report.period_start)} to ${formatDateOnly(report.period_end)}` : "Generate this report to view trends."}</CardDescription>
                </div>
                <Button variant="secondary" size="sm" onClick={() => void ensureReport(key as "weekly" | "monthly")}>
                  <RefreshCcw className="size-4" />
                  Generate
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {!report ? <p className="text-sm text-[--muted-foreground]">No generated report yet.</p> : null}
              {report ? (
                <>
                  <div className="rounded-[20px] bg-[--sand-100] p-4 text-sm text-[--foreground]">
                    <div className="flex items-center gap-2"><BarChart3 className="size-4 text-[--primary]" /> Days with data: {String(report.report_data.days_with_data ?? 0)}</div>
                    <p className="mt-2">Average intensity: {String(report.report_data.average_intensity ?? "n/a")}</p>
                    <p className="mt-2">Highest risk: {String(report.report_data.highest_risk ?? "n/a")}</p>
                  </div>
                  {Array.isArray(report.report_data.highlights) ? (
                    <ul className="grid gap-2 text-sm text-[--muted-foreground]">
                      {report.report_data.highlights.map((highlight, index) => (
                        <li key={index} className="rounded-[16px] border border-[--border] p-3">{highlight}</li>
                      ))}
                    </ul>
                  ) : null}
                  {typeof report.report_data.generated_summary === "string" ? <p className="text-sm text-[--muted-foreground]">{report.report_data.generated_summary}</p> : null}
                </>
              ) : null}
            </CardContent>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
