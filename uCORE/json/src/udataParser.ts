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
     * Convert array of objects to uDATA format (minified JSON, one record per line)
     */
    static toUDATA(records: uDATARecord[]): string {
        return records.map(record => JSON.stringify(record, null, 0)).join('\n');
    }

    /**
     * Convert array of objects to uDATA format with custom formatting options
     */
    static toUDATAFormatted(records: uDATARecord[], options?: {
        minified?: boolean;
        sortKeys?: boolean;
        addMetadata?: boolean;
    }): string {
        const opts = {
            minified: true,
            sortKeys: false,
            addMetadata: false,
            ...options
        };

        let result = records.map(record => {
            // Sort keys if requested
            if (opts.sortKeys) {
                const sortedRecord: uDATARecord = {};
                Object.keys(record).sort().forEach(key => {
                    sortedRecord[key] = record[key];
                });
                record = sortedRecord;
            }

            // Use minified format (no spaces) or compact format
            return opts.minified
                ? JSON.stringify(record, null, 0)
                : JSON.stringify(record);
        }).join('\n');

        // Add metadata record at the beginning if requested
        if (opts.addMetadata) {
            const metadata = {
                metadata: {
                    format: "uDATA",
                    version: "1.0",
                    generated: new Date().toISOString(),
                    records: records.length,
                    description: "uDOS Data Format - Minified JSON records, one per line"
                }
            };
            result = JSON.stringify(metadata, null, 0) + '\n' + result;
        }

        return result;
    }

    /**
     * Write records to uDATA format file with options
     */
    static writeFile(filePath: string, records: uDATARecord[], options?: {
        minified?: boolean;
        addMetadata?: boolean;
        sortKeys?: boolean;
    }): boolean {
        try {
            const content = this.toUDATAFormatted(records, options);
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ Wrote ${records.length} records to ${filePath}`);
            return true;
        } catch (error) {
            console.error(`❌ Error writing uDATA file ${filePath}:`, error);
            return false;
        }
    }

    /**
     * Write records to uDATA format file (legacy method)
     */
    static writeFileSimple(filePath: string, records: uDATARecord[]): boolean {
        return this.writeFile(filePath, records, { minified: true, addMetadata: false });
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
     * Convert traditional JSON file to uDATA format with enhanced options
     */
    static convertJsonToUDATA(inputPath: string, outputPath: string, options?: {
        addMetadata?: boolean;
        preserveStructure?: boolean;
        sortKeys?: boolean;
    }): boolean {
        try {
            const content = fs.readFileSync(inputPath, 'utf8');
            const jsonData = JSON.parse(content);

            const opts = {
                addMetadata: true,
                preserveStructure: false,
                sortKeys: false,
                ...options
            };

            let records: uDATARecord[] = [];

            if (Array.isArray(jsonData)) {
                records = jsonData;
            } else if (typeof jsonData === 'object') {
                // Handle object-based JSON - create records from object structure
                if (jsonData.metadata && !opts.preserveStructure) {
                    records.push({ metadata: jsonData.metadata });
                    delete jsonData.metadata;
                }

                // Convert remaining object properties to records
                for (const [key, value] of Object.entries(jsonData)) {
                    if (Array.isArray(value)) {
                        // Handle arrays - each item becomes a record
                        value.forEach((item, index) => {
                            if (typeof item === 'object' && item !== null) {
                                records.push({
                                    category: key,
                                    index: index,
                                    ...item
                                });
                            } else {
                                records.push({
                                    category: key,
                                    index: index,
                                    value: item
                                });
                            }
                        });
                    } else if (typeof value === 'object' && value !== null) {
                        records.push({ name: key, ...value });
                    } else {
                        records.push({ name: key, value: value });
                    }
                }
            }

            return this.writeFile(outputPath, records, {
                minified: true,
                addMetadata: opts.addMetadata,
                sortKeys: opts.sortKeys
            });
        } catch (error) {
            console.error(`❌ Error converting JSON to uDATA:`, error);
            return false;
        }
    }

    /**
     * Read and parse both JSON and uDATA formats automatically
     */
    static readUniversal(filePath: string): uDATARecord[] {
        try {
            const content = fs.readFileSync(filePath, 'utf8').trim();

            // Check if it's uDATA format (multiple lines with JSON objects)
            const lines = content.split('\n').filter((line: string) => line.trim() !== '');

            if (lines.length > 1) {
                // Likely uDATA format
                return this.parseContent(content);
            } else {
                // Likely regular JSON
                const jsonData = JSON.parse(content);

                if (Array.isArray(jsonData)) {
                    return jsonData;
                } else {
                    // Convert single object to array
                    return [jsonData];
                }
            }
        } catch (error) {
            console.error(`❌ Error reading file ${filePath}:`, error);
            return [];
        }
    }

    /**
     * Get statistics about uDATA file
     */
    static getStats(records: uDATARecord[]): {
        totalRecords: number;
        metadataRecords: number;
        dataRecords: number;
        uniqueKeys: string[];
        categories: string[];
    } {
        const stats = {
            totalRecords: records.length,
            metadataRecords: 0,
            dataRecords: 0,
            uniqueKeys: new Set<string>(),
            categories: new Set<string>()
        };

        records.forEach(record => {
            if (record.metadata) {
                stats.metadataRecords++;
            } else {
                stats.dataRecords++;
            }

            Object.keys(record).forEach(key => {
                stats.uniqueKeys.add(key);
            });

            if (record.category) {
                stats.categories.add(record.category);
            }
        });

        return {
            totalRecords: stats.totalRecords,
            metadataRecords: stats.metadataRecords,
            dataRecords: stats.dataRecords,
            uniqueKeys: Array.from(stats.uniqueKeys),
            categories: Array.from(stats.categories)
        };
    }
}

export default uDATAParser;
