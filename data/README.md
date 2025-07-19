# Credit Card Data Files

This directory contains the credit card terms and conditions data that powers the Credit Card Assistant.

## 🚨 **Data Not in Repository**

The actual JSON data files are **NOT included in the git repository** for the following reasons:

1. **Intellectual Property Protection**: These files represent significant work cleaning and structuring data from 10s of PDF documents
2. **Commercial Value**: The cleaned, structured data has commercial value and should not be freely distributed
3. **Quality Control**: Ensures only authorized versions of the data are used in production

## 📁 **Required Files**

To run the application locally, you need these data files in this directory:

```
data/
├── axis-atlas.json          # Axis Bank Atlas Credit Card terms and conditions
├── hsbc-premier.json        # HSBC Premier Credit Card terms and conditions  
├── icici-epm.json          # ICICI Bank Emeralde Private Metal Credit Card terms
└── README.md               # This file
```

## 📋 **Data Structure**

Each JSON file should contain:

```json
{
  "common_terms": {
    "interest_rates": { ... },
    "fees": { ... },
    "policies": { ... }
  },
  "card": {
    "name": "Card Name",
    "rewards": { ... },
    "benefits": { ... },
    "milestones": { ... }
  }
}
```

## 🛠 **Setup Instructions**

### For Development Team Members:
1. Contact the project maintainer for access to the data files
2. Place the JSON files in this `data/` directory
3. Verify the files are loaded correctly by running the application

### For External Contributors:
1. The application will show an error if data files are missing
2. You can create minimal test data files with the same structure
3. Or contact the maintainers for access to sample data

## 🔒 **Security & Privacy**

- **Do NOT commit** these JSON files to git
- **Do NOT share** these files publicly
- **Do NOT upload** these files to any public storage
- The `.gitignore` file is configured to prevent accidental commits

## 🚀 **Production Deployment**

In production environments:
- Data files are loaded from secure storage (Google Cloud Storage)
- Vertex AI Search indexes are built from the structured data
- Local JSON files are not required in production

## 📊 **Adding New Credit Cards**

To add a new credit card:

1. **Create JSON file** following the existing structure
2. **Place in data/ directory** (will be ignored by git)
3. **Update Vertex AI Search** data store with new content
4. **Test locally** before deploying to production

## 🔄 **Data Processing Pipeline**

```
PDF Documents → Manual Cleaning → JSON Files → JSONL Format → Vertex AI Search → Production
```

The JSON files in this directory represent the "cleaned" stage and are the source of truth for the application data.

## ❓ **Troubleshooting**

**Error: "No data files found"**
- Ensure JSON files are present in this directory
- Check file names match exactly: `axis-atlas.json`, `hsbc-premier.json`, `icici-epm.json`
- Verify JSON files are valid (use `jq . filename.json` to validate)

**Error: "Invalid data structure"**
- Check that JSON files contain both `common_terms` and `card` sections
- Validate against the expected structure shown above

## 📞 **Contact**

For access to data files or questions about data structure:
- Contact project maintainers
- Refer to main README.md for setup instructions
- Check the application logs for specific error messages