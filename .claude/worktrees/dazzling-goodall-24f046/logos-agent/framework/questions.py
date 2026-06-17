"""100 pytań w 10 kategoriach z metadata Zachman.

Każde pytanie ma id (1-100), kategorię, tag Zachman do którego zasila pole
w ZachmanModel, flagę required (True dla trybu fast), oraz przykład
dobrej odpowiedzi (few-shot dla CategoryAgent).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


ZachmanTag = Literal[
    "entities", "actors", "rules", "events",
    "integrations", "tech", "scale", "observability"
]


@dataclass(frozen=True)
class Question:
    id: int                # 1..100
    category_id: str       # "co", "gdzie", ...
    text: str              # po polsku
    zachman_tag: ZachmanTag
    required: bool         # True = używane w trybie fast
    example: str           # przykład dobrej, konkretnej odpowiedzi


@dataclass(frozen=True)
class Category:
    id: str                # "co", "gdzie", ...
    name: str              # "CO", "GDZIE", ...
    sub: str               # podtytul np. "WHAT — Czym jest system"
    color_hex: str
    desc: str              # cel kategorii
    fast_mode: bool        # czy wchodzi w tryb fast


CATEGORIES: list[Category] = [
    Category("co", "CO", "WHAT — Czym jest system", "#3B82F6",
             "Encje, ich stany, dane wymagane i opcjonalne", fast_mode=True),
    Category("gdzie", "GDZIE", "WHERE — Granice i lokalizacja", "#22C55E",
             "Skąd dostęp, gdzie dane mogą trafiać, granice systemu", fast_mode=False),
    Category("kiedy", "KIEDY", "WHEN — Czas i wyzwalacze", "#EAB308",
             "Kiedy coś się dzieje, kiedy wygasa, kiedy retry", fast_mode=False),
    Category("kto", "KTO", "WHO — Aktorzy i uprawnienia", "#F97316",
             "Kto może co robić, kto nie może, kto zatwierdza", fast_mode=True),
    Category("dlaczego", "DLACZEGO", "WHY — Reguły i ograniczenia", "#EF4444",
             "Dlaczego system istnieje, dlaczego reguły są takie", fast_mode=True),
    Category("jak", "JAK", "HOW — Mechanizmy i tech", "#A855F7",
             "Jak system reaguje, jak obsługuje błędy, jak utrzymuje spójność", fast_mode=True),
    Category("ile", "ILE", "HOW MUCH — Skala i koszty", "#06B6D4",
             "Liczby: użytkownicy, czas odpowiedzi, koszty, limity", fast_mode=False),
    Category("co_jesli", "CO JEŚLI", "WHAT IF — Scenariusze graniczne", "#F43F5E",
             "Tryby awaryjne, edge cases, co jeśli coś padnie", fast_mode=False),
    Category("jak_mierzyc", "JAK MIERZYĆ", "HOW TO MEASURE — Obserwowalność", "#84CC16",
             "Metryki, alerty, kryteria sukcesu", fast_mode=False),
    Category("integracje", "INTEGRACJE", "INTEGRATIONS — Upstream/Downstream", "#F59E0B",
             "Systemy zewnętrzne in/out, protokoły, krytyczność", fast_mode=False),
]

FAST_CATEGORIES = {c.id for c in CATEGORIES if c.fast_mode}

CATEGORY_BY_ID = {c.id: c for c in CATEGORIES}


def category_by_id(cid: str) -> Category:
    return CATEGORY_BY_ID[cid]


# ─────────────────────────────────────────────────────────────────────────
# 100 pytań
# ─────────────────────────────────────────────────────────────────────────

ALL_QUESTIONS: list[Question] = [
    # ── CO (1-10) ────────────────────────────────────────────────────────
    Question(1, "co", "Co robi system?", "entities", True,
             "System przyjmuje, przetwarza i archiwizuje zamówienia e-commerce klientów B2C."),
    Question(2, "co", "Jakie są główne elementy systemu?", "entities", True,
             "Zamówienie, Pozycja zamówienia, Klient, Produkt, Płatność, Wysyłka."),
    Question(3, "co", "Co może istnieć w systemie?", "entities", True,
             "Wyłącznie zamówienia złożone przez zarejestrowanych klientów; brak gości."),
    Question(4, "co", "Czego nie może być w systemie?", "entities", True,
             "Nie przechowujemy numerów kart płatniczych — tylko token z bramki płatności."),
    Question(5, "co", "Jakie informacje muszą zawsze być obecne?", "entities", True,
             "ID klienta, lista pozycji (min. 1), adres dostawy, metoda płatności."),
    Question(6, "co", "Jakie informacje są opcjonalne?", "entities", False,
             "Komentarz do zamówienia, faktura na firmę, kod rabatowy."),
    Question(7, "co", "W jakich stanach może znajdować się każdy element?", "entities", True,
             "Zamówienie: robocze → złożone → opłacone → wysłane → dostarczone | anulowane."),
    Question(8, "co", "Jakie zmiany są dozwolone?", "rules", True,
             "Edycja adresu dostawy do momentu wysyłki; zmiana ilości tylko w stanie 'robocze'."),
    Question(9, "co", "Jakich zmian nie wolno dokonywać?", "rules", True,
             "Po stanie 'opłacone' nie można dodawać pozycji ani zmieniać metody płatności."),
    Question(10, "co", "Czego nigdy nie należy przechowywać?", "rules", True,
             "Numerów kart, kodów CVV, surowych haseł — tylko hashe i tokeny."),

    # ── GDZIE (11-20) ────────────────────────────────────────────────────
    Question(11, "gdzie", "Skąd można uzyskać dostęp do systemu?", "actors", False,
             "Przeglądarka web (desktop/mobile) i aplikacja iOS/Android; tylko HTTPS."),
    Question(12, "gdzie", "Gdzie wykonywane są działania (użytkownik vs system)?", "tech", False,
             "Walidacja danych: klient i serwer; obliczenia cen i rabatów: tylko serwer."),
    Question(13, "gdzie", "Gdzie mogą trafiać dane?", "integrations", False,
             "PostgreSQL (podstawowe), Redis (cache), S3 (faktury), Stripe (płatności)."),
    Question(14, "gdzie", "Gdzie dane NIE mogą trafiać?", "rules", False,
             "Dane osobowe klientów EU nie opuszczają regionu eu-central-1."),
    Question(15, "gdzie", "Gdzie są granice systemu?", "tech", False,
             "System nie obsługuje magazynu — integruje się z zewnętrznym WMS przez REST."),
    Question(16, "gdzie", "Gdzie łączą się systemy zewnętrzne?", "integrations", False,
             "Stripe (płatności), SendGrid (email), Allegro API (sync produktów)."),
    Question(17, "gdzie", "Gdzie dostęp jest ograniczony?", "actors", False,
             "Panel admina dostępny tylko z VPN firmowego (zakres IP 10.0.0.0/8)."),
    Question(18, "gdzie", "Gdzie mogą wystąpić awarie?", "tech", False,
             "Bramka płatności, dostawca emaili, warstwa cache Redis."),
    Question(19, "gdzie", "Gdzie system musi zawsze odpowiadać?", "tech", False,
             "Endpoint /api/orders/create — nawet w trybie degraded musi przyjąć zamówienie."),
    Question(20, "gdzie", "Gdzie zachowanie różni się w zależności od lokalizacji?", "rules", False,
             "VAT i waluta zależą od kraju klienta; PL=23%, DE=19%, UK=20%."),

    # ── KIEDY (21-30) ────────────────────────────────────────────────────
    Question(21, "kiedy", "Kiedy coś jest tworzone?", "events", False,
             "Zamówienie tworzy się przy POST /api/orders; status 'robocze' do potwierdzenia."),
    Question(22, "kiedy", "Kiedy coś jest aktualizowane?", "events", False,
             "Status zamówienia po webhooku ze Stripe; stan magazynu po pickingu w WMS."),
    Question(23, "kiedy", "Kiedy coś jest usuwane?", "events", False,
             "Zamówienia anulowane > 90 dni — soft delete; logi audytowe — nigdy."),
    Question(24, "kiedy", "Kiedy rozpoczyna się proces?", "events", False,
             "Wysyłka rozpoczyna się gdy płatność == 'opłacone' I produkty są w magazynie."),
    Question(25, "kiedy", "Kiedy kończy się proces?", "events", False,
             "Zamówienie zamknięte gdy 'dostarczone' + 14 dni minęło bez reklamacji."),
    Question(26, "kiedy", "Kiedy system musi odpowiedzieć natychmiast?", "tech", False,
             "Wszystkie operacje synchroniczne API < 500 ms p99."),
    Question(27, "kiedy", "Kiedy może odpowiedzieć później?", "tech", False,
             "Generowanie faktur PDF i wysyłka emaili — async, do 5 min."),
    Question(28, "kiedy", "Kiedy system powinien ponowić próbę?", "rules", False,
             "Webhooki Stripe: 3 ponowienia z exponential backoff (1s, 5s, 25s)."),
    Question(29, "kiedy", "Kiedy system powinien blokować działania?", "rules", False,
             "Nowe zamówienia blokowane gdy klient ma > 3 niezapłacone faktury."),
    Question(30, "kiedy", "Kiedy coś wygasa?", "rules", False,
             "Sesje użytkownika: 30 min; tokeny resetu hasła: 1h; rezerwacja produktu: 15 min."),

    # ── KTO (31-40) ──────────────────────────────────────────────────────
    Question(31, "kto", "Kto może korzystać z systemu?", "actors", True,
             "Klient (zarejestrowany), Pracownik obsługi, Administrator, System (webhooks)."),
    Question(32, "kto", "Kto może zobaczyć co?", "actors", True,
             "Klient: tylko własne zamówienia; Pracownik: wszystkie z swojej strefy; Admin: wszystko."),
    Question(33, "kto", "Kto może tworzyć elementy?", "actors", True,
             "Klient tworzy zamówienia; Admin tworzy produkty; nikt inny."),
    Question(34, "kto", "Kto może aktualizować elementy?", "actors", True,
             "Klient: adres dostawy do wysyłki; Pracownik: status; Admin: wszystko."),
    Question(35, "kto", "Kto może usuwać elementy?", "actors", True,
             "Tylko Admin może wykonać hard-delete; Klient może tylko anulować swoje zamówienie."),
    Question(36, "kto", "Kto nie ma dostępu do określonych danych?", "actors", True,
             "Pracownik nie widzi danych płatności (tylko status); tylko Admin widzi pełne dane karty."),
    Question(37, "kto", "Kto zatwierdza ważne działania?", "actors", True,
             "Zwroty > 1000 PLN wymagają zatwierdzenia drugiego pracownika (4-eyes)."),
    Question(38, "kto", "Kto wyzwala kluczowe zdarzenia?", "events", True,
             "Wysyłkę wyzwala Pracownik Magazynu po pickingu; webhook Stripe wyzwala status płatności."),
    Question(39, "kto", "Kto jest odpowiedzialny za działania?", "actors", True,
             "Każde działanie ma actor_id w logu audytu (user lub 'system')."),
    Question(40, "kto", "Komu nigdy nie wolno działać?", "actors", True,
             "Klient nie może zmienić właściciela zamówienia; Pracownik nie może modyfikować cen historycznych."),

    # ── DLACZEGO (41-50) ─────────────────────────────────────────────────
    Question(41, "dlaczego", "Dlaczego ten system istnieje?", "rules", True,
             "Aby umożliwić sprzedaż 24/7 z automatyzacją obsługi zamówień (cel: 10k zamówień/dzień)."),
    Question(42, "dlaczego", "Dlaczego każda funkcja istnieje?", "rules", False,
             "Anulowanie do 1h: zgodność z UE Right of Withdrawal + redukcja chargebacków."),
    Question(43, "dlaczego", "Dlaczego określone działania są dozwolone?", "rules", True,
             "Edycja adresu do wysyłki: 30% klientów się myli przy pierwszym wpisaniu."),
    Question(44, "dlaczego", "Dlaczego określone działania są blokowane?", "rules", True,
             "Brak dodawania pozycji po opłaceniu: każda zmiana wymagałaby ponownej autoryzacji płatności."),
    Question(45, "dlaczego", "Dlaczego część danych jest objęta ograniczeniami?", "rules", False,
             "Dane PII tylko w EU: zgodność z RODO art. 44-49 (transfer do państw trzecich)."),
    Question(46, "dlaczego", "Dlaczego walidacje są potrzebne?", "rules", False,
             "Walidacja kodu pocztowego zapobiega 12% błędom dostawy z poprzedniego roku."),
    Question(47, "dlaczego", "Dlaczego czas ma znaczenie?", "rules", False,
             "Rezerwacja 15 min: bilans między doświadczeniem klienta a dostępnością stocka."),
    Question(48, "dlaczego", "Dlaczego część działań jest nieodwracalna?", "rules", True,
             "Wysłana faktura ma numer prawny; korekta wymaga osobnego dokumentu (księgowość)."),
    Question(49, "dlaczego", "Dlaczego te ograniczenia są egzekwowane?", "rules", True,
             "Limit 3 niezapłacone: chroni przed nadużyciami i windykacją."),
    Question(50, "dlaczego", "Dlaczego system powinien zgłaszać błąd zamiast zgadywać?", "rules", True,
             "Złe zgadnięcie ceny = strata pieniędzy + utrata zaufania; lepiej fail-fast."),

    # ── JAK (51-60) ──────────────────────────────────────────────────────
    Question(51, "jak", "Jak system reaguje na działania użytkownika?", "tech", True,
             "Wszystkie mutacje przez REST POST/PUT, idempotency-key wymagany dla create."),
    Question(52, "jak", "Jak zachowuje się, gdy brakuje danych?", "rules", True,
             "Zwraca 422 Unprocessable Entity z listą brakujących pól; nigdy nie używa defaultów."),
    Question(53, "jak", "Jak obsługuje nieprawidłowe dane wejściowe?", "rules", True,
             "Walidacja w warstwie API (JSON Schema); odrzucenie z dokładnym kodem błędu."),
    Question(54, "jak", "Jak obsługuje błędy?", "rules", True,
             "Error envelope: {code, message_pl, message_en, trace_id}; wszystkie 5xx logowane."),
    Question(55, "jak", "Jak zachowuje się, gdy coś zawiedzie?", "rules", True,
             "Tryb degraded: zamówienia przyjmowane do kolejki, płatność weryfikowana async."),
    Question(56, "jak", "Jak odzyskuje sprawność po awarii?", "tech", True,
             "Outbox pattern + idempotent consumers; replay zdarzeń od ostatniego checkpointa."),
    Question(57, "jak", "Jak egzekwuje reguły?", "rules", True,
             "Reguły biznesowe w warstwie domeny (nie w API ani DB); jedno miejsce zmiany."),
    Question(58, "jak", "Jak zapobiega nieoczekiwanemu zachowaniu?", "rules", True,
             "Kontrakty API wersjonowane; testy property-based dla reguł cenowych."),
    Question(59, "jak", "Jak zachowuje się pod obciążeniem?", "tech", True,
             "Rate limiting 100 req/s per user; circuit breaker na zewnętrznych API."),
    Question(60, "jak", "Jak utrzymuje spójność?", "tech", True,
             "Transakcje DB dla operacji atomowych; saga pattern dla rozproszonych (płatność + wysyłka)."),

    # ── ILE (61-70) ──────────────────────────────────────────────────────
    Question(61, "ile", "Ilu użytkowników będzie korzystać z systemu jednocześnie?", "scale", False,
             "Peak 5000 concurrent, średnia 800; cel skalowalność do 20k."),
    Question(62, "ile", "Jaki jest maksymalny akceptowalny czas odpowiedzi?", "scale", False,
             "p50 < 100ms, p95 < 300ms, p99 < 500ms dla operacji read."),
    Question(63, "ile", "Jaka ilość danych będzie przetwarzana (dziennie/miesięcznie)?", "scale", False,
             "10k zamówień/dzień, 300k/miesiąc; ~50 GB nowych danych/miesiąc."),
    Question(64, "ile", "Jaki jest budżet kosztów operacyjnych?", "scale", False,
             "Max 0.05 PLN per zamówienie (compute + storage + integracje)."),
    Question(65, "ile", "Jaki poziom dostępności (uptime) jest wymagany?", "scale", False,
             "99.9% (43 min downtime/miesiąc); checkout: 99.95%."),
    Question(66, "ile", "Jak długo dane muszą być przechowywane?", "rules", False,
             "Faktury: 5 lat (prawo PL); logi audytu: 2 lata; sesje: 30 dni."),
    Question(67, "ile", "Ile równoległych operacji system musi obsłużyć?", "scale", False,
             "1000 równoczesnych transakcji checkout; 10k równoczesnych odczytów katalogu."),
    Question(68, "ile", "Jakie są limity rozmiaru danych wejściowych/wyjściowych?", "rules", False,
             "Body request max 1 MB; upload faktury max 10 MB; lista pozycji max 100."),
    Question(69, "ile", "Ile czasu może zająć przetwarzanie zadań asynchronicznych?", "scale", False,
             "Generowanie faktury < 30s; sync z Allegro < 5 min; raporty miesięczne < 1h."),
    Question(70, "ile", "Jakie są progi skalowania?", "scale", False,
             "Auto-scale up gdy CPU > 70% przez 5 min; scale down gdy < 30% przez 15 min."),

    # ── CO JEŚLI (71-80) ─────────────────────────────────────────────────
    Question(71, "co_jesli", "Co jeśli zewnętrzne API/serwis jest niedostępny?", "rules", False,
             "Stripe down: tryb 'pay later' z hold; SendGrid down: kolejka emaili w Redis (TTL 24h)."),
    Question(72, "co_jesli", "Co jeśli użytkownik prześle złośliwe lub nieprawidłowe dane?", "rules", False,
             "Walidacja JSON Schema, sanitacja HTML w komentarzach, rate limiting per IP."),
    Question(73, "co_jesli", "Co jeśli baza danych jest niedostępna?", "rules", False,
             "Read repliki: czytamy z najnowszej dostępnej; zapisy: kolejka w Kafka, replay po recovery."),
    Question(74, "co_jesli", "Co jeśli system jest przeciążony powyżej zakładanej przepustowości?", "rules", False,
             "Rate limiting 429; priorytet checkoutu nad listingiem; 'busy page' dla nowych sesji."),
    Question(75, "co_jesli", "Co jeśli operacja krytyczna zostanie przerwana w połowie?", "rules", False,
             "Outbox + idempotent retry; saga compensation dla rozproszonych transakcji."),
    Question(76, "co_jesli", "Co jeśli dwa procesy jednocześnie zmodyfikują ten sam zasób?", "rules", False,
             "Optimistic locking z version field; konflikt → 409 Conflict, klient retry."),
    Question(77, "co_jesli", "Co jeśli użytkownik straci połączenie podczas wieloetapowej operacji?", "rules", False,
             "Checkout zachowuje stan w Redis (TTL 1h); klient może wrócić i kontynuować."),
    Question(78, "co_jesli", "Co jeśli dane wejściowe są prawidłowe technicznie, ale logicznie sprzeczne?", "rules", False,
             "Walidacje cross-field na warstwie domeny; np. data dostawy < data zamówienia → 422."),
    Question(79, "co_jesli", "Co jeśli system nie może dotrzymać SLA?", "rules", False,
             "Alert PagerDuty SEV-2 gdy p99 > 800ms przez 10 min; escalation do CTO po 30 min."),
    Question(80, "co_jesli", "Co jeśli zmiany konfiguracji są potrzebne bez zatrzymywania systemu?", "rules", False,
             "Feature flags w LaunchDarkly; rolling deploy z health checks; hot reload configów."),

    # ── JAK MIERZYĆ (81-90) ──────────────────────────────────────────────
    Question(81, "jak_mierzyc", "Po czym poznamy, że system działa poprawnie?", "observability", False,
             "Conversion rate > 2.5%, error rate < 0.1%, p99 latency < 500ms, NPS > 40."),
    Question(82, "jak_mierzyc", "Jakie metryki biznesowe mierzą sukces?", "observability", False,
             "GMV/dzień, conversion rate, AOV, refund rate, customer LTV."),
    Question(83, "jak_mierzyc", "Jakie metryki techniczne są kluczowe?", "observability", False,
             "Request rate, error rate, latency p50/p95/p99, queue depth, DB connection pool usage."),
    Question(84, "jak_mierzyc", "Kiedy alert powinien obudzić inżyniera o 3 w nocy?", "observability", False,
             "SEV-1: checkout error rate > 5% przez 5 min; baza niedostępna; payment provider down."),
    Question(85, "jak_mierzyc", "Jak wygląda 'dobra' odpowiedź systemu?", "observability", False,
             "Status 2xx, latency w SLA, response zgodny z OpenAPI schema."),
    Question(86, "jak_mierzyc", "Jak mierzymy degradację jakości?", "observability", False,
             "Tracking conversion funnel; A/B test każdej zmiany checkout > 1 tydzień."),
    Question(87, "jak_mierzyc", "Jakie logi są niezbędne do diagnostyki?", "observability", False,
             "Structured JSON logs z trace_id, user_id, request_id; retention 30 dni hot, 1 rok cold."),
    Question(88, "jak_mierzyc", "Jak testujemy system przed wdrożeniem?", "observability", False,
             "Unit (>80%), integration (krytyczne flow), E2E (checkout), load test (2x peak)."),
    Question(89, "jak_mierzyc", "Jak mierzymy wpływ zmian?", "observability", False,
             "Canary deploy 5% → 25% → 100%; metryki vs baseline; auto-rollback na regresji."),
    Question(90, "jak_mierzyc", "Jakie są kryteria akceptacji dla nowych funkcji?", "observability", False,
             "Acceptance criteria w Given-When-Then; testy E2E zielone; performance regression < 5%."),

    # ── INTEGRACJE (91-100) ──────────────────────────────────────────────
    Question(91, "integracje", "Jakie systemy zewnętrzne dostarczają dane do systemu (inbound)?", "integrations", False,
             "Allegro API (katalog produktów), GUS (NIP validator), Bank webhook (potwierdzenia płatności)."),
    Question(92, "integracje", "Do jakich systemów zewnętrznych system wysyła dane (outbound)?", "integrations", False,
             "Stripe (płatności), SendGrid (email), WMS (wysyłka), GA4 (analityka), SAP (księgowość)."),
    Question(93, "integracje", "Jakie protokoły/API są używane?", "integrations", False,
             "REST/JSON dla Stripe i WMS; webhooks z signature dla Stripe; SFTP dla SAP (dzienne batches)."),
    Question(94, "integracje", "Jakie są umowy SLA z zewnętrznymi systemami?", "integrations", False,
             "Stripe 99.99%; SendGrid 99.95%; WMS 99% (5h downtime/miesiąc); SAP best-effort."),
    Question(95, "integracje", "Jakie dane są synchronizowane i jak często?", "integrations", False,
             "Allegro: katalog co 1h; SAP: zamówienia codziennie 02:00; WMS: stan magazynu real-time."),
    Question(96, "integracje", "Kto odpowiada za utrzymanie każdej integracji?", "integrations", False,
             "Stripe/SendGrid: Platform Team; SAP: Finance IT; WMS: Logistics IT; Allegro: Catalog Team."),
    Question(97, "integracje", "Jakie formaty danych są wymieniane?", "integrations", False,
             "JSON dla wszystkich REST; CSV/SFTP dla SAP; protobuf dla event bus wewnętrznego."),
    Question(98, "integracje", "Jak system reaguje na breaking changes w API dostawców?", "rules", False,
             "Wersjonowanie endpointów (v1, v2); contract tests Pact; alert na deprecation notices."),
    Question(99, "integracje", "Jakie są granice odpowiedzialności?", "integrations", False,
             "My: integracja i mapowanie; Stripe: PCI compliance; WMS: stan magazynu; SAP: księgowość."),
    Question(100, "integracje", "Które integracje są krytyczne dla działania systemu?", "integrations", False,
             "Krytyczne: Stripe, baza, Redis. Degraded-OK: SendGrid, WMS. Opcjonalne: GA4, Allegro."),
]


# ─────────────────────────────────────────────────────────────────────────
# Helpery
# ─────────────────────────────────────────────────────────────────────────

QUESTION_BY_ID = {q.id: q for q in ALL_QUESTIONS}


def question_by_id(qid: int) -> Question:
    return QUESTION_BY_ID[qid]


def questions_for_mode(mode: str) -> list[Question]:
    """Zwraca pytania właściwe dla trybu: 'fast' (40) lub 'full' (100)."""
    if mode == "fast":
        return [q for q in ALL_QUESTIONS if q.required and q.category_id in FAST_CATEGORIES]
    return ALL_QUESTIONS


def questions_by_category(cid: str, mode: str = "full") -> list[Question]:
    qs = questions_for_mode(mode)
    return [q for q in qs if q.category_id == cid]


# Sanity check przy imporcie
assert len(ALL_QUESTIONS) == 100, f"Expected 100 questions, got {len(ALL_QUESTIONS)}"
assert {q.id for q in ALL_QUESTIONS} == set(range(1, 101)), "Question IDs must be 1..100"
