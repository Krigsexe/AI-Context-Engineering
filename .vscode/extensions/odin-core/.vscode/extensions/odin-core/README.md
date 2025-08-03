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

## Commands Detail

### Audit Project
Runs a comprehensive audit of your project including:
- Code integrity verification (SHA-256 + SIH)
- Test coverage analysis
- Security vulnerability scan
- Documentation completeness check

### Rollback to Last Checkpoint
Safely reverts your project to the last known good state. This will:
- Restore files from the latest backup
- Update integrity hashes
- Refresh project status

### Generate Tests
Automatically generates unit tests for:
- Current file (if editor is focused on a source file)
- Entire project (if no specific file targeted)
- Uses ODIN's TestGen AI for intelligent test creation

### Open Learning Log
Opens ODIN's learning log JSON file showing:
- Successful actions and patterns learned
- Error corrections and fixes applied
- User feedback history
- Knowledge base updates

## Troubleshooting

### Extension Not Activating
- Ensure your project has a `.odin` directory
- Check that ODIN CLI is installed and in PATH
- Restart VS Code

### Commands Not Working
- Verify ODIN CLI path in settings
- Check VS Code output panel for error messages
- Ensure you have proper permissions for the project directory

### Status Not Updating
- Check auto-refresh settings
- Manually click the refresh button
- Verify `.odin/AI_CHECKPOINT.json` exists and is readable

## Contributing

This extension is part of the ODIN v6.0 project. For bugs, feature requests, or contributions:

1. Check the project repository
2. File issues with detailed information
3. Include VS Code version, ODIN version, and error logs

## License

MIT License - Copyright (c) 2025 Make With Passion by Krigs

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.
