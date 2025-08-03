# ODIN Core VS Code Extension

The official VS Code extension for ODIN v6.0 - Autonomous AI Codebase Assistant.

## Features

### 🖥️ Webview Sidebar
- Real-time checkpoint status monitoring
- Test coverage percentage display
- Last audit results
- Integrity hash verification status
- Backup tracking

### 🎛️ Commands
- **ODIN: Audit Project** - Run comprehensive project audit
- **ODIN: Rollback to Last Checkpoint** - Revert to previous valid state
- **ODIN: Generate Tests** - Auto-generate tests for current file or project
- **ODIN: Open Learning Log** - View ODIN's learning history

### 🔧 Features
- Auto-refresh status when `.odin` files change
- Configurable refresh intervals
- Native CLI integration using Node child-process
- Status notifications and progress indicators

## Requirements

- VS Code 1.80.0 or higher
- ODIN CLI v6.0.0 installed and accessible in PATH
- Project initialized with ODIN (`odin init`)

## Installation

1. Install from VS Code Extension Marketplace
2. Or install manually from `.vsix` file:
   ```bash
   code --install-extension odin-core-6.0.0.vsix
   ```

## Configuration

The extension can be configured via VS Code settings:

```json
{
  "odin.cliPath": "odin",           // Path to ODIN CLI executable
  "odin.autoRefresh": true,         // Auto-refresh status on file changes
  "odin.refreshInterval": 5000      // Refresh interval in milliseconds
}
```

## Usage

1. Open a project with ODIN initialized (`.odin` directory exists)
2. The ODIN sidebar will appear automatically
3. Use the command palette (`Ctrl+Shift+P`) to access ODIN commands:
   - Type "ODIN:" to see all available commands
4. Click the refresh button in the sidebar to manually update status

## License

MIT License - Copyright (c) 2025 Make With Passion by Krigs
