# 🚀 ODIN v6.0 - Quick Start Guide

**ODIN v6.0 - Autonomous AI Codebase Assistant (Complete Edition)**  
*Get up and running with ODIN in under 5 minutes*

---

## 📦 Installation

### Method 1: CLI via pip (Recommended)

```bash
# Install ODIN CLI globally
pip install odin-ai

# Verify installation
odin --version
# Expected output: ODIN v6.0.0-COMPLETE
```

### Method 2: VS Code Extension + CLI Bundle

1. **Install VS Code Extension:**
   - Open VS Code
   - Go to Extensions (`Ctrl+Shift+X`)
   - Search for "ODIN Core"
   - Click "Install" on "ODIN Core - Autonomous AI Codebase Assistant"

2. **Install CLI dependency:**
   ```bash
   pip install odin-ai
   ```

### Method 3: Pre-compiled Executables

**Windows:**
```bash
# Download latest release
curl -L https://github.com/Krigsexe/AI-Context-Engineering/releases/download/v6.0.0-complete/odin-windows.exe -o odin.exe

# Add to PATH or use directly
./odin.exe --version
```

**macOS/Linux:**
```bash
# Download and install
curl -L https://github.com/Krigsexe/AI-Context-Engineering/releases/download/v6.0.0-complete/odin-unix.tar.gz | tar -xz
chmod +x odin
sudo mv odin /usr/local/bin/
```

---

## 🏁 Quick Start (3 Steps)

### Step 1: Initialize Your Project

```bash
# Navigate to your project
cd my-awesome-project

# Initialize ODIN (creates .odin/ structure)
odin init

# Output:
# ✅ ODIN v6.0 initialized successfully
# 📁 Created .odin/ scaffold with security schemas
# 🔒 Single instance lock established
# 📊 Initial integrity audit completed
# 🎯 Project ready for autonomous assistance
```

### Step 2: Run Your First Audit

```bash
# Basic health check
odin audit

# Or comprehensive analysis
odin audit --full

# Output:
# 📊 Audit Report Generated: .odin/audit_report.md
# ✅ Integrity: SECURE (SHA-256 + SIH verified)
# 🧪 Test Coverage: 0% (no tests detected)
# 📚 Documentation: Partial (README.md found)
# 🔐 Security: SAFE (no vulnerabilities detected)
```

### Step 3: Experience ODIN's Autonomous Features

**Option A: Via VS Code Extension**
1. Open project in VS Code
2. ODIN sidebar appears automatically
3. Click "Generate Tests" or "Audit Project"
4. Provide feedback: ✅ Perfect / ⚠️ Partial / ❌ False

**Option B: Via CLI**
```bash
# Let ODIN analyze and improve your codebase
odin start --interactive

# Or run specific commands
odin testgen src/utils.js
odin rollback  # If something goes wrong
```

---

## 🛠️ Core Commands Reference

| Command | Description | Usage |
|---------|-------------|--------|
| `odin init` | Initialize ODIN in project | `odin init` |
| `odin audit [--full]` | Health check & analysis | `odin audit --full` |
| `odin rollback` | Restore to last checkpoint | `odin rollback` |
| `odin testgen <file>` | Generate tests for file | `odin testgen src/app.py` |
| `odin start` | Begin autonomous mode | `odin start --interactive` |
| `odin status` | Show current project state | `odin status` |

---

## 🧩 VS Code Extension Features

### 🎛️ ODIN Sidebar Panel
- **Real-time Status**: Integrity, coverage, last audit
- **Quick Actions**: Audit, Rollback, TestGen
- **Learning Log**: View ODIN's decisions and improvements
- **Feedback Buttons**: ✅ / ⚠️ / ❌ for rating ODIN's work

### 📋 Command Palette Integration
Press `Ctrl+Shift+P` and type:
- `ODIN: Audit Project` - Run comprehensive audit
- `ODIN: Rollback to Last Checkpoint` - Emergency restore
- `ODIN: Generate Tests` - Create tests for current file
- `ODIN: Open Learning Log` - View ODIN's learning history

