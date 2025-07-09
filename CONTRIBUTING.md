# Contributing to ODIN

First off, thank you for considering contributing to ODIN! It's people like you who make ODIN such a great tool for democratizing AI development.

## 🌟 Philosophy

ODIN was born from a desire to make AI accessible to everyone. When contributing, please keep in mind:

- **Simplicity over complexity**: Features should be accessible to non-developers
- **Reliability over features**: Better to do less, but do it perfectly
- **Documentation is mandatory**: Every change must be documented
- **Learning from failures**: Mistakes are opportunities to improve

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Version of ODIN prompt used**
- **Environment details** (OS, IDE, LLM used)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use case**: Who will benefit and how?
- **Current workaround**: If any
- **Proposed solution**: Be as specific as possible
- **Alignment with ODIN philosophy**: How does it make AI more accessible?

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Follow the existing structure**: 
   - Prompts go in `prompts/`
   - Documentation in `docs/`
   - Examples in `exemple/`
3. **Test thoroughly**: Ensure your changes work with multiple LLMs
4. **Update documentation**: This is mandatory, not optional
5. **Follow the commit convention** (see below)

## 📝 Commit Message Convention

We follow a simple convention for commit messages:

```
<type>: <description>

[optional body]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Formatting, missing semi colons, etc
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat: add pattern recognition for Python decorators

Added new pattern in ODIN.md to handle Python decorators correctly.
This improves the AI's ability to work with Flask and Django projects.
```

## 🔍 Code Review Process

1. **Automated checks**: Ensure all GitHub Actions pass
2. **Documentation review**: Is everything properly documented?
3. **Philosophy alignment**: Does it fit ODIN's mission?
4. **Community feedback**: Major changes may require community discussion

## 📚 Documentation Standards

- **Bilingual when possible**: French and English (following the project's tradition)
- **Examples are mandatory**: Show, don't just tell
- **Explain the "why"**: Not just what changed, but why it matters
- **Update all affected docs**: Don't leave outdated information

## 🧪 Testing Guidelines

Since ODIN is a prompt engineering framework, "testing" means:

1. **Trying prompts with multiple LLMs** (GPT-4, Claude, local models)
2. **Documenting edge cases** in the `anti_patterns.json`
3. **Getting community feedback** before major changes
4. **Creating examples** that demonstrate the feature

## 🎯 Areas We Need Help With

- **Translations**: Making ODIN accessible in more languages
- **Examples**: Real-world use cases and success stories
- **LLM compatibility**: Testing with different models
- **Documentation**: Always room for clearer explanations
- **Community building**: Spreading the word about ODIN

## ❓ Questions?

Feel free to:
- Open an issue for discussion
- Reach out in the GitHub Discussions
- Tag @Krigsexe in your PR for direct feedback

## 🙏 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- A future CONTRIBUTORS.md file

Remember: **Every contribution, no matter how small, makes AI more accessible to someone, somewhere.**

Thank you for helping democratize AI development! 🚀 