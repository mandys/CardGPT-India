import OpenAI from 'openai';
import { VectorSearchService } from './vectorSearch';
import { ProcessedDocument, QueryResult } from '../types';
import logger from '../utils/logger';

export class RAGPipeline {
  private openai: OpenAI;
  private vectorSearch: VectorSearchService;

  constructor(vectorSearch: VectorSearchService) {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
    this.vectorSearch = vectorSearch;
  }

  async query(question: string, topK: number = 5): Promise<QueryResult> {
    try {
      const searchResults = await this.vectorSearch.search({
        query: question,
        topK,
        threshold: 0.3
      });

      const answer = await this.generateAnswer(question, searchResults.documents);

      return {
        documents: searchResults.documents,
        scores: searchResults.scores,
        answer
      };
    } catch (error) {
      logger.error('Error in RAG pipeline:', error);
      throw error;
    }
  }

  async queryByCard(cardName: string, question: string, topK: number = 5): Promise<QueryResult> {
    try {
      const searchResults = await this.vectorSearch.searchByCard(cardName, question, topK);

      const answer = await this.generateAnswer(question, searchResults.documents, cardName);

      return {
        documents: searchResults.documents,
        scores: searchResults.scores,
        answer
      };
    } catch (error) {
      logger.error('Error in card-specific RAG pipeline:', error);
      throw error;
    }
  }

  private async generateAnswer(question: string, documents: ProcessedDocument[], cardName?: string): Promise<string> {
    if (documents.length === 0) {
      return "I couldn't find relevant information to answer your question. Please try rephrasing your query or asking about specific credit card features.";
    }

    const context = documents.map(doc => 
      `Card: ${doc.cardName}\nSection: ${doc.metadata.section}\nContent: ${doc.content}`
    ).join('\n\n---\n\n');

    const systemPrompt = `You are an expert assistant helping users understand Indian credit card terms and conditions. 
    You have access to detailed information about various credit cards from Indian banks.
    
    Please provide accurate, helpful answers based on the provided context. If the context doesn't contain enough information to answer the question, say so clearly.
    
    Format your response in a clear, easy-to-understand way. Use bullet points or numbered lists when appropriate.
    Include specific details like fees, interest rates, and conditions when relevant.
    
    ${cardName ? `Focus on information about the ${cardName} card.` : 'Compare different cards when relevant.'}`;

    const userPrompt = `Based on the following credit card information, please answer this question: "${question}"

    Context:
    ${context}

    Please provide a comprehensive answer based on the information provided.`;

    try {
      const completion = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        max_tokens: 1000,
        temperature: 0.1,
      });

      return completion.choices[0].message.content || 'Sorry, I was unable to generate a response.';
    } catch (error) {
      logger.error('Error generating answer with OpenAI:', error);
      return 'Sorry, I encountered an error while generating the answer. Please try again.';
    }
  }

  async compareCards(question: string, cardNames: string[]): Promise<QueryResult> {
    try {
      const allResults = await Promise.all(
        cardNames.map(cardName => 
          this.vectorSearch.searchByCard(cardName, question, 3)
        )
      );

      const allDocuments = allResults.flatMap(result => result.documents);
      const allScores = allResults.flatMap(result => result.scores);

      const answer = await this.generateComparisonAnswer(question, allDocuments, cardNames);

      return {
        documents: allDocuments,
        scores: allScores,
        answer
      };
    } catch (error) {
      logger.error('Error in card comparison:', error);
      throw error;
    }
  }

  private async generateComparisonAnswer(question: string, documents: ProcessedDocument[], cardNames: string[]): Promise<string> {
    const context = documents.map(doc => 
      `Card: ${doc.cardName}\nSection: ${doc.metadata.section}\nContent: ${doc.content}`
    ).join('\n\n---\n\n');

    const systemPrompt = `You are an expert assistant helping users compare Indian credit cards.
    
    Please provide a clear comparison based on the provided context. Format your response as a comparison table or structured list.
    Highlight key differences and similarities between the cards.
    Include specific details like fees, interest rates, and conditions when comparing.
    
    If some information is missing for certain cards, mention that clearly.`;

    const userPrompt = `Please compare the following credit cards (${cardNames.join(', ')}) for this question: "${question}"

    Context:
    ${context}

    Please provide a structured comparison based on the information provided.`;

    try {
      const completion = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        max_tokens: 1200,
        temperature: 0.1,
      });

      return completion.choices[0].message.content || 'Sorry, I was unable to generate a comparison.';
    } catch (error) {
      logger.error('Error generating comparison answer with OpenAI:', error);
      return 'Sorry, I encountered an error while generating the comparison. Please try again.';
    }
  }
}