import { useState, useEffect, useCallback } from 'react';
import tipsData from '../data/tips.json';

interface Tip {
  text: string;
  category: string;
}

export const useTips = () => {
  const [currentTip, setCurrentTip] = useState<Tip | null>(null);

  // Get a random tip from a specific category
  const getTipFromCategory = useCallback((categoryKey: string): Tip | null => {
    const category = tipsData.categories[categoryKey as keyof typeof tipsData.categories];
    if (!category || !category.tips.length) return null;

    const randomTip = category.tips[Math.floor(Math.random() * category.tips.length)];
    return {
      text: randomTip,
      category: category.title
    };
  }, []);

  // Get a random tip from any category
  const getRandomTip = useCallback((): Tip => {
    const categoryKeys = Object.keys(tipsData.categories);
    const randomCategoryKey = categoryKeys[Math.floor(Math.random() * categoryKeys.length)];
    
    const tip = getTipFromCategory(randomCategoryKey);
    return tip || {
      text: "🤔 Try asking about specific spending amounts: 'For ₹50K monthly spend...'",
      category: "General"
    };
  }, [getTipFromCategory]);

  // Detect relevant category based on user query
  const detectCategory = useCallback((query: string): string[] => {
    const lowerQuery = query.toLowerCase();
    const relevantCategories: string[] = [];

    // Check each category's keywords
    Object.entries(tipsData.contextual_mapping).forEach(([category, keywords]) => {
      const hasKeyword = keywords.some(keyword => 
        lowerQuery.includes(keyword.toLowerCase())
      );
      if (hasKeyword) {
        relevantCategories.push(category);
      }
    });

    return relevantCategories;
  }, []);

  // Get contextual tip based on user's query
  const getContextualTip = useCallback((userQuery: string): Tip => {
    const relevantCategories = detectCategory(userQuery);
    
    if (relevantCategories.length > 0) {
      // Pick a random category from relevant categories
      const randomCategory = relevantCategories[Math.floor(Math.random() * relevantCategories.length)];
      const tip = getTipFromCategory(randomCategory);
      if (tip) return tip;
    }
    
    // Fallback to random tip
    return getRandomTip();
  }, [detectCategory, getTipFromCategory, getRandomTip]);

  // Set a new random tip
  const refreshTip = useCallback(() => {
    setCurrentTip(getRandomTip());
  }, [getRandomTip]);

  // Set contextual tip based on query
  const setContextualTip = useCallback((userQuery: string) => {
    setCurrentTip(getContextualTip(userQuery));
  }, [getContextualTip]);

  // Initialize with a random tip
  useEffect(() => {
    setCurrentTip(getRandomTip());
  }, [getRandomTip]);

  return {
    currentTip,
    refreshTip,
    setContextualTip,
    getRandomTip,
    getContextualTip,
    detectCategory
  };
};