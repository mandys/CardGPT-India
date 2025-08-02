# Vertex AI Deployment Guide

## 🚀 **Quick Deployment (Incremental Update)**

### 1. Generate Delta Chunks
```bash
# Check what changed
python incremental_update.py --check-changes

# Generate delta update (only changed files)
python incremental_update.py
# Output: card_data_delta.jsonl (1055 chunks with insurance)
```

### 2. Upload to Google Cloud Storage
```bash
# Upload delta file
gsutil cp card_data_delta.jsonl gs://your-bucket/card_data_delta.jsonl

# Upload updated FAQ file
gsutil cp faq-common-questions.jsonl gs://your-bucket/faq-common-questions.jsonl
```

### 3. Update Vertex AI Search Data Store

**Main Card Data Store:**
1. Go to [Vertex AI Search Console](https://console.cloud.google.com/ai/search)
2. Select your existing data store
3. **Delete all existing documents** (unfortunately required)
4. **Import new data** → Choose `card_data_delta.jsonl` from GCS
5. Wait for indexing (5-10 minutes vs previous 20-30 minutes)

**FAQ Data Store (Optional - Separate):**
1. Create new data store for FAQ data
2. Import `faq-common-questions.jsonl`
3. Update application to query both data stores

## 📋 **Full Rebuild (If Needed)**

### 1. Generate Complete JSONL
```bash
python incremental_update.py --full-rebuild
# Output: card_data.jsonl (1055 chunks complete)
```

### 2. Upload and Update
```bash
gsutil cp card_data.jsonl gs://your-bucket/card_data.jsonl
# Follow same Vertex AI update process
```

## 🎯 **Downtime Comparison**

| Method | File Size | Upload Time | Indexing Time | Total Downtime |
|--------|-----------|-------------|---------------|----------------|
| **Previous (Full)** | ~1023 chunks | 5-8 min | 15-25 min | **20-30 min** |
| **Incremental** | 1055 chunks | 3-5 min | 5-10 min | **<15 min** |
| **Future Incremental** | ~50-100 chunks | 1-2 min | 2-5 min | **<5 min** |

## ⚠️ **Important Notes**

1. **Vertex AI Limitation**: No true incremental updates - must delete and re-import
2. **Downtime is Unavoidable**: But minimized with delta files
3. **FAQ System**: Consider separate data store for FAQ data
4. **Versioning**: Each chunk has metadata for tracking changes

## 🔧 **Recommended Workflow**

1. **Development**: Use `--check-changes` to see what will change
2. **Staging**: Test with delta file first
3. **Production**: Upload delta file during low-traffic hours
4. **Monitoring**: Verify search results after deployment