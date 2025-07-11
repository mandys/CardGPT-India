import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import apiRoutes, { initializeRoutes } from './routes/api';
import { DataLoader } from './services/dataLoader';
import { VectorSearchService } from './services/vectorSearch';
import { RAGPipeline } from './services/ragPipeline';
import logger from './utils/logger';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use('/api', apiRoutes);

async function initializeApplication() {
  try {
    logger.info('Starting supavec-clone application...');

    if (!process.env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY environment variable is required');
    }

    const dataPath = path.join(__dirname, '../data');
    const dataLoader = new DataLoader(dataPath);
    
    logger.info('Loading credit card data...');
    const documents = await dataLoader.loadAllCreditCardData();
    
    logger.info('Initializing vector search service...');
    const vectorSearch = new VectorSearchService();
    await vectorSearch.initializeIndex(documents);
    
    logger.info('Initializing RAG pipeline...');
    const ragPipeline = new RAGPipeline(vectorSearch);
    
    initializeRoutes(ragPipeline, vectorSearch);
    
    logger.info('Application initialized successfully');
    
    return { vectorSearch, ragPipeline };
  } catch (error) {
    logger.error('Failed to initialize application:', error);
    process.exit(1);
  }
}

app.get('/', (req, res) => {
  res.json({
    message: 'Supavec Clone - RAG API for Indian Credit Card Data',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      cards: '/api/cards',
      query: '/api/query',
      cardQuery: '/api/query/:cardName',
      compare: '/api/compare',
      search: '/api/search'
    },
    documentation: {
      query: 'POST /api/query with { "question": "your question", "topK": 5 }',
      cardQuery: 'POST /api/query/:cardName with { "question": "your question", "topK": 5 }',
      compare: 'POST /api/compare with { "question": "your question", "cards": ["card1", "card2"] }',
      search: 'POST /api/search with { "query": "your query", "topK": 5, "threshold": 0.3 }'
    }
  });
});

initializeApplication().then(({ vectorSearch, ragPipeline }) => {
  app.listen(PORT, () => {
    logger.info(`Server running on port ${PORT}`);
    logger.info(`Available cards: ${vectorSearch.getAvailableCards().join(', ')}`);
    console.log(`
🚀 Supavec Clone is running!
📍 Server: http://localhost:${PORT}
📊 API Documentation: http://localhost:${PORT}
🔍 Available cards: ${vectorSearch.getAvailableCards().join(', ')}

Example queries:
- POST /api/query with { "question": "What are the interest rates?" }
- POST /api/query/axis-atlas with { "question": "What are the cash withdrawal fees?" }
- POST /api/compare with { "question": "Compare interest rates", "cards": ["Axis Atlas", "Icici Epm"] }
`);
  });
}).catch(error => {
  logger.error('Failed to start server:', error);
  process.exit(1);
});