### ⚙️ Configuration Options
```json
// settings.json
{
  "odin.cliPath": "odin",           // Custom CLI path
  "odin.autoRefresh": true,         // Auto-update status
  "odin.refreshInterval": 5000      // Update frequency (ms)
}
```

---

## 🎯 Language & Framework Support

### ✅ Fully Supported

| Language | Framework Examples | Features |
|----------|-------------------|----------|
| **JavaScript** | React, Vue, Express, Next.js | TestGen, AST analysis, dependency tracking |
| **TypeScript** | Angular, NestJS, Svelte | Full type inference, lint integration |
| **Python** | Django, Flask, FastAPI | pytest generation, PEP compliance |
| **Rust** | Actix, Rocket, Tokio | Cargo integration, safety analysis |
| **Go** | Gin, Echo, Fiber | Module awareness, goroutine tracking |
| **Java** | Spring, Quarkus | Maven/Gradle integration, JUnit tests |
| **C#** | .NET, ASP.NET Core | NuGet packages, xUnit generation |
| **PHP** | Laravel, Symfony | Composer integration, PHPUnit tests |

### 🔄 Partially Supported

| Language | Status | Notes |
|----------|--------|-------|
| **Ruby** | ⚠️ Basic | Gem detection, basic test generation |
| **Swift** | ⚠️ Basic | Package.swift parsing, XCTest support |
| **Kotlin** | ⚠️ Basic | Gradle integration, basic analysis |
| **Dart** | ⚠️ Basic | Flutter project detection |

---

## 💻 Platform Compatibility

### ✅ Operating Systems

| OS | CLI Support | VS Code Extension | Pre-built Binary |
|----|-------------|-------------------|-------------------|
| **Windows 10/11** | ✅ Full | ✅ Native | ✅ `.exe` available |
| **macOS 10.15+** | ✅ Full | ✅ Native | ✅ Universal binary |
| **Ubuntu 20.04+** | ✅ Full | ✅ Native | ✅ Static binary |
| **Debian 11+** | ✅ Full | ✅ Native | ✅ Static binary |
| **CentOS/RHEL 8+** | ✅ Full | ✅ Native | ✅ Static binary |
| **Arch Linux** | ✅ Full | ✅ Native | ✅ AUR package |

### 🏗️ Development Environment

| IDE/Editor | Support Level | Extension Available |
|------------|--------------- |-------------------|
| **VS Code** | ✅ Native Extension | ✅ ODIN Core v6.0 |
| **Cursor** | ✅ Compatible | ✅ Same as VS Code |
| **Windsurf** | ✅ Compatible | ✅ Same as VS Code |
| **JetBrains** | 🔄 In Development | ⏳ Coming Q2 2025 |
| **Vim/Neovim** | ⚠️ CLI Only | ❌ Manual integration |
| **Emacs** | ⚠️ CLI Only | ❌ Manual integration |

---

## 🔧 Advanced Configuration

### Project-Level Settings

Create `.odin/config.json`:

```json
{
  "version": "6.0.0",
  "project_name": "my-awesome-app",
  "auto_audit": true,
  "testgen_enabled": true,
  "backup_retention": 10,
  "plugins": {
    "depguard": {
      "enabled": true,
      "alert_level": "high"
    },
    "contextguard": {
      "enabled": true,
      "architecture_tracking": true
    }
  },
  "languages": {
    "javascript": {
      "test_framework": "jest",
      "lint_integration": true
    },
    "python": {
      "test_framework": "pytest",
      "virtual_env": ".venv"
    }
  }
}
```

### Environment Variables

```bash
# Debug mode
export ODIN_DEBUG=1

# Custom cache directory
export ODIN_CACHE_DIR="~/.odin-cache"

# Disable online documentation fetching
export ODIN_OFFLINE_MODE=1

# Custom plugin directory
export ODIN_PLUGINS_PATH="/custom/plugins"
```

