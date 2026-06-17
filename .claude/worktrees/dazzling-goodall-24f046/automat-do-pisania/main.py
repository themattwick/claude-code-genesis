"""Main entry point - CLI for Automat do Pisania"""

import argparse
import logging
import sys
from schemas import UserInput
from pipeline import run
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Automat do Pisania - AI-powered specification writer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --description "E-commerce platform" --mode fast
  python main.py --description "Chat application" --mode full --model claude
  python main.py --description "CRM system" --provider openai --model gpt-4o
        """,
    )

    parser.add_argument(
        "--description",
        "-d",
        required=True,
        help="System description (what you want to build)",
    )

    parser.add_argument(
        "--mode",
        "-m",
        choices=["fast", "full"],
        default="full",
        help="Execution mode: fast (5 min) or full (15 min)",
    )

    parser.add_argument(
        "--provider",
        "-p",
        default=config.LLM_PROVIDER,
        help=f"LLM provider (default: {config.LLM_PROVIDER})",
    )

    parser.add_argument(
        "--model",
        "-M",
        default=config.LLM_MODEL,
        help=f"LLM model (default: {config.LLM_MODEL})",
    )

    parser.add_argument(
        "--output",
        "-o",
        default=config.OUTPUT_DIR,
        help=f"Output directory (default: {config.OUTPUT_DIR})",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug mode",
    )

    args = parser.parse_args()

    try:
        logger.info("=" * 80)
        logger.info("Automat do Pisania - AI-powered Specification Writer")
        logger.info("=" * 80)

        # Create user input
        user_input = UserInput(
            system_description=args.description,
            mode=args.mode,
        )

        logger.info(f"System Description: {user_input.system_description}")
        logger.info(f"Mode: {user_input.mode}")
        logger.info(f"Provider: {args.provider}")
        logger.info(f"Model: {args.model}")

        # Run pipeline
        logger.info("Starting pipeline...")
        session = run(user_input)

        # Output results
        logger.info("=" * 80)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 80)

        if session.gatherer_output:
            logger.info(f"✓ Collected {len(session.gatherer_output.answers)} answers")

        if session.analyzer_output:
            logger.info(f"✓ Found {len(session.analyzer_output.gaps_found)} gaps")

        if session.spec_output:
            logger.info(f"✓ Generated specification: {session.spec_output.title}")

        if session.validator_output:
            logger.info(f"✓ Validation quality score: {session.validator_output.quality_score:.2%}")

        # Save session
        import json
        from datetime import datetime

        session_file = f"{args.output}/.sessions/session-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(session_file, "w") as f:
            json.dump(session.model_dump(), f, indent=2, default=str)
        logger.info(f"✓ Session saved: {session_file}")

        # Save specification
        if session.spec_output:
            spec_file = f"{args.output}/{session.spec_output.title.replace(' ', '-')}.md"
            with open(spec_file, "w") as f:
                f.write(session.spec_output.markdown_spec)
            logger.info(f"✓ Specification saved: {spec_file}")

        logger.info("=" * 80)
        return 0

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.debug)
        return 1


if __name__ == "__main__":
    sys.exit(main())
