# ODIN Framework - Validation Scripts

This directory contains validation scripts for the ODIN framework.

## Scripts

### `validate.sh`
Validates JSON and Markdown files in the repository:
- **JSON Validation**: Checks syntax using `python -m json.tool`
- **Markdown Validation**: Basic syntax checks for code blocks

### Usage
```bash
chmod +x .github/scripts/validate.sh
.github/scripts/validate.sh
```

### Exit Codes
- `0`: All validations passed
- `1`: JSON validation failed
- `2`: Script error

### Requirements
- Python 3.x (for JSON validation)
- Bash (for script execution)
