export type DataStatus = "live" | "demo" | "degraded" | "unavailable";

export interface SourceEnvelope {
  status: DataStatus;
  source: string;
  observed_at?: string | null;
  ingested_at: string;
  message?: string | null;
}

export interface RiskDriver {
  factor: string;
  contribution: number;
  value?: number | null;
}

export type RiskCategory = "LOW" | "MODERATE" | "HIGH" | "VERY_HIGH" | "CRITICAL";

export interface RiskAssessment {
  location: { latitude: number; longitude: number; name?: string | null };
  risk_score: number;
  risk_probability: number;
  category: RiskCategory;
  confidence: number;
  uncertainty: number;
  timestamp: string;
  model_version: string;
  feature_version: string;
  drivers: RiskDriver[];
  data_freshness: { layer: string; status: string; observed_at?: string | null }[];
  data_sources: SourceEnvelope[];
  previous_risk_score?: number | null;
  trend_explanation?: string | null;
}