---

## 📊 Usage Examples

### Example 1: React Project Setup

```bash
# Create new React project
npx create-react-app my-react-app
cd my-react-app

# Initialize ODIN
odin init

# Let ODIN analyze and improve
odin audit --full
# Generates: test coverage report, security analysis, documentation gaps

# Generate tests for specific component
odin testgen src/App.js
# Creates: src/__tests__/App.test.js with comprehensive test cases

# Start autonomous development mode
odin start --watch
# ODIN monitors changes and maintains code quality automatically
```

### Example 2: Python Flask API

```bash
# Setup Flask project
mkdir flask-api && cd flask-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install flask

# Initialize ODIN
odin init

# Create simple API
echo "from flask import Flask
app = Flask(__name__)

@app.route('/api/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True)" > app.py

# Let ODIN generate comprehensive tests
odin testgen app.py
# Creates: tests/test_app.py with API endpoint tests

# Audit security and best practices
odin audit --full
# Generates: security recommendations, dependency analysis
```

### Example 3: Multi-Language Project

```bash
# Project structure
my-fullstack-app/
├── frontend/     (React + TypeScript)
├── backend/      (Node.js + Express)
├── database/     (PostgreSQL migrations)
└── docs/         (Markdown documentation)

# Initialize ODIN at root
cd my-fullstack-app
odin init

# ODIN detects multi-language setup automatically
odin audit --full
# Analyzes: frontend tests, backend API tests, database integrity

# Generate tests for specific modules
odin testgen frontend/src/components/UserDashboard.tsx
odin testgen backend/src/routes/auth.js

# Monitor entire project
odin start --recursive
# Watches all subdirectories, maintains cross-component integrity
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

**"Another ODIN instance is running"**
```bash
# Check for stale lock files
ls .odin/*.lock
rm .odin/odin.lock  # If stale

# Or force restart
odin init --force
```

**"CLI not found" in VS Code Extension**
```bash
# Ensure ODIN is in PATH
which odin  # Linux/Mac
where odin  # Windows

# Or configure custom path in VS Code
# Settings > Extensions > ODIN Core > CLI Path
```

**"Permission denied on backup creation"**
```bash
# Check directory permissions
ls -la .odin/
chmod 755 .odin/backups/

# Or reinitialize with proper permissions
sudo odin init --reset-permissions
```

**TestGen fails for specific language**
```bash
# Install language-specific dependencies
pip install odin-ai[python]    # Python support
npm install -g odin-js-parser  # JavaScript/TypeScript
```

### Getting Help

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Krigsexe/AI-Context-Engineering/issues)
- 📚 **Documentation**: [odin-ai.dev/docs](https://odin-ai.dev/docs)
- 💬 **Community**: [Discord Server](https://proxitek.fr/invite)
- 📧 **Direct Support**: [contact@makewithpassion.dev](mailto:contact@makewithpassion.dev)

---

## 🎉 What's Next?

1. **Explore ODIN's Learning**: Check `.odin/learning_log.json` to see how ODIN learns from your feedback
2. **Customize Plugins**: Add custom rules in `.odin/plugins/`
3. **Integrate CI/CD**: Use `odin audit` in your GitHub Actions/Jenkins pipelines
4. **Advanced Features**: Try `odin start --autonomous` for fully autonomous development
5. **Share Feedback**: Rate ODIN's suggestions to improve its performance

---

## 📄 License & Support

**MIT License** - Copyright (c) 2025 Make With Passion by Krigs

🎯 **Mission**: Develop, maintain, and document software projects autonomously, reliably, and securely—without external dependencies—while ensuring industrial-grade traceability, reversibility, and system integrity.

---

*Ready to experience autonomous AI development? Start with `odin init` and let ODIN transform your coding workflow!* 🚀
