import fs from 'fs';
import path from 'path';
import { CreditCardData, ProcessedDocument } from '../types';
import logger from '../utils/logger';

export class DataLoader {
  private dataPath: string;

  constructor(dataPath: string = './data') {
    this.dataPath = dataPath;
  }

  async loadAllCreditCardData(): Promise<ProcessedDocument[]> {
    const documents: ProcessedDocument[] = [];
    
    try {
      const files = fs.readdirSync(this.dataPath);
      const jsonFiles = files.filter(file => file.endsWith('.json'));
      
      logger.info(`Found ${jsonFiles.length} JSON files in ${this.dataPath}`);
      
      for (const file of jsonFiles) {
        const filePath = path.join(this.dataPath, file);
        const cardData = this.loadCreditCardFile(filePath);
        const processedDocs = this.processCardData(cardData, file);
        documents.push(...processedDocs);
      }
      
      logger.info(`Processed ${documents.length} documents from ${jsonFiles.length} files`);
      return documents;
    } catch (error) {
      logger.error('Error loading credit card data:', error);
      throw error;
    }
  }

  private loadCreditCardFile(filePath: string): CreditCardData {
    try {
      const fileContent = fs.readFileSync(filePath, 'utf8');
      return JSON.parse(fileContent) as CreditCardData;
    } catch (error) {
      logger.error(`Error reading file ${filePath}:`, error);
      throw error;
    }
  }

  private processCardData(cardData: any, filename: string): ProcessedDocument[] {
    const cardName = this.extractCardName(filename);
    const documents: ProcessedDocument[] = [];

    // Process common_terms
    if (cardData.common_terms) {
      Object.entries(cardData.common_terms).forEach(([section, data]) => {
        const content = this.formatSectionContent(section, data);
        
        documents.push({
          id: `${cardName}_common_${section}`,
          cardName,
          content,
          metadata: {
            section: `common_terms_${section}`,
            cardType: cardName
          }
        });
      });
    }

    // Process card-specific data (rewards, benefits, etc.)
    if (cardData.card) {
      const cardInfo = cardData.card;
      const importantSections = ['fees', 'rewards', 'reward_capping', 'milestones', 'insurance', 'lounge_access', 'welcome_benefits'];
      
      Object.entries(cardInfo).forEach(([section, data]) => {
        if (typeof data === 'object' && data !== null && !['id', 'name', 'bank', 'category', 'network', 'launch_date'].includes(section)) {
          const content = this.formatSectionContent(section, data);
          
          documents.push({
            id: `${cardName}_card_${section}`,
            cardName,
            content,
            metadata: {
              section,
              cardType: cardName
            }
          });
        } else if (importantSections.includes(section)) {
          const content = this.formatSectionContent(section, data);
          
          documents.push({
            id: `${cardName}_card_${section}`,
            cardName,
            content,
            metadata: {
              section,
              cardType: cardName
            }
          });
        }
      });
    }

    return documents;
  }

  private extractCardName(filename: string): string {
    return filename.replace('.json', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  private formatSectionContent(section: string, data: any): string {
    const sectionTitle = section.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    let content = `${sectionTitle}:\n`;

    if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
      Object.entries(data).forEach(([key, value]) => {
        const keyFormatted = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          content += `  ${keyFormatted}:\n`;
          Object.entries(value).forEach(([subKey, subValue]) => {
            const subKeyFormatted = subKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            if (typeof subValue === 'object') {
              content += `    ${subKeyFormatted}: ${JSON.stringify(subValue, null, 2)}\n`;
            } else {
              content += `    ${subKeyFormatted}: ${subValue}\n`;
            }
          });
        } else if (Array.isArray(value)) {
          content += `  ${keyFormatted}: ${value.join(', ')}\n`;
        } else {
          content += `  ${keyFormatted}: ${value}\n`;
        }
      });
    } else if (Array.isArray(data)) {
      content += `  ${data.join(', ')}\n`;
    } else {
      content += `  ${data}\n`;
    }

    return content;
  }
}