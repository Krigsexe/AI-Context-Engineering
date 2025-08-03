# Change Log

All notable changes to the ODIN Core VS Code extension will be documented in this file.

## [6.0.0] - 2025-01-08

### Added
- Initial release of ODIN Core VS Code extension
- Webview sidebar displaying real-time checkpoint status
- Test coverage percentage monitoring
- Last audit results display
- Integrity hash verification status
- Commands for ODIN CLI integration:
  - `odin.audit` - Run comprehensive project audit
  - `odin.rollback` - Rollback to last checkpoint
  - `odin.testgen` - Generate tests for current file or project
  - `odin.openLearningLog` - Open ODIN's learning log
- Auto-refresh functionality when `.odin` files change
- Configurable refresh intervals
- Native CLI integration using Node child-process
- Status notifications and progress indicators
- Support for ODIN v6.0 features:
  - Semantic Integrity Hash (SIH) monitoring
  - TestGen AI integration  
  - ContextGuard compatibility
  - MCP cache system support
  - DepGuard security analysis
  - Enhanced feedback system

### Features
- Real-time monitoring of ODIN project status
- Visual indicators for project integrity
- One-click access to ODIN commands
- Automatic detection of ODIN-enabled projects
- File system watcher for automatic updates
- Configurable CLI path for custom ODIN installations

### Requirements
- VS Code 1.80.0 or higher
- ODIN CLI v6.0.0 installed and accessible
- Project initialized with ODIN (`odin init`)

### Configuration Options
- `odin.cliPath`: Path to ODIN CLI executable (default: "odin")
- `odin.autoRefresh`: Auto-refresh status on file changes (default: true)
- `odin.refreshInterval`: Refresh interval in milliseconds (default: 5000)
