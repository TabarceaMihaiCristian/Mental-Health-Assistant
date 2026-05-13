import { apiRequest } from "../../lib/api";
import type { DailyMoodSummary, ReportResponse } from "../../types/report";

export function listDailyMoodSummaries(token: string) {
  return apiRequest<DailyMoodSummary[]>("/reports/daily-summaries", { method: "GET", token });
}

export function getReport(token: string, period: "weekly" | "monthly") {
  return apiRequest<ReportResponse>(`/reports/${period}`, { method: "GET", token });
}

export function generateReport(token: string, period: "weekly" | "monthly") {
  return apiRequest<ReportResponse>(`/reports/${period}`, { method: "POST", token });
}
