# Automat do Pisania — AI-Powered Specification Writer

Polish specification generator using multi-agent system and Zachman Framework.

## What is it?

**Automat do Pisania** (Writing Automaton) is a system that helps you write system specifications using AI. It works like a team of agents that:

1. **Gatherer Agent** — Asks you systematic questions
2. **Analyzer Agent** — Finds gaps and contradictions in your answers
3. **Spec Writer Agent** — Generates specification in 3 formats
4. **Validator Agent** — Checks specification quality

## Key Features

✅ **Multi-Agent System** — 4 AI agents working together
✅ **Zachman Framework** — 10 categories (CO, KTO, GDZIE, KIEDY, etc.)
✅ **2 Execution Modes**:
   - **FAST**: 6 questions, 5 minutes
   - **FULL**: 15 questions, 15 minutes

✅ **Model Agnostic** — Works with:
   - Google Gemini
   - Anthropic Claude
   - OpenAI GPT
   - Ollama (local)
   - Groq
   - HuggingFace
   - Any LLM with API

✅ **3 Output Formats**:
   - Markdown (human-readable spec)
   - JSON Contract (machine-readable)
   - Diagrams and Tables

✅ **Iterative** — Agents validate each other and ask for clarifications

## Installation

```bash
# Clone repo
git clone <repo-url>
cd automat-do-pisania

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# LLM Provider
LLM_PROVIDER=gemini          # or: claude, openai, ollama, etc.
LLM_MODEL=gemini-2.5-flash  # or: claude-3-5-sonnet, gpt-4o, etc.
LLM_API_KEY=your-key-here   # Required for most providers
```

## Usage

### Quick Start (FAST mode)

```bash
python main.py \
  --description "E-commerce platform" \
  --mode fast
```

### Full Mode (FULL)

```bash
python main.py \
  --description "Chat application for teams" \
  --mode full
```

### Use Different Model

```bash
python main.py \
  --description "CRM system" \
  --provider openai \
  --model gpt-4o
```

### Help

```bash
python main.py --help
```

## Output

The system generates:

1. **Markdown Spec** → `output/System-Name.md`
   - Human-readable specification
   - All 10 Zachman categories
   - Formatted for documentation

2. **JSON Contract** → `output/.sessions/session-*.json`
   - Machine-readable specification
   - Structured data for code generation
   - Can be used by other tools

3. **Session State** → `output/.sessions/session-*.json`
   - Full conversation history
   - Can resume from any checkpoint
   - For auditing and debugging

## Zachman Categories (10)

| Polish | English | Description |
|--------|---------|------------|
| CO | WHAT | Data entities, fields, structure |
| KTO | WHO | Users, roles, permissions |
| GDZIE | WHERE | Access, boundaries, locations |
| KIEDY | WHEN | Timing, events, triggers |
| DLACZEGO | WHY | Business rules, constraints |
| JAK | HOW | Mechanisms, processes, workflows |
| ILE | HOW MUCH | Scale, performance, limits |
| CO JEŚLI | WHAT IF | Edge cases, failover, recovery |
| JAK MIERZYĆ | HOW TO MEASURE | Metrics, monitoring, alerts |
| INTEGRACJE | INTEGRATIONS | External systems, protocols |

## Architecture

```
User Input (system description)
    ↓
[GATHERER] → Questions
    ↓
[ANALYZER] → Check gaps, contradictions
    ↓
[SPEC WRITER] → Generate spec
    ↓
[VALIDATOR] → Check quality
    ↓
If issues → Loop back to GATHERER
If OK → Output 3 formats
```

## Project Structure

```
automat-do-pisania/
├── README.md              # This file
├── config.py              # Configuration
├── main.py                # CLI entry point
├── pipeline.py            # Orchestration
├── requirements.txt       # Dependencies
│
├── agents/                # AI agents
│   ├── backends.py       # LLM backend (model-agnostic)
│   ├── gatherer.py       # Gatherer Agent
│   ├── analyzer.py       # Analyzer Agent
│   ├── spec_writer.py    # Spec Writer Agent
│   └── validator.py      # Validator Agent
│
├── schemas/               # Data models (Pydantic)
│   └── models.py
│
├── framework/             # Zachman framework
│   └── questions.py      # 100 questions
│
├── tests/                 # Test suite
│   ├── unit/
│   └── integration/
│
└── output/                # Generated specs (gitignored)
    ├── *.md              # Markdown specs
    └── .sessions/        # Session state
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run only integration tests
pytest tests/integration/ -v
```

## Development

### Current Status

- ✅ Phase 1: **SPECIFICATION** — All contracts and schemas defined
- ⏳ Phase 2: **IMPLEMENTATION** — Agents partially implemented (stubs)
- ⏳ Phase 3: **TESTING** — Test structure ready, tests not yet written
- ⏳ Phase 4: **POLISH** — UI, error handling, documentation

### TODO: Implement

1. **Gatherer Agent** — Interactive Q&A with user
2. **Analyzer Agent** — Contradiction detection, gap analysis
3. **Spec Writer Agent** — Markdown generation, JSON mapping
4. **Validator Agent** — Quality checks, consistency validation
5. **User Interface** — Web UI or advanced CLI
6. **Persistence** — Session save/load
7. **Tests** — Comprehensive test coverage

## Environment Variables

See `.env.example` for all available options.

## License

TBD

## Author

Created as part of Spec-Driven Development initiative.
