"""Save/load SessionState do JSON w output/.session/."""
from __future__ import annotations
import json
from pathlib import Path
from schemas import SessionState
from config import SESSION_DIR


def session_path(slug: str) -> Path:
    return SESSION_DIR / f"{slug}.json"


def save_session(state: SessionState) -> Path:
    p = session_path(state.slug())
    p.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    return p


def load_session(slug_or_name: str) -> SessionState | None:
    """Próbuje wczytać po slug, potem po nazwie."""
    p = session_path(slug_or_name)
    if not p.exists():
        # spróbuj po znormalizowanej nazwie
        from schemas.session import SessionState as S
        s = S(system_name=slug_or_name, description="")
        p = session_path(s.slug())
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    return SessionState.model_validate(data)


def list_sessions() -> list[tuple[str, str]]:
    """Zwraca listę (slug, system_name) zapisanych sesji."""
    out = []
    for p in sorted(SESSION_DIR.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            out.append((p.stem, data.get("system_name", p.stem)))
        except Exception:
            continue
    return out
