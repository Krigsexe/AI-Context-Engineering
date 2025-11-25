#!/usr/bin/env python3
"""
ODIN v7.0 - Basic Usage Example

This example demonstrates:
1. Creating an LLM client with provider selection
2. Using the IntakeAgent to analyze a request
3. Using the DevAgent to generate code
4. Using the OracleCodeAgent to verify code
"""

import asyncio
import os
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import (
    LLMClient,
    InMemoryStateStore,
    IntakeAgent,
    DevAgent,
    OracleCodeAgent,
    ConfidenceLevel,
)


async def main():
    """Run basic usage example."""
    print("=" * 60)
    print("ODIN v7.0 - Basic Usage Example")
    print("=" * 60)

    # Initialize shared components
    # The LLM client will auto-detect available providers
    llm_client = LLMClient()
    state_store = InMemoryStateStore()

    # Check available providers
    print("\n📡 Available LLM Providers:")
    available = llm_client.list_available_providers()
    if available:
        for provider in available:
            print(f"  ✓ {provider}")
    else:
        print("  ⚠ No providers available. Configure at least one provider.")
        print("  For local: Install Ollama and run 'ollama pull qwen2.5:7b'")
        return

    # Create agents
    intake = IntakeAgent(llm_client=llm_client, state_store=state_store)
    dev = DevAgent(llm_client=llm_client, state_store=state_store)
    oracle = OracleCodeAgent(state_store=state_store)

    # Start agents
    await intake.start()
    await dev.start()
    await oracle.start()

    print("\n🤖 Agents initialized:")
    print(f"  - {intake.name}: {intake.description}")
    print(f"  - {dev.name}: {dev.description}")
    print(f"  - {oracle.name}: {oracle.description}")

    # Example 1: Analyze a user request
    print("\n" + "=" * 60)
    print("Example 1: Analyzing a user request")
    print("=" * 60)

    user_request = "Create a Python function that calculates the fibonacci sequence"

    print(f"\n📝 User Request: {user_request}")
    print("\n⏳ Analyzing request...")

    analysis = await intake.run_task(
        "analyze_request",
        {"request": user_request}
    )

    if analysis.success:
        print(f"\n✓ Analysis complete (Confidence: {analysis.confidence.name})")
        print(f"  Task Type: {analysis.data.get('task_type', 'unknown')}")
        print(f"  Complexity: {analysis.data.get('complexity', 'unknown')}")
        print(f"  Suggested Agents: {analysis.data.get('suggested_agents', [])}")
    else:
        print(f"\n✗ Analysis failed: {analysis.reasoning}")

    # Example 2: Generate code
    print("\n" + "=" * 60)
    print("Example 2: Generating code")
    print("=" * 60)

    print("\n⏳ Generating code...")

    code_result = await dev.run_task(
        "generate_code",
        {
            "requirements": "Create a function that calculates the nth fibonacci number using memoization",
            "language": "python",
        }
    )

    if code_result.success:
        print(f"\n✓ Code generated (Confidence: {code_result.confidence.name})")
        print("\nGenerated Code:")
        print("-" * 40)
        print(code_result.data.get("code", "No code generated")[:500])
        if len(code_result.data.get("code", "")) > 500:
            print("... (truncated)")
    else:
        print(f"\n✗ Code generation failed: {code_result.reasoning}")

    # Example 3: Verify code with Oracle
    print("\n" + "=" * 60)
    print("Example 3: Verifying code with Oracle")
    print("=" * 60)

    test_code = '''
def fibonacci(n, memo={}):
    """Calculate nth fibonacci number with memoization."""
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]

# Test
print(fibonacci(10))
'''

    print("\n⏳ Verifying code execution...")

    verify_result = await oracle.run_task(
        "execute_code",
        {
            "code": test_code,
            "language": "python",
        }
    )

    if verify_result.success:
        print(f"\n✓ Code executed successfully (Confidence: {verify_result.confidence.name})")
        print(f"  Output: {verify_result.data.get('output', '').strip()}")
    else:
        print(f"\n✗ Code execution failed: {verify_result.reasoning}")
        print(f"  Errors: {verify_result.data.get('errors', '')}")

    # Example 4: Syntax check
    print("\n" + "=" * 60)
    print("Example 4: Syntax validation")
    print("=" * 60)

    invalid_code = "def broken(:\n    pass"

    print("\n⏳ Checking syntax of invalid code...")

    syntax_result = await oracle.run_task(
        "syntax_check",
        {
            "code": invalid_code,
            "language": "python",
        }
    )

    if syntax_result.data:
        valid = syntax_result.data.get("valid", False)
        print(f"\n{'✓ Valid' if valid else '✗ Invalid'} syntax")
        if not valid:
            for error in syntax_result.data.get("errors", []):
                print(f"  Error: {error}")

    # Cleanup
    await intake.stop()
    await dev.stop()
    await oracle.stop()

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
