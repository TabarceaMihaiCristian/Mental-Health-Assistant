export interface DailyMoodSummary {
  id: string;
  user_id: string;
  summary_date: string;
  dominant_mood: string;
  average_intensity: number;
  risk: string;
  summary_text: string | null;
  created_at: string;
}

export interface ReportData {
  days_with_data?: number;
  average_intensity?: number;
  highest_risk?: string;
  dominant_mood_distribution?: Record<string, number>;
  risk_distribution?: Record<string, number>;
  highlights?: string[];
  generated_summary?: string;
  [key: string]: unknown;
}

export interface ReportResponse {
  id: string;
  user_id: string;
  period: "weekly" | "monthly";
  period_start: string;
  period_end: string;
  report_data: ReportData;
  created_at: string;
}
