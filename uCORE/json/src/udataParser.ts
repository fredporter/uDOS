/**
 * uDATA Parser Module v1.0.0
 * Handles uDATA JSON minified format (one record per line)
 */

import * as fs from 'fs';

export interface uDATARecord {
    [key: string]: any;
}

export class uDATAParser {
    /**
     * Parse uDATA format file (JSON records, one per line)
     */
    static parseFile(filePath: string): uDATARecord[] {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            return this.parseContent(content);
        } catch (error) {
            console.error(`❌ Error reading uDATA file ${filePath}:`, error);
            return [];
        }
    }

    /**
     * Parse uDATA format content string
     */
    static parseContent(content: string): uDATARecord[] {
        const records: uDATARecord[] = [];
        const lines = content.split('\n').filter(line => line.trim() !== '');

        for (const line of lines) {
            try {
                const record = JSON.parse(line.trim());
                records.push(record);
            } catch (error) {
                console.error(`❌ Error parsing uDATA line: ${line}`, error);
            }
        }

        return records;
    }

    /**
     * Convert array of objects to uDATA format (one JSON record per line)
     */
    static toUDATA(records: uDATARecord[]): string {
        return records.map(record => JSON.stringify(record)).join('\n');
    }

    /**
     * Write records to uDATA format file
     */
    static writeFile(filePath: string, records: uDATARecord[]): boolean {
        try {
            const content = this.toUDATA(records);
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ Wrote ${records.length} records to ${filePath}`);
            return true;
        } catch (error) {
            console.error(`❌ Error writing uDATA file ${filePath}:`, error);
            return false;
        }
    }

    /**
     * Validate uDATA format file
     */
    static validateFile(filePath: string): boolean {
        try {
            const records = this.parseFile(filePath);
            return records.length > 0;
        } catch (error) {
            console.error(`❌ uDATA validation failed for ${filePath}:`, error);
            return false;
        }
    }

    /**
     * Get metadata record (usually first record with metadata field)
     */
    static getMetadata(records: uDATARecord[]): uDATARecord | null {
        return records.find(record => record.metadata) || null;
    }

    /**
     * Filter records by type
     */
    static filterByType(records: uDATARecord[], type: string): uDATARecord[] {
        return records.filter(record => record.type === type);
    }

    /**
     * Find record by name or id
     */
    static findRecord(records: uDATARecord[], key: string, value: string): uDATARecord | undefined {
        return records.find(record => record[key] === value);
    }

    /**
     * Convert traditional JSON file to uDATA format
     */
    static convertJsonToUDATA(inputPath: string, outputPath: string): boolean {
        try {
            const content = fs.readFileSync(inputPath, 'utf8');
            const jsonData = JSON.parse(content);

            let records: uDATARecord[] = [];

            if (Array.isArray(jsonData)) {
                records = jsonData;
            } else if (typeof jsonData === 'object') {
                // Handle object-based JSON - create records from object structure
                if (jsonData.metadata) {
                    records.push({ metadata: jsonData.metadata });
                    delete jsonData.metadata;
                }

                // Convert remaining object properties to records
                for (const [key, value] of Object.entries(jsonData)) {
                    if (typeof value === 'object' && value !== null) {
                        records.push({ name: key, ...value });
                    } else {
                        records.push({ name: key, value: value });
                    }
                }
            }

            return this.writeFile(outputPath, records);
        } catch (error) {
            console.error(`❌ Error converting JSON to uDATA:`, error);
            return false;
        }
    }
}

export default uDATAParser;
