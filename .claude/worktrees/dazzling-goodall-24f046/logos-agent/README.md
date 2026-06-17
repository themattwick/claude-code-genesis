# Logos Agent

Półautomatyczny system agentowy do generowania specyfikacji systemów (Spec-Driven Development) oparty na **Google ADK + Gemini** i **Zachman Framework**.

Wejście: krótki opis systemu.
Wyjście: trzy pliki — Markdown dla ludzi, JSON kontrakt dla AI, draft artefaktów (entities, rules, events, permissions).

---

## Filozofia

Każda niejednoznaczność w specyfikacji to **Ambiguity Tax** — AI milcząco wybierze default, który wygeneruje błąd 6 tygodni później. Logos Agent prowadzi przez 100 pytań w 10 kategoriach (lub 40 w 4 — tryb fast), wykrywa risky words, sprawdza spójność i syntetyzuje wszystko w ZachmanModel — *AI's Contract*.

---

## Architektura

```
opis → ContextAgent → 10×CategoryAgent → CP1
                                              ↓
                          InterviewAgent → CP2
                                              ↓
                                   SynthesisAgent (ZachmanModel JSON)
                                              ↓
                       CritiqueAgent + RiskAgent + ConsistencyAgent
                                              ↓
                                            CP3 ──[r]── pętla redukcji (max 2)
                                              ↓
                                         ExportAgent
                                              ↓
                       <slug>-logos.md  +  <slug>-contract.json  +  <slug>-artifacts.md
```

3 checkpointy człowieka:
- **CP1** — przegląd draftów per kategoria
- **CP2** — odpowiedzi na luki wykryte przez InterviewAgent
- **CP3** — finalna walidacja z opcją ponownego interview dla redukcji niejednoznaczności

---

## Instalacja

```bash
pip install -r requirements.txt
cp .env.example .env  # wpisz GOOGLE_API_KEY
```

---

## Użycie

### Gemini (domyślnie — wymaga API key)
```bash
export GOOGLE_API_KEY=your_key_here
python main.py --mode full
python main.py --example ecommerce --mode fast
python main.py --resume "MyApp"
python main.py --validate output/myapp-contract.json
```

### Ollama (lokalnie — bez API key)
```bash
# 1. Zainstaluj Ollama: https://ollama.ai
# 2. Pobierz model: ollama pull mistral
# 3. Uruchom Ollama: ollama serve (w osobnym terminalu)

# 4. W innym terminalu:
python main.py --model ollama/mistral --mode fast --example ecommerce
python main.py --model ollama/neural-chat --example chatbot

# Ollama na zdalnym serwerze:
OLLAMA_API_BASE=http://192.168.1.100:11434 python main.py --model ollama/mistral
```

### Inne modele (przez LiteLlm)
```bash
# OpenAI
OPENAI_API_KEY=sk-... python main.py --model gpt-4o --example ecommerce

# Anthropic
ANTHROPIC_API_KEY=sk-ant-... python main.py --model claude-3-5-sonnet-20241022

# Groq (szybki, darmowy tier)
GROQ_API_KEY=gsk-... python main.py --model groq/llama-3.1-70b-versatile --mode fast

# HuggingFace
HUGGINGFACE_API_KEY=hf-... python main.py --model huggingface/mistralai/Mistral-7B-Instruct-v0.1
```

### Wznowienie sesji
```bash
python main.py --resume "MyApp"
python main.py --list
```

### Walidacja
```bash
python main.py --validate output/myapp-contract.json
```

---

## Tryby

| Tryb | Pytania | Kategorie | Czas | Zastosowanie |
|------|---------|-----------|------|--------------|
| `fast` | 40 | CO, KTO, DLACZEGO, JAK | ~10 min | MVP, prototyp, decyzja architektoniczna |
| `full` | 100 | + GDZIE, KIEDY, ILE, CO JEŚLI, JAK MIERZYĆ, INTEGRACJE | ~30 min | Produkcyjna specyfikacja |

---

## Modele

**v4 — model-agnostic przez LiteLlm** (wbudowany w google-adk):

| Model | Flaga | Wymaga | Koszt | JSON |
|-------|-------|--------|-------|------|
| **Gemini 2.5 Flash** | (domyślnie) | `GOOGLE_API_KEY` | $ | ✅ Gwarantowany (schema) |
| **Gemini 2.5 Pro** | synthesis/critique auto | `GOOGLE_API_KEY` | $$ | ✅ Gwarantowany (schema) |
| **Ollama/Mistral** | `--model ollama/mistral` | Ollama lokalnie | 0 | ⚠ Best-effort |
| **GPT-4o** | `--model gpt-4o` | `OPENAI_API_KEY` | $$ | ⚠ Best-effort |
| **Claude** | `--model claude-3-5-sonnet-...` | `ANTHROPIC_API_KEY` | $$ | ⚠ Best-effort |
| **Groq** | `--model groq/llama-3.1-70b-versatile` | `GROQ_API_KEY` | $ | ⚠ Best-effort |

Jeden backend (ADK + LiteLlm) — zero zmian w kodzie agentów.

---

## Struktura wyjścia

### `<slug>-contract.json`
ZachmanModel — *AI's Contract*. Strukturyzowany JSON gotowy do feedu w kolejne agenty/AI generatory kodu:

```json
{
  "system": "...",
  "ambiguity_score": 0.18,
  "entities": [...],
  "actors": [...],
  "rules": [{"id": "R1", "condition": "...", "action": "..."}],
  "events": [...],
  "integrations": [...],
  "tech_constraints": [...],
  "scale": {"concurrent_users": 500, ...}
}
```

### `<slug>-logos.md`
Pełna specyfikacja Q&A z adnotacjami `> ⚠ Ambiguity Tax: ...` przy odpowiedziach z risky words.

### `<slug>-artifacts.md`
Tabele draft artefaktów: Entity Model, Permission Matrix, Business Rules, Event Catalog, Integration Map.

---

## Konfiguracja modeli

W `config.py`:

```python
MODELS = {
    "category":   "gemini-2.5-flash",   # 10× równolegle, optymalizacja kosztu
    "synthesis":  "gemini-2.5-pro",     # głębokie reasoning + structured output
    "critique":   "gemini-2.5-pro",
    ...
}
```

Flash dla równoległych draftów (10× tańsze), pro dla syntezy/krytyki (głębsze reasoning).

---

## Logi

Każde uruchomienie zapisuje pełen input/output każdego agenta w `logs/<timestamp>/<agent>.jsonl` — przydatne do debugowania promptów i kosztu.

---

## Save / Resume

Po każdej fazie pipeline zapisuje pełen `SessionState` w `output/.session/<slug>.json`. Można przerwać CTRL+C w dowolnym checkpoincie i wznowić: `python main.py --resume "MyApp"`.
