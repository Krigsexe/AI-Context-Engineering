# ODIN v6.0 CLI - Autonomous AI Codebase Assistant

[![Version](https://img.shields.io/badge/version-6.0.0-blue.svg)](https://github.com/makewithpassion/odin-ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://python.org)

ODIN v6.0 Command Line Interface provides cross-platform access to the Autonomous AI Codebase Assistant functionality through three core commands: `init`, `audit`, and `rollback`.

## 🚀 Quick Start

### Installation via pip

```bash
pip install odin-ai
```

### Using pre-compiled executable (Windows)

Download the latest `odin.exe` from releases and add it to your PATH.

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

## 🌐 Cross-Platform Support

| Platform | Support | Installation Method |
|----------|---------|-------------------|
| Windows | ✅ Full | `pip install` or `.exe` |
| macOS | ✅ Full | `pip install` or build from source |
| Linux | ✅ Full | `pip install` or build from source |

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
