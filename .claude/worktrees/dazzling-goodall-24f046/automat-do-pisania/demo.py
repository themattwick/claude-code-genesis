#!/usr/bin/env python3
"""Demo script for Gatherer Agent"""

import sys
from schemas import UserInput
from agents import create_gatherer

def main():
    """Run demo of Gatherer Agent"""
    print("\n" + "=" * 80)
    print("🤖 Automat do Pisania - Demo Agenta Zbierającego")
    print("=" * 80)

    # Get system description from user
    print("\nDawaj! Opisz swój system (1-2 zdania):")
    system_description = input("➜ ").strip()

    if not system_description:
        print("❌ Opis nie może być pusty!")
        return 1

    # Get mode from user
    print("\nJaką tryb wolisz?")
    print("1. FAST  (6 pytań, ~5 minut)")
    print("2. FULL  (15 pytań, ~15 minut)")
    mode_choice = input("Wybierz [1/2] (domyślnie 2): ").strip() or "2"

    mode = "fast" if mode_choice == "1" else "full"

    # Create user input
    user_input = UserInput(
        system_description=system_description,
        mode=mode,
    )

    # Initialize Gatherer Agent
    gatherer = create_gatherer()
    print(f"\n✓ Agent Zbierający zainicjalizowany!")
    print(f"✓ Model: {gatherer.model}")

    # Execute
    print(f"\nStartuję zbieranie informacji (tryb: {mode})...")
    try:
        output = gatherer.execute(user_input)

        # Display results
        print("\n" + "=" * 80)
        print("📊 PODSUMOWANIE")
        print("=" * 80)
        print(f"✓ System: {output.system_name}")
        print(f"✓ Zebrano odpowiedzi: {len(output.answers)}")
        print(f"✓ Kompletność: {output.completion_percentage:.0%}")

        # Display answers
        print("\n📝 Odpowiedzi:")
        for i, answer in enumerate(output.answers, 1):
            print(f"\n{i}. [{answer.category}] {answer.question_text}")
            print(f"   Odpowiedź: {answer.answer_text}")
            print(f"   Pewność: {answer.confidence:.0%}")

        # Save results
        import json
        from datetime import datetime
        session_file = f"output/.sessions/demo-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(output.model_dump(), f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✓ Wyniki zapisane: {session_file}")

        return 0

    except KeyboardInterrupt:
        print("\n\n⏹️  Przerwano przez użytkownika")
        return 1
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
