#!/bin/bash

# JSON Validation Script
# Warning: Do not leave test files (test_invalid.json, etc.) in the repository
# as they will cause validation to fail
echo "🔍 Validating JSON files..."

json_files_found=false
for json_file in $(find . -name "*.json" -type f); do
    json_files_found=true
    echo "Checking $json_file"
    
    if python -m json.tool "$json_file" > /dev/null 2>&1; then
        echo "✅ Valid JSON: $json_file"
    else
        echo "❌ Invalid JSON: $json_file"
        exit 1
    fi
done

if [ "$json_files_found" = false ]; then
    echo "No JSON files found to validate"
else
    echo "✅ All JSON files are valid!"
fi

# Markdown Validation
echo ""
echo "🔍 Checking Markdown files for basic syntax..."

md_files_found=false
for md_file in $(find . -name "*.md" -type f); do
    md_files_found=true
    echo "Checking $md_file"
    
    # Check for unclosed code blocks
    if grep -q '```' "$md_file"; then
        # Count opening and closing code blocks
        opening_blocks=$(grep -c '^```' "$md_file")
        if [ $((opening_blocks % 2)) -ne 0 ]; then
            echo "⚠️  Warning: Possible unclosed code block in $md_file"
        fi
    fi
done

if [ "$md_files_found" = false ]; then
    echo "No Markdown files found to validate"
else
    echo "✅ Markdown validation complete!"
fi

echo ""
echo "🎉 All validations passed!"
