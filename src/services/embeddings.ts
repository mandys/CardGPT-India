import OpenAI from 'openai';
import { ProcessedDocument } from '../types';
import logger from '../utils/logger';

export class EmbeddingService {
  private openai: OpenAI;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async generateEmbedding(text: string): Promise<number[]> {
    try {
      const response = await this.openai.embeddings.create({
        model: 'text-embedding-3-small',
        input: text,
        encoding_format: 'float',
      });

      return response.data[0].embedding;
    } catch (error) {
      logger.error('Error generating embedding:', error);
      throw error;
    }
  }

  async generateEmbeddings(documents: ProcessedDocument[]): Promise<ProcessedDocument[]> {
    logger.info(`Generating embeddings for ${documents.length} documents`);
    
    const embeddedDocuments = await Promise.all(
      documents.map(async (doc) => {
        try {
          const embedding = await this.generateEmbedding(doc.content);
          return { ...doc, embedding };
        } catch (error) {
          logger.error(`Error generating embedding for document ${doc.id}:`, error);
          return doc;
        }
      })
    );

    const successCount = embeddedDocuments.filter(doc => doc.embedding).length;
    logger.info(`Successfully generated embeddings for ${successCount}/${documents.length} documents`);
    
    return embeddedDocuments;
  }

  cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error('Vectors must have the same length');
    }

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    normA = Math.sqrt(normA);
    normB = Math.sqrt(normB);

    if (normA === 0 || normB === 0) {
      return 0;
    }

    return dotProduct / (normA * normB);
  }
}