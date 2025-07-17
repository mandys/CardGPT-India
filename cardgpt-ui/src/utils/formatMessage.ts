/**
 * Format message content for display
 */
export function formatMessageContent(content: string): string {
  // Basic formatting - you can extend this with more sophisticated formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
    .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
    .replace(/`(.*?)`/g, '<code>$1</code>') // Inline code
    .replace(/\n/g, '<br>'); // Line breaks
}

/**
 * Extract key information from message
 */
export function extractKeyInfo(content: string): {
  hasNumbers: boolean;
  hasCardNames: boolean;
  hasCalculations: boolean;
  isQuestion: boolean;
} {
  const hasNumbers = /\d/.test(content);
  const hasCardNames = /(?:axis|atlas|icici|epm|hsbc|premier)/i.test(content);
  const hasCalculations = /(?:earn|miles|points|spend|cost|fee|₹|calculate)/i.test(content);
  const isQuestion = content.includes('?') || /(?:what|how|which|when|where|why|can|do|does|is|are)/i.test(content);
  
  return {
    hasNumbers,
    hasCardNames,
    hasCalculations,
    isQuestion
  };
}

/**
 * Generate a unique ID for messages
 */
export function generateMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Sanitize user input
 */
export function sanitizeUserInput(input: string): string {
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .substring(0, 1000); // Limit length
}

/**
 * Check if message is likely a calculation query
 */
export function isCalculationQuery(content: string): boolean {
  const calculationKeywords = [
    'earn', 'miles', 'points', 'spend', 'cost', 'fee', 'calculate',
    'how much', 'how many', 'total', 'annual', 'yearly', 'monthly',
    '₹', 'lakh', 'thousand', 'crore'
  ];
  
  return calculationKeywords.some(keyword => 
    content.toLowerCase().includes(keyword)
  );
}

/**
 * Format time ago
 */
export function formatTimeAgo(timestamp: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - timestamp.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return timestamp.toLocaleDateString();
}