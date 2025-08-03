#!/usr/bin/env python3
"""
DepGuard Plugin for ODIN v6.0
Offline CVE DB loader, manifest resolver, and severity matrix.
Includes online documentation verification capability.
"""

import json
import hashlib
import requests
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class DepGuard:
    """
    DepGuard plugin for dependency vulnerability analysis and 
    online documentation verification.
    """
    
    def __init__(self, config_path: str):
        """Initialize DepGuard with configuration."""
        self.config_path = Path(config_path)
        self.config = {}
        self.cve_data = {}
        self.docs_cache = {}
        self.load_config()
        
    def load_config(self) -> None:
        """Load DepGuard configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            # Create default config if not exists
            self.config = {
                "vulnerability_db": ".odin/cache/cve-offline.json",
                "auto_update": False,
                "alert_levels": {
                    "critical": True,
                    "high": True,
                    "medium": "notify",
                    "low": False
                },
                "official_doc_sources": {
                    "npm": "https://registry.npmjs.org/",
                    "pypi": "https://pypi.org/pypi/",
                    "crates": "https://crates.io/api/v1/crates/",
                    "cargo": "https://doc.rust-lang.org/cargo/"
                },
                "cache_directory": ".odin/docs_cache/"
            }
            self._save_config()
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        os.makedirs(self.config_path.parent, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, indent=2)
    
    def load_cve_db(self) -> None:
        """Load offline CVE database and verify online documentation."""
        self.verify_online_docs()  # Verify documentation before loading CVE
        
        cve_path = Path(self.config.get("vulnerability_db", ".odin/cache/cve-offline.json"))
        
        if cve_path.exists():
            try:
                with open(cve_path, 'r', encoding='utf-8') as file:
                    self.cve_data = json.load(file)
                print(f"✅ Loaded CVE database: {len(self.cve_data)} entries")
            except json.JSONDecodeError as e:
                print(f"❌ Error loading CVE database: {e}")
                self.cve_data = {}
        else:
            print("⚠️ CVE database not found, creating empty database")
            self.cve_data = {}
            self._create_sample_cve_db(cve_path)

    def _create_sample_cve_db(self, path: Path) -> None:
        """Create a sample CVE database for testing."""
        path.parent.mkdir(parents=True, exist_ok=True)
        sample_cve = {
            "CVE-2024-12345": {
                "package": "lodash",
                "versions": ["<4.17.21"],
                "severity": "high",
                "description": "Prototype pollution vulnerability"
            },
            "CVE-2024-54321": {
                "package": "axios",
                "versions": ["<1.6.0"],
                "severity": "medium",
                "description": "Request smuggling vulnerability"
            }
        }
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(sample_cve, file, indent=2)
    
    def verify_online_docs(self) -> Dict[str, bool]:
        """
        Verify official documentation online for codebase dependencies.
        Caches documentation locally for offline use.
        """
        print("🌐 Connecting to official documentation sources...")
        
        verification_results = {}
        doc_sources = self.config.get("official_doc_sources", {})
        cache_dir = Path(self.config.get("cache_directory", ".odin/docs_cache/"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        for platform, base_url in doc_sources.items():
            try:
                # Test connection to documentation source
                response = requests.get(base_url, timeout=10)
                if response.status_code == 200:
                    verification_results[platform] = True
                    print(f"✅ {platform} documentation accessible")
                    
                    # Cache documentation index
                    cache_file = cache_dir / f"{platform}_index.json"
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "url": base_url,
                            "verified": datetime.now().isoformat(),
                            "status": "accessible"
                        }, f, indent=2)
                else:
                    verification_results[platform] = False
                    print(f"⚠️ {platform} documentation returned status {response.status_code}")
                    
            except requests.RequestException as e:
                verification_results[platform] = False
                print(f"❌ Failed to access {platform} documentation: {e}")
                # Use cached documentation if available
                cache_file = cache_dir / f"{platform}_index.json"
                if cache_file.exists():
                    print(f"📁 Using cached {platform} documentation")
                    verification_results[platform] = "cached"
        
        return verification_results
    
    def resolve_manifests(self, manifest_files: List[str]) -> Dict[str, Dict]:
        """
        Resolve package manifests for npm, pip, Cargo, and Crates.
        """
        resolved = {}
        
        for manifest_file in manifest_files:
            manifest_path = Path(manifest_file)
            
            if not manifest_path.exists():
                print(f"⚠️ Manifest file not found: {manifest_file}")
                continue
                
            if manifest_path.name == "package.json":
                resolved[manifest_file] = self._resolve_npm_manifest(manifest_path)
            elif manifest_path.name in ["requirements.txt", "Pipfile", "pyproject.toml"]:
                resolved[manifest_file] = self._resolve_python_manifest(manifest_path)
            elif manifest_path.name == "Cargo.toml":
                resolved[manifest_file] = self._resolve_cargo_manifest(manifest_path)
            else:
                print(f"⚠️ Unknown manifest type: {manifest_file}")
                
        return resolved
    
    def _resolve_npm_manifest(self, manifest_path: Path) -> Dict:
        """Resolve npm package.json dependencies."""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as file:
                package_data = json.load(file)
            
            dependencies = {}
            for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
                if dep_type in package_data:
                    dependencies.update(package_data[dep_type])
            
            return {
                "type": "npm",
                "dependencies": dependencies,
                "resolved_count": len(dependencies)
            }
        except Exception as e:
            print(f"❌ Error resolving npm manifest: {e}")
            return {"type": "npm", "error": str(e)}
    
    def _resolve_python_manifest(self, manifest_path: Path) -> Dict:
        """Resolve Python requirements."""
        try:
            dependencies = {}
            
            if manifest_path.name == "requirements.txt":
                with open(manifest_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Simple parsing - could be enhanced
                            if '==' in line:
                                package, version = line.split('==', 1)
                                dependencies[package.strip()] = version.strip()
                            else:
                                dependencies[line] = "latest"
            
            return {
                "type": "python",
                "dependencies": dependencies,
                "resolved_count": len(dependencies)
            }
        except Exception as e:
            print(f"❌ Error resolving Python manifest: {e}")
            return {"type": "python", "error": str(e)}
    
    def _resolve_cargo_manifest(self, manifest_path: Path) -> Dict:
        """Resolve Cargo.toml dependencies."""
        try:
            # Simple TOML parsing - in production, use proper TOML library
            dependencies = {}
            
            with open(manifest_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Basic parsing for dependencies section
                in_deps = False
                for line in content.split('\n'):
                    line = line.strip()
                    if line == '[dependencies]':
                        in_deps = True
                        continue
                    elif line.startswith('[') and in_deps:
                        in_deps = False
                        continue
                    elif in_deps and '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) == 2:
                            package = parts[0].strip()
                            version = parts[1].strip().strip('"\'')
                            dependencies[package] = version
            
            return {
                "type": "cargo",
                "dependencies": dependencies,
                "resolved_count": len(dependencies)
            }
        except Exception as e:
            print(f"❌ Error resolving Cargo manifest: {e}")
            return {"type": "cargo", "error": str(e)}
    
    def check_severity(self, package_data: Dict) -> Dict[str, Any]:
        """
        Check severity against CVE database and configuration matrix.
        """
        package_name = package_data.get("name", "")
        package_version = package_data.get("version", "")
        
        vulnerabilities = []
        max_severity = "none"
        
        # Check against CVE database
        for cve_id, cve_info in self.cve_data.items():
            if cve_info.get("package") == package_name:
                # Simple version matching - could be enhanced with proper semver
                if self._version_matches(package_version, cve_info.get("versions", [])):
                    vulnerability = {
                        "cve_id": cve_id,
                        "severity": cve_info.get("severity", "unknown"),
                        "description": cve_info.get("description", "")
                    }
                    vulnerabilities.append(vulnerability)
                    
                    # Update max severity
                    severity_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1, "none": 0}
                    current_level = severity_levels.get(cve_info.get("severity", "none"), 0)
                    max_level = severity_levels.get(max_severity, 0)
                    if current_level > max_level:
                        max_severity = cve_info.get("severity", "none")
        
        # Check alert configuration
        alert_config = self.config.get("alert_levels", {})
        should_alert = alert_config.get(max_severity, False)
        
        return {
            "package": package_name,
            "version": package_version,
            "vulnerabilities": vulnerabilities,
            "max_severity": max_severity,
            "should_alert": should_alert,
            "vulnerability_count": len(vulnerabilities)
        }
    
    def _version_matches(self, version: str, vulnerable_versions: List[str]) -> bool:
        """
        Simple version matching logic.
        In production, use proper semantic versioning library.
        """
        for vuln_version in vulnerable_versions:
            if vuln_version.startswith('<'):
                # Simple comparison - enhance with proper semver
                target_version = vuln_version[1:].strip()
                if version < target_version:
                    return True
            elif vuln_version == version:
                return True
        return False

