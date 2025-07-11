export interface CreditCardData {
  common_terms: {
    interest_free_grace_period: {
      duration: string;
      condition_for_loss: string;
    };
    minimum_amount_due_logic: {
      base: string;
      floor?: string;
      reference_sources?: string[];
    };
    finance_charges: {
      rate_per_month: string;
      rate_per_annum: string;
      cash_withdrawal_start: string;
      applicability: string;
      interest_accrual_on_fees_charges_gst: boolean;
      interest_accrual_on_customer_spends_levied_interest_emis: boolean;
      reference_sources?: string[];
    };
    surcharge_fees: Record<string, string>;
    cash_withdrawal: {
      fee: string;
      limit: string;
      reference_sources?: string[];
    };
    fuel_surcharge_waiver?: {
      rate: string;
      waiver_band?: string;
      monthly_cap?: string;
      details?: string;
      reference_sources?: string[];
    };
    other_fees: Record<string, string>;
    card_management_policies?: Record<string, string>;
    reward_points_policy?: Record<string, any>;
  };
  [key: string]: any;
}

export interface ProcessedDocument {
  id: string;
  cardName: string;
  content: string;
  metadata: {
    section: string;
    subsection?: string;
    cardType: string;
  };
  embedding?: number[];
}

export interface QueryResult {
  documents: ProcessedDocument[];
  scores: number[];
  answer: string;
}

export interface SearchQuery {
  query: string;
  topK?: number;
  threshold?: number;
}