#!/usr/bin/env python3
"""
ODIN v7.0 - Security Review Example

This example demonstrates:
1. Using the SecurityAgent to scan code for vulnerabilities
2. Detecting exposed secrets
3. Getting security recommendations
"""

import asyncio
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import (
    LLMClient,
    InMemoryStateStore,
    SecurityAgent,
    ConfidenceLevel,
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


async def main():
    """Run security review example."""
    print_section("ODIN v7.0 - Security Review Example")

    # Initialize components
    llm_client = LLMClient()
    state_store = InMemoryStateStore()

    # Create security agent
    security = SecurityAgent(llm_client=llm_client, state_store=state_store)
    await security.start()

    print("\n🛡️ Security Agent initialized")

    # Example 1: Check for secrets
    print_section("Example 1: Secret Detection")

    code_with_secrets = '''
import requests

# Configuration
API_KEY = "sk-proj-abc123xyz456def789ghi012jkl345mno678pqr901"
DATABASE_PASSWORD = "super_secret_password_123"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

def call_api():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get("https://api.example.com", headers=headers)
'''

    print("\n🔍 Scanning code for exposed secrets...")

    secrets_result = await security.run_task(
        "check_secrets",
        {"code": code_with_secrets}
    )

    if secrets_result.success:
        data = secrets_result.data
        safe = data.get("safe", True)

        if not safe:
            print(f"\n⚠️ SECRETS DETECTED! Found {data.get('count', 0)} potential secrets:")
            for secret in data.get("secrets_found", []):
                print(f"  🔑 {secret['type']} at line {secret['line']}")
                print(f"     Preview: {secret['matched']}")
        else:
            print("\n✓ No secrets detected")
    else:
        print(f"\n✗ Scan failed: {secrets_result.reasoning}")

    # Example 2: Vulnerability scan
    print_section("Example 2: Vulnerability Scan")

    vulnerable_code = '''
import sqlite3
import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q")
    # SQL Injection vulnerability
    conn = sqlite3.connect("db.sqlite")
    result = conn.execute(f"SELECT * FROM users WHERE name = '{query}'")
    return str(result.fetchall())

@app.route("/run")
def run_command():
    cmd = request.args.get("cmd")
    # Command injection vulnerability
    output = subprocess.check_output(cmd, shell=True)
    return output

@app.route("/greet")
def greet():
    name = request.args.get("name")
    # XSS vulnerability
    return f"<h1>Hello {name}!</h1>"
'''

    print("\n🔍 Scanning code for security vulnerabilities...")

    if llm_client.is_available():
        vuln_result = await security.run_task(
            "scan_vulnerabilities",
            {
                "code": vulnerable_code,
                "language": "python",
            }
        )

        if vuln_result.success:
            data = vuln_result.data
            print(f"\n📊 Scan Results (Confidence: {vuln_result.confidence.name})")
            print(f"   Risk Level: {data.get('risk_level', 'unknown').upper()}")
            print(f"   Vulnerabilities Found: {data.get('vulnerability_count', 0)}")

            for vuln in data.get("vulnerabilities", [])[:5]:
                print(f"\n   🚨 {vuln.get('type', 'Unknown')}")
                print(f"      Severity: {vuln.get('severity', 'unknown')}")
                print(f"      Line: {vuln.get('line', '?')}")
                print(f"      Description: {vuln.get('description', '')[:100]}")
        else:
            print(f"\n✗ Scan failed: {vuln_result.reasoning}")
    else:
        print("\n⚠️ LLM not available - vulnerability scanning requires LLM")
        print("   Configure an LLM provider to enable this feature")

    # Example 3: Full security review
    print_section("Example 3: Comprehensive Security Review")

    if llm_client.is_available():
        print("\n🔍 Running comprehensive security review...")

        review_result = await security.run_task(
            "security_review",
            {
                "code": vulnerable_code,
                "language": "python",
            }
        )

        if review_result.success:
            data = review_result.data
            print(f"\n📋 Security Review Summary")
            print(f"   Overall Risk: {data.get('risk_level', 'unknown').upper()}")
            print(f"   Issues Found: {len(data.get('issues', []))}")
            print(f"   Secrets Detected: {data.get('secrets_detected', False)}")

            if data.get("recommendations"):
                print("\n📌 Recommendations:")
                for rec in data["recommendations"]:
                    print(f"   • {rec}")
        else:
            print(f"\n✗ Review failed: {review_result.reasoning}")
    else:
        print("\n⚠️ Skipping - LLM required for comprehensive review")

    # Example 4: Safe code example
    print_section("Example 4: Safe Code Verification")

    safe_code = '''
import sqlite3
from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q")
    # Safe: Using parameterized queries
    conn = sqlite3.connect("db.sqlite")
    result = conn.execute(
        "SELECT * FROM users WHERE name = ?",
        (query,)
    )
    return str(result.fetchall())

@app.route("/greet")
def greet():
    name = request.args.get("name")
    # Safe: Escaping user input
    return f"<h1>Hello {escape(name)}!</h1>"
'''

    print("\n🔍 Scanning secure code for secrets...")

    safe_result = await security.run_task(
        "check_secrets",
        {"code": safe_code}
    )

    if safe_result.success and safe_result.data.get("safe"):
        print("\n✓ No secrets or obvious vulnerabilities detected")
        print("  This code follows better security practices:")
        print("  • Parameterized SQL queries (prevents SQL injection)")
        print("  • HTML escaping (prevents XSS)")
        print("  • No hardcoded credentials")

    # Cleanup
    await security.stop()

    print_section("Security Best Practices")
    print("""
ODIN Security Agent checks for:

🔐 OWASP Top 10:
   • Injection (SQL, Command, XSS)
   • Broken Authentication
   • Sensitive Data Exposure
   • Security Misconfiguration
   • And more...

🔑 Secret Detection:
   • API keys
   • Passwords
   • AWS credentials
   • Private keys
   • Tokens

💡 Always:
   • Use parameterized queries
   • Escape user input
   • Store secrets in environment variables
   • Use secret management tools
""")

    print("\nExample complete!")


if __name__ == "__main__":
    asyncio.run(main())
