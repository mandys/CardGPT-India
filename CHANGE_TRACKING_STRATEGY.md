# Change Tracking Strategy for IP-Protected Data

## 🎯 **Problem Statement**

- **data/*.json files**: Cannot be committed (IP protection)
- **card_data.jsonl files**: Cannot be committed (generated from IP data)
- **Need to track changes**: For incremental updates and deployment
- **Team collaboration**: Multiple developers need sync strategy

## 📊 **Current Solution: State File Tracking**

### **Automatic State Management**
The incremental update system creates `.incremental_state.json`:

```json
{
  "data/hdfc-infinia.json": {
    "hash": "a1b2c3d4e5f6...",
    "last_modified": 1691234567.89,
    "size": 45123
  },
  "data/axis-atlas.json": {
    "hash": "f6e5d4c3b2a1...",
    "last_modified": 1691234568.12,
    "size": 42856
  }
}
```

### **What Gets Tracked**
- **File Hashes**: SHA256 of file content for change detection
- **Timestamps**: Last modification time for temporal tracking
- **File Sizes**: Quick validation of changes
- **Incremental State**: What was last processed

## 🔧 **Enhanced Tracking Strategy**

### 1. **Commit State Files** (Safe to commit)
```bash
# Add to .gitignore (already done)
data/*.json
*.jsonl

# Commit state tracking files
git add .incremental_state.json
git add DEPLOYMENT_GUIDE.md
git add CHANGE_TRACKING_STRATEGY.md
git commit -m "Add change tracking infrastructure"
```

### 2. **Deployment Log System**
```bash
# Create deployment log
echo "$(date): Deployed insurance category (1055 chunks)" >> deployment.log
git add deployment.log
git commit -m "Log: Insurance category deployment"
```

### 3. **Schema Versioning**
Track data structure changes in committed files:

```bash
# Update schema version when standardized categories change
echo "v2.1: Added insurance category to spending_categories" >> SCHEMA_VERSIONS.md
git add SCHEMA_VERSIONS.md
git commit -m "Schema v2.1: Insurance category standardization"
```

## 📋 **Team Collaboration Strategy**

### **For New Team Members:**
1. **Get data files separately** (secure share/drive)
2. **Clone repository** (no data files included)
3. **Copy data files** to `data/` directory
4. **Run incremental update** to generate state

### **For Synchronization:**
1. **Pull latest code** with state files
2. **Check state differences**:
   ```bash
   python incremental_update.py --check-changes
   ```
3. **If state differs**: Data files need updating
4. **Request latest data** from secure source

### **For Production Deployment:**
1. **Verify state file** matches expected hashes
2. **Run deployment** using tracked state
3. **Log deployment** with timestamp and chunk count

## 🔐 **Security Considerations**

### **What's Safe to Commit:**
- ✅ `.incremental_state.json` (only hashes, no content)
- ✅ `deployment.log` (timestamps and statistics)
- ✅ `SCHEMA_VERSIONS.md` (structure changes)
- ✅ Infrastructure tools (`incremental_update.py`, etc.)

### **What's Never Committed:**
- ❌ `data/*.json` (credit card data - IP protected)
- ❌ `*.jsonl` (generated from IP data)
- ❌ Raw data backups or exports

## 🚀 **Recommended Workflow**

### **Daily Development:**
```bash
# 1. Check for changes
python incremental_update.py --check-changes

# 2. If changes exist, generate delta
python incremental_update.py

# 3. Test locally, then deploy to staging
gsutil cp card_data_delta.jsonl gs://staging-bucket/

# 4. Log the deployment
echo "$(date): Deployed $(wc -l card_data_delta.jsonl | awk '{print $1}') chunks" >> deployment.log

# 5. Commit tracking info
git add .incremental_state.json deployment.log
git commit -m "Deploy: $(date +%Y-%m-%d) incremental update"
```

### **Production Deployment:**
```bash
# 1. Verify state consistency
python incremental_update.py --check-changes

# 2. Generate production-ready delta
python incremental_update.py

# 3. Deploy to production
gsutil cp card_data_delta.jsonl gs://production-bucket/

# 4. Update Vertex AI Search (see DEPLOYMENT_GUIDE.md)

# 5. Log successful deployment
echo "$(date): PRODUCTION deployed $(wc -l card_data_delta.jsonl | awk '{print $1}') chunks" >> deployment.log
git add deployment.log
git commit -m "Production deploy: $(date +%Y-%m-%d)"
```

## 📊 **Monitoring Changes**

### **State File Analysis:**
```bash
# Compare state files between commits
git diff HEAD~1 .incremental_state.json

# See what files changed
python incremental_update.py --check-changes
```

### **Deployment History:**
```bash
# View deployment log
tail -20 deployment.log

# Search for specific deployments
grep "insurance" deployment.log
```

This strategy provides **full change tracking** while maintaining **IP protection** and enabling **team collaboration**.