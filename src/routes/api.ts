import { Router } from 'express';
import { RAGPipeline } from '../services/ragPipeline';
import { VectorSearchService } from '../services/vectorSearch';
import logger from '../utils/logger';

const router = Router();

let ragPipeline: RAGPipeline;
let vectorSearch: VectorSearchService;

export function initializeRoutes(rag: RAGPipeline, vs: VectorSearchService) {
  ragPipeline = rag;
  vectorSearch = vs;
}

router.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

router.get('/cards', async (req, res) => {
  try {
    const cards = vectorSearch.getAvailableCards();
    res.json({ cards });
  } catch (error) {
    logger.error('Error fetching available cards:', error);
    res.status(500).json({ error: 'Failed to fetch available cards' });
  }
});

router.post('/query', async (req, res) => {
  try {
    const { question, topK = 5 } = req.body;

    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: 'Question is required and must be a string' });
    }

    const result = await ragPipeline.query(question, topK);

    res.json({
      question,
      answer: result.answer,
      sources: result.documents.map(doc => ({
        cardName: doc.cardName,
        section: doc.metadata.section,
        content: doc.content.substring(0, 200) + '...'
      })),
      confidence: result.scores
    });
  } catch (error) {
    logger.error('Error processing query:', error);
    res.status(500).json({ error: 'Failed to process query' });
  }
});

router.post('/query/:cardName', async (req, res) => {
  try {
    const { cardName } = req.params;
    const { question, topK = 5 } = req.body;

    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: 'Question is required and must be a string' });
    }

    const result = await ragPipeline.queryByCard(cardName, question, topK);

    res.json({
      question,
      cardName,
      answer: result.answer,
      sources: result.documents.map(doc => ({
        cardName: doc.cardName,
        section: doc.metadata.section,
        content: doc.content.substring(0, 200) + '...'
      })),
      confidence: result.scores
    });
  } catch (error) {
    logger.error('Error processing card-specific query:', error);
    res.status(500).json({ error: 'Failed to process card-specific query' });
  }
});

router.post('/compare', async (req, res) => {
  try {
    const { question, cards } = req.body;

    if (!question || typeof question !== 'string') {
      return res.status(400).json({ error: 'Question is required and must be a string' });
    }

    if (!Array.isArray(cards) || cards.length < 2) {
      return res.status(400).json({ error: 'At least 2 cards are required for comparison' });
    }

    const result = await ragPipeline.compareCards(question, cards);

    res.json({
      question,
      cards,
      comparison: result.answer,
      sources: result.documents.map(doc => ({
        cardName: doc.cardName,
        section: doc.metadata.section,
        content: doc.content.substring(0, 200) + '...'
      }))
    });
  } catch (error) {
    logger.error('Error processing card comparison:', error);
    res.status(500).json({ error: 'Failed to process card comparison' });
  }
});

router.post('/search', async (req, res) => {
  try {
    const { query, topK = 5, threshold = 0.3 } = req.body;

    if (!query || typeof query !== 'string') {
      return res.status(400).json({ error: 'Query is required and must be a string' });
    }

    const result = await vectorSearch.search({
      query,
      topK,
      threshold
    });

    res.json({
      query,
      results: result.documents.map((doc, index) => ({
        cardName: doc.cardName,
        section: doc.metadata.section,
        content: doc.content,
        score: result.scores[index]
      }))
    });
  } catch (error) {
    logger.error('Error processing search:', error);
    res.status(500).json({ error: 'Failed to process search' });
  }
});

export default router;