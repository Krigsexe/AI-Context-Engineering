#!/usr/bin/env python3
"""
ODIN Hallucination Scanner v6.0 - Windows Compatible
Searches repository for hallucinated data patterns and generates detailed report.
"""

import os
import json
import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class HallucinationScanner:
    def __init__(self, mapping_file: str = "hallucination_mapping.yaml"):
        self.mapping_file = mapping_file
        self.hallucination_map = {}
        self.search_patterns = []
        self.results = []
        self.report_path = ".odin/hallucination_report.json"
        
    def load_mapping(self):
        """Load the hallucination mapping YAML file"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.hallucination_map = yaml.safe_load(f)
            print(f"✅ Loaded mapping from {self.mapping_file}")
        except Exception as e:
            print(f"❌ Error loading mapping file: {e}")
            return False
        return True
    
    def extract_search_patterns(self):
        """Extract all bad patterns from the mapping for searching"""
        patterns = []
        
        # Direct string patterns
        direct_patterns = [
            ('github_bad', self.hallucination_map.get('github_bad', '')),
            ('author_bad', self.hallucination_map.get('author_bad', '')),
            ('project_name_bad', self.hallucination_map.get('project_name_bad', '')),
            ('version_bad', self.hallucination_map.get('version_bad', '')),
            ('release_date_bad', self.hallucination_map.get('release_date_bad', '')),
            ('copyright_bad', self.hallucination_map.get('copyright_bad', '')),
            ('vscode_extension_bad', self.hallucination_map.get('vscode_extension_bad', ''))
        ]
        
        # List patterns
        list_patterns = [
            ('domains_bad', self.hallucination_map.get('domains_bad', [])),
            ('emails_bad', self.hallucination_map.get('emails_bad', [])),
            ('download_urls_bad', self.hallucination_map.get('download_urls_bad', [])),
            ('npm_packages_bad', self.hallucination_map.get('npm_packages_bad', [])),
            ('file_extensions_bad', self.hallucination_map.get('file_extensions_bad', [])),
            ('config_paths_bad', self.hallucination_map.get('config_paths_bad', [])),
            ('commands_bad', self.hallucination_map.get('commands_bad', [])),
            ('integrations_bad', self.hallucination_map.get('integrations_bad', [])),
            ('modes_bad', self.hallucination_map.get('modes_bad', [])),
            ('api_endpoints_bad', self.hallucination_map.get('api_endpoints_bad', [])),
            ('db_references_bad', self.hallucination_map.get('db_references_bad', [])),
            ('functions_bad', self.hallucination_map.get('functions_bad', [])),
            ('architecture_claims_bad', self.hallucination_map.get('architecture_claims_bad', []))
        ]
        
        # Add direct patterns
        for pattern_type, pattern_value in direct_patterns:
            if pattern_value:
                patterns.append((pattern_type, pattern_value))
        
        # Add list patterns
        for pattern_type, pattern_list in list_patterns:
            if pattern_list:
                for item in pattern_list:
                    patterns.append((pattern_type, item))
        
        self.search_patterns = patterns
        print(f"✅ Extracted {len(patterns)} search patterns")
        return patterns
    
    def search_with_findstr(self, pattern: str, pattern_type: str) -> List[Dict[str, Any]]:
        """Use Windows findstr to search for a pattern"""
        matches = []
        
        try:
            # Use findstr to search recursively
            cmd = f'findstr /S /N /I "{pattern}" *.*'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            file_path = parts[0].replace('\\', '/')
                            line_number = parts[1]
                            line_text = parts[2].strip()
                            
                            matches.append({
                                'file_path': file_path,
                                'line_number': int(line_number) if line_number.isdigit() else 0,
                                'line_text': line_text,
                                'pattern_type': pattern_type,
                                'pattern_value': pattern,
                                'match_context': line_text
                            })
        
        except Exception as e:
            print(f"⚠️  Error searching for pattern '{pattern}': {e}")
        
        return matches
    
    def search_manually(self, pattern: str, pattern_type: str) -> List[Dict[str, Any]]:
        """Manual search as fallback"""
        matches = []
        
        # Common file extensions to search
        extensions = ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md', '.txt', '.html', '.css']
        
        for root, dirs, files in os.walk('.'):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file).replace('\\', '/')
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line_content in enumerate(f, 1):
                                if pattern.lower() in line_content.lower():
                                    matches.append({
                                        'file_path': file_path,
                                        'line_number': line_num,
                                        'line_text': line_content.strip(),
                                        'pattern_type': pattern_type,
                                        'pattern_value': pattern,
                                        'match_context': line_content.strip()
                                    })
                    except Exception:
                        continue
        
        return matches
    
    def run_scan(self):
        """Run the complete hallucination scan"""
        print("🔍 Starting ODIN Hallucination Repository Scan...")
        
        # Load mapping
        if not self.load_mapping():
            return False
        
        # Extract patterns
        self.extract_search_patterns()
        
        # Search for each pattern
        total_matches = 0
        for pattern_type, pattern_value in self.search_patterns:
            print(f"🔎 Searching for: {pattern_value} ({pattern_type})")
            
            # Try findstr first, fallback to manual search
            matches = self.search_with_findstr(pattern_value, pattern_type)
            
            if not matches:
                matches = self.search_manually(pattern_value, pattern_type)
            
            if matches:
                print(f"📍 Found {len(matches)} matches for pattern '{pattern_value}'")
                self.results.extend(matches)
                total_matches += len(matches)
        
        print(f"✅ Scan complete: {total_matches} total matches found")
        return True
    
    def generate_report(self):
        """Generate the hallucination report JSON"""
        # Group results by pattern type for better organization
        grouped_results = {}
        for result in self.results:
            pattern_type = result['pattern_type']
            if pattern_type not in grouped_results:
                grouped_results[pattern_type] = []
            grouped_results[pattern_type].append(result)
        
        # Generate summary statistics
        summary = {
            'total_matches': len(self.results),
            'unique_files_affected': len(set(r['file_path'] for r in self.results)),
            'pattern_types_found': len(grouped_results),
            'patterns_breakdown': {k: len(v) for k, v in grouped_results.items()}
        }
        
        # Create comprehensive report
        report = {
            'scan_metadata': {
                'scan_date': datetime.now().isoformat(),
                'scanner_version': '6.0.0',
                'mapping_file': self.mapping_file,
                'total_patterns_searched': len(self.search_patterns)
            },
            'summary': summary,
            'grouped_results': grouped_results,
            'detailed_results': self.results,
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on scan results"""
        recommendations = []
        
        if len(self.results) == 0:
            recommendations.append("✅ No hallucinated data found in repository")
            return recommendations
        
        # Group by file for recommendations
        files_affected = {}
        for result in self.results:
            file_path = result['file_path']
            if file_path not in files_affected:
                files_affected[file_path] = []
            files_affected[file_path].append(result)
        
        recommendations.append(f"🔧 {len(files_affected)} files require cleanup")
        
        for file_path, matches in files_affected.items():
            pattern_types = set(match['pattern_type'] for match in matches)
            recommendations.append(f"   📁 {file_path}: {len(matches)} matches ({', '.join(pattern_types)})")
        
        recommendations.append("🎯 Priority cleanup order:")
        recommendations.append("   1. README.md and documentation files")
        recommendations.append("   2. Configuration files (.json, .yaml)")
        recommendations.append("   3. Source code files")
        recommendations.append("   4. Template and example files")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any]):
        """Save the report to the specified JSON file"""
        try:
            # Ensure .odin directory exists
            os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
            
            with open(self.report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Report saved to {self.report_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False

def main():
    """Main execution function"""
    scanner = HallucinationScanner()
    
    if scanner.run_scan():
        report = scanner.generate_report()
        scanner.save_report(report)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 HALLUCINATION SCAN SUMMARY")
        print("="*60)
        print(f"Total matches found: {report['summary']['total_matches']}")
        print(f"Files affected: {report['summary']['unique_files_affected']}")
        print(f"Pattern types found: {report['summary']['pattern_types_found']}")
        print("\n📋 Pattern Breakdown:")
        for pattern_type, count in report['summary']['patterns_breakdown'].items():
            print(f"   {pattern_type}: {count} matches")
        print("\n📋 Recommendations:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        print("="*60)
    else:
        print("❌ Scan failed")

if __name__ == "__main__":
    main()
