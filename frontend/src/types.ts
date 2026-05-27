// Type setting
export interface GroupData {
  group: string;
  rate: number;
  count: number;
  percentage: string;
}

export interface Mitigation {
  type: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
}

export interface AuditResult {
  characteristic: string;
  groups: GroupData[];
  disparity: {
    disparate_impact_ratio: number;
    max_disparity: number;
    flag: boolean;
    highest_group: string;
    lowest_group: string;
  };
}

export interface AuditResponse {
  overall_risk: {
    level: 'Low' | 'Moderate' | 'High' | 'Critical';
    score: number;
    flagged_characteristics: string[];
  };
  metadata: {
    timestamp: string | number | Date;
    total_rows: number;
    total_columns: number;
    prediction_column: string;
    protected_characteristics_found: string[];
    columns_detected: string[];
  };
  warnings: string[];
  audits: AuditResult[];
  mitigations: Mitigation[];
}