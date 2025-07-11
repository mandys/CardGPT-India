import { ProcessedDocument, SearchQuery } from '../types';
import { EmbeddingService } from './embeddings';
import logger from '../utils/logger';

export class VectorSearchService {
  private documents: ProcessedDocument[] = [];
  private embeddingService: EmbeddingService;

  constructor() {
    this.embeddingService = new EmbeddingService();
  }

  async initializeIndex(documents: ProcessedDocument[]): Promise<void> {
    logger.info('Initializing vector search index');
    
    const embeddedDocuments = await this.embeddingService.generateEmbeddings(documents);
    this.documents = embeddedDocuments.filter(doc => doc.embedding);
    
    logger.info(`Vector search index initialized with ${this.documents.length} documents`);
  }

  async search(query: SearchQuery): Promise<{ documents: ProcessedDocument[], scores: number[] }> {
    if (this.documents.length === 0) {
      throw new Error('Vector search index not initialized');
    }

    const queryEmbedding = await this.embeddingService.generateEmbedding(query.query);
    const topK = query.topK || 5;
    const threshold = query.threshold || 0.5;

    const results = this.documents
      .map(doc => {
        if (!doc.embedding) return null;
        
        const similarity = this.embeddingService.cosineSimilarity(queryEmbedding, doc.embedding);
        return { document: doc, score: similarity };
      })
      .filter(result => result !== null && result.score >= threshold)
      .sort((a, b) => b!.score - a!.score)
      .slice(0, topK);

    const documents = results.map(r => r!.document);
    const scores = results.map(r => r!.score);

    logger.info(`Search for "${query.query}" returned ${documents.length} results`);
    
    return { documents, scores };
  }

  async searchByCard(cardName: string, query: string, topK: number = 5): Promise<{ documents: ProcessedDocument[], scores: number[] }> {
    const filteredDocs = this.documents.filter(doc => 
      doc.cardName.toLowerCase().includes(cardName.toLowerCase())
    );

    if (filteredDocs.length === 0) {
      logger.warn(`No documents found for card: ${cardName}`);
      return { documents: [], scores: [] };
    }

    const queryEmbedding = await this.embeddingService.generateEmbedding(query);
    
    const results = filteredDocs
      .map(doc => {
        if (!doc.embedding) return null;
        
        const similarity = this.embeddingService.cosineSimilarity(queryEmbedding, doc.embedding);
        return { document: doc, score: similarity };
      })
      .filter(result => result !== null)
      .sort((a, b) => b!.score - a!.score)
      .slice(0, topK);

    const documents = results.map(r => r!.document);
    const scores = results.map(r => r!.score);

    logger.info(`Card-specific search for "${query}" in ${cardName} returned ${documents.length} results`);
    
    return { documents, scores };
  }

  getAvailableCards(): string[] {
    const uniqueCards = [...new Set(this.documents.map(doc => doc.cardName))];
    return uniqueCards.sort();
  }
}