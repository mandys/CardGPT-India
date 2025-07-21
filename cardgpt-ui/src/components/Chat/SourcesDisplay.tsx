import React, { useState } from 'react';
import { FileText, CreditCard, Copy, ChevronDown, ChevronRight } from 'lucide-react';
import { DocumentSource } from '../../types';

interface SourcesDisplayProps {
  sources: DocumentSource[];
}

const SourcesDisplay: React.FC<SourcesDisplayProps> = ({ sources }) => {
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const toggleSource = (index: number) => {
    const newExpanded = new Set(expandedSources);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSources(newExpanded);
  };

  const copyContent = async (content: string, index: number) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy content:', err);
    }
  };

  const getCardColor = (cardName: string) => {
    if (cardName.toLowerCase().includes('axis') || cardName.toLowerCase().includes('atlas')) {
      return 'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300';
    } else if (cardName.toLowerCase().includes('icici') || cardName.toLowerCase().includes('epm')) {
      return 'bg-orange-50 border-orange-200 text-orange-700 dark:bg-orange-900/20 dark:border-orange-800 dark:text-orange-300';
    } else if (cardName.toLowerCase().includes('hsbc') || cardName.toLowerCase().includes('premier')) {
      return 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300';
    }
    return 'bg-gray-50 border-gray-200 text-gray-700 dark:bg-gray-900/20 dark:border-gray-800 dark:text-gray-300';
  };

  const formatSimilarity = (similarity: number) => {
    if (similarity > 0) {
      return `${(similarity * 100).toFixed(1)}%`;
    }
    return 'N/A';
  };

  const truncateContent = (content: string, maxLength: number = 150) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  if (!sources || sources.length === 0) {
    return (
      <div className="bg-gray-50 dark:bg-gray-900/20 border border-gray-200 dark:border-gray-800 rounded-lg p-3">
        <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 text-sm">
          <FileText className="w-4 h-4" />
          No sources found
        </div>
      </div>
    );
  }

  return (
    <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3 space-y-2">
      <div className="flex items-center gap-2 text-green-700 dark:text-green-300 font-medium text-sm">
        <FileText className="w-4 h-4" />
        Sources ({sources.length})
      </div>
      
      <div className="space-y-2">
        {sources.map((source, index) => {
          const isExpanded = expandedSources.has(index);
          const cardColorClass = getCardColor(source.cardName);
          
          return (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
              {/* Source Header */}
              <div 
                className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                onClick={() => toggleSource(index)}
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  )}
                  
                  <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border ${cardColorClass} flex-shrink-0`}>
                    <CreditCard className="w-3 h-3" />
                    {source.cardName.replace(/Credit Card$/, '').trim()}
                  </div>
                  
                  <div className="text-sm text-gray-600 dark:text-gray-400 truncate">
                    {source.section}
                  </div>
                  
                  {source.similarity > 0 && (
                    <div className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded flex-shrink-0">
                      {formatSimilarity(source.similarity)}
                    </div>
                  )}
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    copyContent(source.content, index);
                  }}
                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                  title="Copy content"
                >
                  {copiedIndex === index ? (
                    <span className="text-green-500 text-xs">✓</span>
                  ) : (
                    <Copy className="w-3 h-3" />
                  )}
                </button>
              </div>
              
              {/* Source Content */}
              {isExpanded && (
                <div className="px-3 pb-3 border-t border-gray-100 dark:border-gray-700">
                  <div className="mt-2 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">
                    {source.content}
                  </div>
                </div>
              )}
              
              {/* Preview when collapsed */}
              {!isExpanded && (
                <div className="px-3 pb-3">
                  <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                    {truncateContent(source.content)}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      <div className="text-xs text-gray-500 dark:text-gray-400 italic">
        Click on any source to expand and view full content
      </div>
    </div>
  );
};

export default SourcesDisplay;