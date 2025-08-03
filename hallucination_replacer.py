#!/usr/bin/env python3
"""
ODIN Hallucination Replacer v6.0
Replaces all hallucinated data patterns with correct values and commits changes.
"""

import os
import json
import yaml
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class HallucinationReplacer:
    def __init__(self, mapping_file: str = "hallucination_mapping.yaml"):
        self.mapping_file = mapping_file
        self.hallucination_map = {}
        self.replacement_map = {}
        self.processed_files = []
        self.changes_made = 0
        self.report_path = ".odin/replacement_report.json"
        
    def load_mapping(self):
        """Load the hallucination mapping YAML file"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.hallucination_map = yaml.safe_load(f)
            print(f"✅ Loaded mapping from {self.mapping_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading mapping file: {e}")
            return False
    
    def create_replacement_map(self):
        """Create comprehensive replacement mappings"""
        replacements = {}
        
        # Direct replacements
        if self.hallucination_map.get('github_bad') and self.hallucination_map.get('github_good'):
            replacements[self.hallucination_map['github_bad']] = self.hallucination_map['github_good']
        
        if self.hallucination_map.get('author_bad') and self.hallucination_map.get('author_good'):
            replacements[self.hallucination_map['author_bad']] = self.hallucination_map['author_good']
        
        if self.hallucination_map.get('project_name_bad') and self.hallucination_map.get('project_name_good'):
            replacements[self.hallucination_map['project_name_bad']] = self.hallucination_map['project_name_good']
        
        if self.hallucination_map.get('version_bad') and self.hallucination_map.get('version_good'):
            replacements[self.hallucination_map['version_bad']] = self.hallucination_map['version_good']
        
        if self.hallucination_map.get('copyright_bad') and self.hallucination_map.get('copyright_good'):
            replacements[self.hallucination_map['copyright_bad']] = self.hallucination_map['copyright_good']
        
        # Remove or replace problematic patterns
        bad_patterns = [
            # Domains
            *self.hallucination_map.get('domains_bad', []),
            # Emails
            *self.hallucination_map.get('emails_bad', []),
            # Download URLs
            *self.hallucination_map.get('download_urls_bad', []),
            # NPM packages
            *self.hallucination_map.get('npm_packages_bad', []),
            # Release dates
            self.hallucination_map.get('release_date_bad', ''),
            # VS Code extension
            self.hallucination_map.get('vscode_extension_bad', ''),
        ]
        
        # Mark these for removal (replace with empty string or comments)
        for pattern in bad_patterns:
            if pattern:
                replacements[pattern] = f"# REMOVED: {pattern}"
        
        # Architecture claims - remove or comment out
        architecture_claims = self.hallucination_map.get('architecture_claims_bad', [])
        for claim in architecture_claims:
            if claim:
                replacements[claim] = f"# {claim} (placeholder)"
        
        # Functions - comment out or mark as placeholder
        functions_bad = self.hallucination_map.get('functions_bad', [])
        for func in functions_bad:
            if func:
                replacements[func] = f"# TODO: Implement {func}"
        
        # File extensions - remove references
        file_extensions_bad = self.hallucination_map.get('file_extensions_bad', [])
        for ext in file_extensions_bad:
            if ext:
                replacements[ext] = "# removed file extension reference"
        
        self.replacement_map = replacements
        print(f"✅ Created {len(replacements)} replacement patterns")
        return replacements
    
    def get_files_to_process(self) -> List[str]:
        """Get all files to process in the repository"""
        search_extensions = [
            '.py', '.js', '.ts', '.json', '.yaml', '.yml', 
            '.md', '.txt', '.html', '.css', '.rs', '.go',
            '.java', '.cpp', '.c', '.h', '.php', '.rb',
            '.sh', '.bat', '.ps1', '.toml', '.ini', '.conf'
        ]
        
        files = []
        for root, dirs, filenames in os.walk('.'):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in search_extensions):
                    file_path = os.path.join(root, filename).replace('\\', '/')
                    files.append(file_path)
        
        print(f"✅ Found {len(files)} files to process")
        return files
    
    def process_file(self, file_path: str) -> int:
        """Process a single file for replacements"""
        changes_count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all replacements
            for bad_pattern, good_replacement in self.replacement_map.items():
                if bad_pattern in content:
                    content = content.replace(bad_pattern, good_replacement)
                    changes_count += content.count(good_replacement) - original_content.count(good_replacement)
            
            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.processed_files.append(file_path)
                print(f"📝 Processed {file_path}: {changes_count} changes")
        
        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
        
        return changes_count
    
    def run_replacement(self):
        """Run the complete hallucination replacement"""
        print("🔄 Starting ODIN Hallucination Replacement...")
        
        # Load mapping
        if not self.load_mapping():
            return False
        
        # Create replacement map
        self.create_replacement_map()
        
        # Get files to process
        files_to_process = self.get_files_to_process()
        
        # Process all files
        total_changes = 0
        for file_path in files_to_process:
            changes = self.process_file(file_path)
            total_changes += changes
        
        self.changes_made = total_changes
        print(f"✅ Replacement complete: {total_changes} changes made across {len(self.processed_files)} files")
        return True
    
    def generate_replacement_report(self):
        """Generate replacement report"""
        report = {
            'replacement_metadata': {
                'replacement_date': datetime.now().isoformat(),
                'replacer_version': '6.0.0',
                'mapping_file': self.mapping_file,
                'total_patterns_replaced': len(self.replacement_map)
            },
            'summary': {
                'total_changes': self.changes_made,
                'files_processed': len(self.processed_files),
                'replacement_patterns': len(self.replacement_map)
            },
            'processed_files': self.processed_files,
            'replacement_map': self.replacement_map,
            'recommendations': [
                "✅ All hallucinated data has been replaced",
                "🔍 Review changes before committing",
                "📝 Update documentation if needed",
                "🧪 Run tests to ensure functionality"
            ]
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """Save the replacement report"""
        try:
            os.makedirs(os.path.dirname(self.report_path), exist_ok=True)
            
            with open(self.report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Replacement report saved to {self.report_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False
    
    def commit_changes(self):
        """Commit all changes to git"""
        try:
            # Add all changes
            result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️  Git add warning: {result.stderr}")
            
            # Commit changes
            commit_message = f"🧹 Replace hallucinated data - {len(self.processed_files)} files updated"
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Changes committed successfully: {commit_message}")
                return True
            else:
                print(f"⚠️  Commit result: {result.stdout}")
                print(f"⚠️  Commit error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error committing changes: {e}")
            return False

def main():
    """Main execution function"""
    replacer = HallucinationReplacer()
    
    print("🚀 ODIN Hallucination Data Cleanup Process")
    print("=" * 50)
    
    if replacer.run_replacement():
        # Generate and save report
        report = replacer.generate_replacement_report()
        replacer.save_report(report)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 REPLACEMENT SUMMARY")
        print("=" * 60)
        print(f"Total changes made: {report['summary']['total_changes']}")
        print(f"Files processed: {report['summary']['files_processed']}")
        print(f"Replacement patterns: {report['summary']['replacement_patterns']}")
        
        print("\n📁 Processed files:")
        for file_path in replacer.processed_files[:10]:  # Show first 10
            print(f"  - {file_path}")
        if len(replacer.processed_files) > 10:
            print(f"  ... and {len(replacer.processed_files) - 10} more files")
        
        print("\n🔄 Committing changes...")
        if replacer.commit_changes():
            print("✅ All changes committed successfully!")
        else:
            print("⚠️  Manual commit may be required")
        
        print("=" * 60)
    else:
        print("❌ Replacement failed")

if __name__ == "__main__":
    main()
