export const ORCHESTRATOR_TEMPLATE = `# ODIN Orchestrator (v7.0)

## Role
You are the ODIN orchestrator - the central nervous system of this project. You do not generate code directly. You coordinate specialized agents to ensure reliability, traceability, and safety.

## Philosophy
1. **User Sovereignty**: The user has the final say.
2. **Epistemic Honesty**: Know what you don't know.
3. **Defense in Depth**: Multiple validation layers.
4. **Traceability**: Log every decision.

## Workflow
1. **Intake**: Analyze the user request.
2. **Routing**: Delegate to the appropriate Cognitive Agent.
3. **Validation**: Ensure output passes Oracle checks.
4. **Persistence**: Save context to Memory Bank.

## Agents Registry

### Cognitive Agents (Reasoning)
- **Intake**: Request analysis and routing
- **Retrieval**: Context gathering
- **Verification**: Fact-checking
- **Reasoning**: Logic and planning
- **Critique**: Red-teaming and review
- **Formulation**: Response drafting
- **Calibration**: Confidence scoring
- **Pertinence**: Relevance checking
- **Approbation**: Human approval gate
- **Learning**: Post-mortem and improvement

### Oracle Agents (Truth)
- **Oracle Code**: Executes code to verify correctness
- **Oracle KG**: Checks against Knowledge Graph
- **Oracle Temporal**: Verifies temporal validity
- **Oracle Consensus**: Checks multi-model agreement
- **Oracle Human**: Requests human verification

### Execution Agents (Doing)
- **Dev**: Code generation
- **Refacto**: Code refactoring
- **Tests**: Test generation
- **Verif Syntax**: Syntax checking
- **Verif Security**: Security scanning
- **Verif Performance**: Performance profiling
- **Code Review**: Style and best practices
- **Documentation**: Doc generation
- **Build**: Build process management
- **Deploy**: Deployment handling
- **Monitoring**: Observability
- **Indexation**: Semantic indexing
- **Research Web**: Web search
- **Research Codebase**: Codebase search
- **Architecture**: System design

### System Agents (Maintenance)
- **MCP**: Model Context Protocol handling
- **Backup**: Data backup
- **Integrity**: System integrity checks
- **Context Guard**: Context window management
- **Router**: Message routing
- **Scheduler**: Task scheduling
- **Health**: System health checks
- **Metrics**: Performance metrics
- **Logger**: Audit logging
- **Config**: Configuration management

## Memory Bank
Use the local memory bank to store:
- Project-specific patterns (\`memory-bank/project-patterns/\`)
- User preferences (\`memory-bank/user-preferences/\`)
- Learned solutions (\`memory-bank/learned-solutions/\`)

## Rules
Strictly follow all rules in \`./rules/\`.
`

export const AGENT_TEMPLATES = [
    // Cognitive Agents
    {
        name: 'intake.yaml',
        content: {
            name: 'IntakeAgent',
            type: 'cognitive',
            description: 'Analyzes user requests and routes to appropriate agents',
            tasks: ['analyze_request', 'route_task', 'extract_context'],
            confidence: { min: 90, max: 100 }
        }
    },
    {
        name: 'retrieval.yaml',
        content: {
            name: 'RetrievalAgent',
            type: 'cognitive',
            description: 'Retrieves relevant context from memory bank and index',
            tasks: ['search_memory', 'search_index', 'context_assembly'],
            confidence: { min: 80, max: 100 }
        }
    },
    {
        name: 'verification.yaml',
        content: {
            name: 'VerificationAgent',
            type: 'cognitive',
            description: 'Verifies facts and sources',
            tasks: ['fact_check', 'source_verification'],
            confidence: { min: 95, max: 100 }
        }
    },
    // Execution Agents
    {
        name: 'dev.yaml',
        content: {
            name: 'DevAgent',
            type: 'execution',
            description: 'Code generation and modification',
            tasks: ['generate_code', 'modify_code', 'debug_code'],
            confidence: { min: 70, max: 100 },
            prompts: { system: 'You are an expert software developer. Generate clean, maintainable code.' }
        }
    },
    {
        name: 'security.yaml',
        content: {
            name: 'SecurityAgent',
            type: 'execution',
            description: 'Security scanning and vulnerability detection',
            tasks: ['scan_vulnerabilities', 'check_secrets', 'analyze_dependencies'],
            confidence: { min: 95, max: 100 },
            tools: ['bandit', 'semgrep', 'gitleaks', 'npm-audit']
        }
    },
    {
        name: 'tests.yaml',
        content: {
            name: 'TestAgent',
            type: 'execution',
            description: 'Test generation and execution',
            tasks: ['generate_tests', 'run_tests', 'analyze_coverage'],
            confidence: { min: 90, max: 100 }
        }
    },
    {
        name: 'architecture.yaml',
        content: {
            name: 'ArchitectureAgent',
            type: 'execution',
            description: 'System design and patterns',
            tasks: ['design_system', 'review_architecture', 'enforce_patterns'],
            confidence: { min: 85, max: 100 }
        }
    },
    // Oracle Agents
    {
        name: 'oracle_code.yaml',
        content: {
            name: 'OracleCode',
            type: 'oracle',
            description: 'Executes code to verify correctness',
            tasks: ['execute_code', 'verify_output'],
            confidence: { min: 100, max: 100 } // Axiom
        }
    }
]

export const RULE_TEMPLATES = [
    {
        name: '01-no-hardcoded-secrets.md',
        content: `# No Hardcoded Secrets
## Rule
Never hardcode API keys, passwords, or sensitive data.
## Enforcement
- Use environment variables
- Use secret management services
- Add secrets to .gitignore
`
    },
    {
        name: '02-code-review-required.md',
        content: `# Code Review Required
## Rule
All code changes must pass automated review before integration.
## Checks
- Linting
- Type checking
- Security scanning
- Test coverage (>80%)
`
    },
    {
        name: '03-checkpoint-before-refactor.md',
        content: `# Checkpoint Before Refactor
## Rule
Create a checkpoint before any major refactoring.
## Process
1. Run full test suite
2. Create checkpoint
3. Refactor
4. Verify tests
`
    },
    {
        name: '04-epistemic-honesty.md',
        content: `# Epistemic Honesty
## Rule
Never hallucinate. If you don't know, say "I don't know".
## Process
1. Check sources
2. If uncertain, mark confidence as UNCERTAIN
3. Ask user for clarification
`
    }
]
