-- Migration: Add Gemini 2.5 Flash-Lite tracking to query_stats table
-- Date: 2025-07-22
-- Description: Add new column to track usage of the new Gemini 2.5 Flash-Lite model

ALTER TABLE query_stats 
ADD COLUMN gemini_flash_lite_queries INTEGER DEFAULT 0;