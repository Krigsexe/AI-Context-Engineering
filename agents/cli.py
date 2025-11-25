#!/usr/bin/env python3
# =============================================================================
# ODIN v7.0 - Agent CLI
# =============================================================================
# Command-line interface for running and managing agents
# =============================================================================

from __future__ import annotations
import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("odin")


def setup_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass


def get_agent_class(agent_name: str):
    """Get agent class by name."""
    from agents import AgentRegistry

    agent_class = AgentRegistry.get(agent_name)
    if not agent_class:
        available = AgentRegistry.list_agents()
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Available agents: {', '.join(available)}"
        )
    return agent_class


async def run_agent(agent_name: str, config: Optional[dict] = None):
    """Run an agent."""
    from agents import LLMClient, MessageBus, InMemoryStateStore

    # Initialize shared components
    llm_client = LLMClient()
    message_bus = MessageBus()
    state_store = InMemoryStateStore()

    # Create agent
    agent_class = get_agent_class(agent_name)
    agent = agent_class(
        llm_client=llm_client,
        message_bus=message_bus,
        state_store=state_store,
        config=config or {},
    )

    logger.info(f"Starting agent: {agent_name} ({agent.agent_id})")

    try:
        await agent.start()

        # Keep running and consume messages
        while True:
            messages = message_bus.consume(["agents"], block=5000, count=10)
            for message in messages:
                if message.target in ("*", agent_name, agent.agent_id):
                    response = await agent.handle_message(message)
                    if response:
                        message_bus.reply(message, response)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await agent.stop()
        message_bus.close()


async def run_task(agent_name: str, task_type: str, input_data: dict):
    """Run a single task on an agent."""
    from agents import LLMClient, InMemoryStateStore

    # Initialize
    llm_client = LLMClient()
    state_store = InMemoryStateStore()

    # Create agent
    agent_class = get_agent_class(agent_name)
    agent = agent_class(
        llm_client=llm_client,
        state_store=state_store,
    )

    await agent.start()

    try:
        result = await agent.run_task(task_type, input_data)
        return result
    finally:
        await agent.stop()


def cmd_list(args):
    """List available agents."""
    from agents import AgentRegistry

    agents = AgentRegistry.list_agents()

    print("\nAvailable Agents:")
    print("=" * 50)

    for agent_name in sorted(agents):
        agent_class = AgentRegistry.get(agent_name)
        if agent_class:
            # Create temp instance to get description
            temp = object.__new__(agent_class)
            try:
                desc = agent_class.description.fget(temp)
            except:
                desc = "No description"
            print(f"  {agent_name:20} - {desc}")

    print()


def cmd_run(args):
    """Run an agent."""
    setup_environment()

    config = {}
    if args.config:
        config = json.loads(args.config)

    asyncio.run(run_agent(args.agent, config))


def cmd_task(args):
    """Run a single task."""
    setup_environment()

    input_data = {}
    if args.input:
        input_data = json.loads(args.input)

    if args.file:
        file_content = Path(args.file).read_text()
        input_data["code"] = file_content
        input_data["file_path"] = args.file

    result = asyncio.run(run_task(args.agent, args.task_type, input_data))

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"\nResult: {'Success' if result.success else 'Failed'}")
        print(f"Confidence: {result.confidence.name}")
        print(f"Reasoning: {result.reasoning}")

        if result.data:
            print("\nData:")
            print(json.dumps(result.data, indent=2, default=str)[:2000])

        if result.warnings:
            print("\nWarnings:")
            for w in result.warnings:
                print(f"  - {w}")


def cmd_providers(args):
    """List available LLM providers."""
    from agents import list_providers, get_provider

    providers = list_providers()

    print("\nAvailable LLM Providers:")
    print("=" * 50)

    for provider_name in sorted(providers):
        try:
            provider = get_provider(provider_name)
            available = provider.is_available()
            status = "✓ configured" if available else "✗ not configured"
            models = provider.list_models()[:3]  # First 3 models

            print(f"\n  {provider_name}")
            print(f"    Status: {status}")
            print(f"    Models: {', '.join(models)}")
        except Exception as e:
            print(f"\n  {provider_name}")
            print(f"    Error: {e}")

    print()


def cmd_health(args):
    """Check system health."""
    setup_environment()

    print("\nODIN System Health Check")
    print("=" * 50)

    # Check LLM provider
    from agents import LLMClient

    try:
        client = LLMClient()
        available = client.is_available()
        print(f"\n  LLM Provider: {'✓' if available else '✗'}")
        if available:
            print(f"    Available: {', '.join(client.list_available_providers())}")
    except Exception as e:
        print(f"\n  LLM Provider: ✗ Error - {e}")

    # Check Redis
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()
        print("  Redis: ✓")
    except Exception as e:
        print(f"  Redis: ✗ {e}")

    # Check PostgreSQL
    try:
        import psycopg2
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL", "postgresql://odin:odin@localhost:5432/odin")
        )
        conn.close()
        print("  PostgreSQL: ✓")
    except Exception as e:
        print(f"  PostgreSQL: ✗ {e}")

    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="odin-agent",
        description="ODIN v7.0 - Multi-agent AI orchestration"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List available agents")
    list_parser.set_defaults(func=cmd_list)

    # Run command
    run_parser = subparsers.add_parser("run", help="Run an agent")
    run_parser.add_argument("agent", help="Agent name to run")
    run_parser.add_argument("-c", "--config", help="JSON config string")
    run_parser.set_defaults(func=cmd_run)

    # Task command
    task_parser = subparsers.add_parser("task", help="Run a single task")
    task_parser.add_argument("agent", help="Agent name")
    task_parser.add_argument("task_type", help="Task type")
    task_parser.add_argument("-i", "--input", help="JSON input data")
    task_parser.add_argument("-f", "--file", help="Input file path")
    task_parser.add_argument("--json", action="store_true", help="Output as JSON")
    task_parser.set_defaults(func=cmd_task)

    # Providers command
    providers_parser = subparsers.add_parser("providers", help="List LLM providers")
    providers_parser.set_defaults(func=cmd_providers)

    # Health command
    health_parser = subparsers.add_parser("health", help="Check system health")
    health_parser.set_defaults(func=cmd_health)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
