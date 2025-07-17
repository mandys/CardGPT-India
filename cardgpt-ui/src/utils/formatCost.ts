/**
 * Format cost in USD with appropriate precision
 */
export function formatCost(cost: number): string {
  if (cost === 0) return '$0.00';
  
  if (cost < 0.001) {
    return `$${cost.toFixed(6)}`;
  } else if (cost < 0.01) {
    return `$${cost.toFixed(4)}`;
  } else if (cost < 1) {
    return `$${cost.toFixed(3)}`;
  } else {
    return `$${cost.toFixed(2)}`;
  }
}

/**
 * Format token count with commas
 */
export function formatTokens(tokens: number): string {
  return tokens.toLocaleString();
}

/**
 * Calculate cost per query estimate
 */
export function calculateEstimatedCost(
  inputTokens: number,
  outputTokens: number,
  inputCostPer1k: number,
  outputCostPer1k: number
): number {
  const inputCost = (inputTokens / 1000) * inputCostPer1k;
  const outputCost = (outputTokens / 1000) * outputCostPer1k;
  return inputCost + outputCost;
}

/**
 * Get cost efficiency rating
 */
export function getCostEfficiencyRating(cost: number): {
  rating: 'excellent' | 'good' | 'fair' | 'expensive';
  color: string;
  description: string;
} {
  if (cost < 0.001) {
    return {
      rating: 'excellent',
      color: 'text-green-600',
      description: 'Ultra-low cost'
    };
  } else if (cost < 0.01) {
    return {
      rating: 'good',
      color: 'text-blue-600',
      description: 'Low cost'
    };
  } else if (cost < 0.05) {
    return {
      rating: 'fair',
      color: 'text-yellow-600',
      description: 'Moderate cost'
    };
  } else {
    return {
      rating: 'expensive',
      color: 'text-red-600',
      description: 'High cost'
    };
  }
}