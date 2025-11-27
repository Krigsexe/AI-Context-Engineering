# 🚀 Setup Guide - ODIN Framework

## Prerequisites

- Node.js 18+
- pnpm 8+
- Git

## Development Setup

### 1. Install Dependencies

```bash
cd odin-framework
pnpm install
```

### 2. Build CLI Package

```bash
cd packages/cli
pnpm build
```

### 3. Link CLI Locally (for testing)

```bash
pnpm link --global
```

Now you can use `odin` command globally!

### 4. Test CLI

```bash
# In any project directory
odin init

# Check status
odin status

# View agents
odin agents --verbose
```

## Known Issues

### better-sqlite3 Build Error

We switched from `better-sqlite3` to `sql.js` to avoid native compilation issues on Windows.

**If you still see build errors:**

1. Make sure you have the latest package.json
2. Remove node_modules: `rm -rf node_modules`
3. Reinstall: `pnpm install`

### TypeScript Errors

Some minor TypeScript lint warnings exist. These are non-breaking:

- Missing null checks in some commands
- Provider type indexing

**Fix planned**: Will be addressed in next iteration.

## Project Structure

```
odin-framework/
├── apps/
│   ├── web/              # Next.js website (Turborepo created)
│   └── docs/             # Docs app
├── packages/
│   ├── cli/              # ✅ CLI tool (COMPLETED)
│   │   ├── src/
│   │   │   ├── commands/     # CLI commands
│   │   │   ├── utils/        # Utilities
│   │   │   ├── types/        # TypeScript types
│   │   │   └── index.ts      # Entry point
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── tsup.config.ts
│   ├── core/             # Shared logic (TODO)
│   ├── patch/            # Patch templates (TODO)
│   ├── eslint-config/    # ESLint config
│   ├── typescript-config/# TS config
│   └── ui/               # Shared UI components
├── docs/                 # Markdown documentation
│   ├── index.md
│   ├── getting-started/
│   ├── concepts/
│   ├── cli/
│   └── api/
├── package.json
├── pnpm-workspace.yaml
├── turbo.json
├── README.md
└── IMPLEMENTATION_STATUS.md
```

## Development Workflow

### Build All Packages

```bash
pnpm build
```

### Develop CLI

```bash
cd packages/cli
pnpm dev  # Watch mode
```

### Lint

```bash
pnpm lint
```

### Add New Command

1. Create file in `packages/cli/src/commands/new-command.ts`
2. Export a `Command` object
3. Import and add in `packages/cli/src/index.ts`
4. Rebuild: `pnpm build`

## Testing ODIN Installation

### Test in a Sample Project

```bash
# Create test project
mkdir test-project
cd test-project

# Create .claude directory (simulate Claude usage)
mkdir .claude

# Initialize ODIN
odin init

# Follow prompts
# Select provider: Ollama (for testing without API key)

# Check what was created
ls -la .claude/odin/

# View status
odin status

# View configuration
odin config
```

## Environment Variables

### For Cloud Providers

If you select a cloud provider (not Ollama), set the appropriate API key:

```bash
# Anthropic (Claude)
export ANTHROPIC_API_KEY="your-key-here"

# OpenAI
export OPENAI_API_KEY="your-key-here"

# Google (Gemini)
export GOOGLE_API_KEY="your-key-here"

# Groq
export GROQ_API_KEY="your-key-here"

# etc.
```

## Next Steps

1. ✅ CLI core is complete
2. 🚧 Next: Build Next.js website (`apps/web`)
3. 🚧 Create documentation pages
4. 🚧 Deploy to Vercel
5. 🚧 Publish CLI to npm

## Troubleshooting

### CLI not found after `pnpm link`

```bash
# Re-link
cd packages/cli
pnpm unlink
pnpm link --global
```

### Permission errors on Windows

Run PowerShell as Administrator

### Module not found errors

```bash
# Clear and reinstall
pnpm store prune
rm -rf node_modules
pnpm install
```

## Publishing (Future)

```bash
# Bump version
cd packages/cli
npm version patch

# Publish to npm
npm publish --access public
```

Users will then install with:

```bash
npx @odin/cli init
```

---

**Questions?** Open an issue on GitHub!
