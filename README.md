# 🤖 ODIN v6.0 - Autonomous AI Codebase Assistant (Complete Edition)

[![Version](https://img.shields.io/badge/version-6.0.0--COMPLETE-blue.svg)](https://github.com/makewithpassion/odin-ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://python.org)
[![CLI](https://img.shields.io/badge/CLI-Cross--Platform-green.svg)](https://pypi.org/project/odin-ai/)
[![VS Code](https://img.shields.io/badge/VS%20Code-Extension-blue.svg)](https://marketplace.visualstudio.com/items?itemName=make-with-passion-by-krigs.odin-core)

**ODIN v6.0** is a revolutionary autonomous AI codebase assistant that develops, maintains, and documents software projects with industrial-grade reliability, security, and traceability. Operating entirely offline with no external dependencies, ODIN provides comprehensive project management through both CLI and native IDE integration.

## 🚀 Quick Start

> **📚 Need detailed setup instructions?** See **[QUICKSTART.md](QUICKSTART.md)** for comprehensive 5-minute setup guide.

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
   - Open VS Code → Extensions (`Ctrl+Shift+X`)
   - Search for "**ODIN Core**"
   - Install "**ODIN Core - Autonomous AI Codebase Assistant**"

2. **Install CLI dependency:**
   ```bash
   pip install odin-ai
   ```

### Method 3: Pre-compiled Executables

**Windows:**
```bash
curl -L https://github.com/makewithpassion/odin-ai/releases/download/v6.0.0-complete/odin-windows.exe -o odin.exe
./odin.exe --version
```

**macOS/Linux:**
```bash
curl -L https://github.com/makewithpassion/odin-ai/releases/download/v6.0.0-complete/odin-unix.tar.gz | tar -xz
chmod +x odin && sudo mv odin /usr/local/bin/
```

## 📋 Commands

### `odin init`

Initialize a new ODIN-managed project:
- Runs single-instance check
- Creates `.odin/` scaffold if missing  
- Performs first integrity audit

```bash
cd my-project/
odin init
```

### `odin audit [--full]`

Run project health audit:
- Standard audit: basic integrity and quality checks
- Full audit: comprehensive analysis with detailed reporting

```bash
# Standard audit
odin audit

# Full comprehensive audit  
odin audit --full
```

### `odin rollback`

Restore from last valid backup:
- Selects most recent valid backup
- Restores project to known good state
- Maintains integrity throughout process

```bash
odin rollback
```

## 🏗️ Project Structure

After running `odin init`, your project will have:

```
your-project/
├── .odin/
│   ├── AI_CHECKPOINT.json    # Main state tracking
│   ├── config.json           # Configuration
│   ├── learning_log.json     # Learning history
│   ├── audit_report.md       # Latest audit results
│   ├── odin.lock            # Instance lock file
│   └── backups/             # Atomic backups
├── [your project files...]
```

## 🔧 Development Setup

### From Source

```bash
# Clone repository
git clone https://github.com/Krigsexe/AI-Context-Engineering
cd odin-ai

# Install in development mode
pip install -e .

# Run directly
python -m odin --help
```

### Building Executables

```bash
# Windows
scripts/build_windows.bat

# Linux/Mac  
chmod +x scripts/build_unix.sh
./scripts/build_unix.sh
```

## 🔒 Security & Integrity

ODIN v6.0 implements multiple layers of security:

- **Single Instance Enforcement**: Prevents conflicts via lock files
- **Atomic Operations**: All changes are backed up before execution  
- **Integrity Verification**: SHA-256 + Semantic Integrity Hash (SIH)
- **Rollback Safety**: Always recoverable to last known good state

## 🧩 Core Plugins & Commands

ODIN's functionality is extended through a powerful plugin system and a versatile set of commands.

### VS Code Extension: ODIN Core
- **Interactive Sidebar**: Real-time status, one-click actions (Audit, Rollback, TestGen), and feedback.
- **Command Palette**: Access all core commands directly within the editor.
- **Auto-Refresh**: Keeps project status constantly updated.

| Command | Description |
|---|---|
| `odin.audit` | Run comprehensive project audit |
| `odin.rollback` | Revert to previous valid state |
| `odin.testgen` | Auto-generate tests for current file |
| `odin.openLearningLog` | View ODIN's learning history |

### 🎯 Core CLI Commands

| Command | Description | Example |
|---|---|---|
| `odin init` | Initialize ODIN in your project | `odin init` |
| `odin audit [--full]`| Run a health check and analysis | `odin audit --full` |
| `odin rollback` | Restore the project to the last valid checkpoint | `odin rollback` |
| `odin testgen <file>` | Generate tests for a specific file | `odin testgen src/app.py` |
| `odin start` | Start autonomous mode | `odin start --interactive` |

## 💻 Compatibility

ODIN is designed for broad compatibility across operating systems, languages, and development environments.

### Operating Systems

| OS | CLI Support | VS Code Extension | Pre-built Binary |
|---|---|---|---|
| **Windows 10/11** | ✅ Full | ✅ Native | ✅ `.exe` available |
| **macOS 10.15+** | ✅ Full | ✅ Native | ✅ Universal binary |
| **Ubuntu 20.04+** | ✅ Full | ✅ Native | ✅ Static binary |

### Supported Languages

| Language | Feature Support |
|---|---|
| **JavaScript / TypeScript** | ✅ Full (TestGen, AST Analysis, Linting) |
| **Python** | ✅ Full (Pytest/Unittest Generation, PEP Compliance) |
| **Rust / Go / Java / C# / PHP** | ✅ Full (Build Tool Integration, Test Generation) |
| **Ruby / Swift / Kotlin / Dart** | ⚠️ Basic (Dependency Detection, Basic Analysis) |

## 📖 Examples

### Initialize new project
```bash
mkdir my-ai-project
cd my-ai-project
odin init
# ✅ ODIN scaffold created, first audit completed
```

### Run health check
```bash
odin audit --full
# 📊 Comprehensive audit report generated at .odin/audit_report_full.md
```

### Emergency rollback
```bash
odin rollback  
# 🔄 Project restored to last valid backup
```

## 🔍 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ODIN_DEBUG` | Enable debug output | `false` |
| `ODIN_CLI_MODE` | CLI mode indicator | `1` (auto-set) |

## 🐛 Troubleshooting

### Common Issues

**"Another ODIN instance is running"**
```bash
# Check for stale lock files
rm .odin/odin.lock*
```

**"No backups available for rollback"**
```bash
# Initialize ODIN first
odin init
```

**Import errors during development**
```bash
# Ensure proper installation
pip install -e .
```

## 📄 License

MIT License - Copyright 2025 Make With Passion by Krigs

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/makewithpassion/odin-ai/issues)
- 📚 **Documentation**: [odin-ai.dev/docs](https://odin-ai.dev/docs)
- 💬 **Community**: [Discord](https://proxitek.fr/invite)

---

**ODIN v6.0** - *Autonomous AI Codebase Assistant (Complete Edition)*  
Copyright 2025 Make With Passion by Krigs
