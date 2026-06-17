# Sklep B2C — Specyfikacja Logos Agent
Wygenerowano: 2026-04-29 | Tryb: full | Ambiguity Score: 0.13

## Opis systemu
System e-commerce dla sklepu odzieżowego B2C w Polsce z planowaną ekspansją na DE i UK. Klienci rejestrują się, przeglądają katalog, składają zamówienia i płacą przez Stripe. Zamówienia są realizowane przez zewnętrzne WMS, a faktury synchronizowane do SAP. Wymagana zgodność z RODO i ustawą o prawach konsumenta (możliwość anulowania w 14 dni). Cel skali: 10 tys. zamówień dziennie, 99.9% uptime na checkout. Zespół wewnętrzny obsługuje reklamacje przez panel admina dostępny tylko z VPN firmowego. Kluczowe role: Klient, Pracownik obsługi, Administrator.

---

## CO — WHAT — Czym jest system

### P1: Co robi system?
System przyjmuje, przetwarza i archiwizuje zamówienia e-commerce klientów B2C.

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P2: Jakie są główne elementy systemu?
Zamówienie, Pozycja zamówienia, Klient, Produkt, Płatność, Wysyłka, Faktura.

### P3: Co może istnieć w systemie?
Występują tylko zamówienia złożone przez zarejestrowanych klientów; brak gości i niezalogowanych użytkowników.

### P4: Czego nie może być w systemie?
Nie przechowywane są numerki kart płatniczych — tylko tokeny z bramki płatności Stripe.

### P5: Jakie informacje muszą zawsze być obecne?
ID klienta, lista pozycji (min. 1), adres dostawy, metoda płatności, data zamówienia, status zamówienia.

### P6: Jakie informacje są opcjonalne?
Komentarz do zamówienia, faktura na firmę, kod rabatowy, metoda wysyłki.

### P7: W jakich stanach może znajdować się każdy element?
Zamówienie: robocze → złożone → opłacone → wysłane → dostarczone | anulowane; Pozycja zamówienia: dodana → usunięta; Klient: zarejestrowany → nieaktywny; Produkt: dostępny → niedostępny; Faktura: generowana → wysłana.

### P8: Jakie zmiany są dozwolone?
Edycja adresu dostawy do momentu wysyłki; zmiana ilości pozycji tylko w stanie 'robocze'; dodawanie faktury po złożeniu zamówienia.

### P9: Jakich zmian nie wolno dokonywać?
Po stanie 'opłacone' nie można dodawać pozycji ani zmieniać metody płatności; po stanie 'wysłane' nie można edytować adresu dostawy, ilości pozycji ani statusu zamówienia.

### P10: Czego nigdy nie należy przechowywać?
Numery kart, kod CVV, surowe hasła — tylko hashe i tokeny.

## GDZIE — WHERE — Granice i lokalizacja

### P11: Skąd można uzyskać dostęp do systemu?
Dostęp do systemu możliwy z przeglądarki web (desktop/mobile) i aplikacji iOS/Android; tylko HTTPS.

### P12: Gdzie wykonywane są działania (użytkownik vs system)?
Walidacja danych: klient i serwer; obliczenia cen i rabatów: tylko serwer; walidacja płatności Stripe: klient i serwer.

### P13: Gdzie mogą trafiać dane?
PostgreSQL (podstawowe), Redis (cache), S3 (faktury), Stripe (płatności).

### P14: Gdzie dane NIE mogą trafiać?
Dane osobowe klientów EU nie opuszczają regionu eu-central-1; faktury są przenoszone do SAP w regionie eu-central-1.

### P15: Gdzie są granice systemu?
System nie obsługuje magazynu — integruje się z zewnętrznym WMS przez REST.

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P16: Gdzie łączą się systemy zewnętrzne?
Stripe (płatności), SendGrid (email), Allegro API (sync produktów).

### P17: Gdzie dostęp jest ograniczony?
Panel admina dostępny tylko z VPN firmowego (zakres IP 10.0.0.0/8).

### P18: Gdzie mogą wystąpić awarie?
Bramka płatności, dostawca emaili, warstwa cache Redis.

### P19: Gdzie system musi zawsze odpowiadać?
Endpoint /api/orders/create — nawet w trybie degraded musi przyjąć zamówienie.

### P20: Gdzie zachowanie różni się w zależności od lokalizacji?
VAT i waluta zależą od kraju klienta; PL=23%, DE=19%, UK=20%.

## KIEDY — WHEN — Czas i wyzwalacze

### P21: Kiedy coś jest tworzone?
Zamówienie tworzy się przy POST /api/orders; status 'robocze' do potwierdzenia.

### P22: Kiedy coś jest aktualizowane?
Status zamówienia po webhooku ze Stripe; stan magazynu po pickingu w WMS.

### P23: Kiedy coś jest usuwane?
Zamówienia anulowane > 90 dni — soft delete; logi audytowe — nigdy.

> ⚠ **Ambiguity Tax:** `nigdy` — rozważ doprecyzowanie.

### P24: Kiedy rozpoczyna się proces?
Wysyłka rozpoczyna się gdy płatność == 'opłacone' I produkty są w magazynie.

### P25: Kiedy kończy się proces?
Zamówienie zamknięte gdy 'dostarczone' + 14 dni minęło bez reklamacji.

### P26: Kiedy system musi odpowiedzieć natychmiast?
Wszystkie operacje synchroniczne API < 500 ms p99.

### P27: Kiedy może odpowiedzieć później?
Generowanie faktur PDF i wysyłka emaili — async, do 5 min.

### P28: Kiedy system powinien ponowić próbę?
Webhooki Stripe: 3 ponowienia z exponential backoff (1s, 5s, 25s).

### P29: Kiedy system powinien blokować działania?
Nowe zamówienia blokowane gdy klient ma > 3 niezapłacone faktury.

### P30: Kiedy coś wygasa?
Sesje użytkownika: 30 min; tokeny resetu hasła: 1h; rezerwacja produktu: 15 min.

## KTO — WHO — Aktorzy i uprawnienia

### P31: Kto może korzystać z systemu?
Klienci (zarejestrowani), Pracownicy obsługi, Administrator.

### P32: Kto może zobaczyć co?
Klienci: informacje o swoich zamówieniach; Pracownicy: wszystkie zamówienia z odpowiedniej strefy; Administrator: wszystko.

> ⚠ **Ambiguity Tax:** `wszystko` — rozważ doprecyzowanie.

### P33: Kto może tworzyć elementy?
Klienci tworzą zamówienia; Administrator tworzy produkty i kategorie.

### P34: Kto może aktualizować elementy?
Klienci: adres dostawy, informacje o płatności; Pracownicy: status zamówień; Administrator: wszystkie elementy.

### P35: Kto może usuwać elementy?
Tylko Administrator może wykonać hard-delete; Klienci mogą anulować swoje zamówienia.

### P36: Kto nie ma dostępu do określonych danych?
Pracownicy nie widzą danych płatności (tylko status); tylko Administrator widzi pełne dane karty.

### P37: Kto zatwierdza ważne działania?
Zwroty > 1000 PLN wymagają zatwierdzenia drugiego pracownika (4-eyes).

### P38: Kto wyzwala kluczowe zdarzenia?
Wysyłkę wyzwala Pracownik Magazynu po pickingu; webhook Stripe wyzwala status płatności.

### P39: Kto jest odpowiedzialny za działania?
Każde działanie ma actor_id w logu audytu (user lub 'system').

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P40: Komu nigdy nie wolno działać?
Klienci nie mogą modyfikować właściciela zamówienia; Pracownicy nie mogą zmieniać cen historycznych.

## DLACZEGO — WHY — Reguły i ograniczenia

### P41: Dlaczego ten system istnieje?
Aby umożliwić sprzedaż 24/7 z automatyzacją obsługi zamówień (cel: 10k zamówień/dzień).

### P42: Dlaczego każda funkcja istnieje?
Anulowanie do 1h: zgodność z UE Right of Withdrawal + redukcja chargebacków.

### P43: Dlaczego określone działania są dozwolone?
Edycja adresu do wysyłki: 30% klientów się myli przy pierwszym wpisaniu.

### P44: Dlaczego określone działania są blokowane?
Brak dodawania pozycji po opłaceniu: każda zmiana wymagałaby ponownej autoryzacji płatności.

### P45: Dlaczego część danych jest objęta ograniczeniami?
Dane PII tylko w EU: zgodność z RODO art. 44-49 (transfer do państw trzecich).

### P46: Dlaczego walidacje są potrzebne?
Walidacja kodu pocztowego zapobiega 12% błędom dostawy z poprzedniego roku.

### P47: Dlaczego czas ma znaczenie?
Rezerwacja 15 min: bilans między doświadczeniem klienta a dostępnością stocka.

### P48: Dlaczego część działań jest nieodwracalna?
Wysłana faktura ma numer prawny; korekta wymaga osobnego dokumentu (księgowość).

### P49: Dlaczego te ograniczenia są egzekwowane?
Limit 3 niezapłacone: chroni przed nadużyciami i windykacją.

### P50: Dlaczego system powinien zgłaszać błąd zamiast zgadywać?
Złe zgadnięcie ceny = strata pieniędzy + utrata zaufania; lepiej fail-fast.

## JAK — HOW — Mechanizmy i tech

### P51: Jak system reaguje na działania użytkownika?
System reaguje na działania użytkownika poprzez zaktualizowanie stanu bazy danych i synchronizację z Stripe. Dla nowych zamówień POST /orders, idempotency-key wymagany.

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P52: Jak zachowuje się, gdy brakuje danych?
Gdy brakuje danych, system zwraca 400 Bad Request z listą niepełnych pól; nigdy nie używa defaultów.

> ⚠ **Ambiguity Tax:** `nigdy`, `system` — rozważ doprecyzowanie.

### P53: Jak obsługuje nieprawidłowe dane wejściowe?
Nieprawidłowe dane wejściowe są odrzucane z kodem błędu 400 i wiadomością specyficzna dla typu błędu, np. 'field_required'.

### P54: Jak obsługuje błędy?
Błędy obsługiwane za pomocą error envelope: {code, message_pl, message_en, trace_id}; wszystkie 5xx logowane do pliku i wysyłane do monitoringu.

### P55: Jak zachowuje się, gdy coś zawiedzie?
Gdy coś zawiedzie (np. WMS offline), system przechodzi w tryb degradowany: zamówienia są zapisywane do kolejki i przetwarzane po powrocie usługi, płatność jest weryfikowana asynchronicznie.

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P56: Jak odzyskuje sprawność po awarii?
System używa patternu outbox + idempotent consumers; regrupowanie i odzyskiwanie zdarzeń zapisanych do kolejki po awarii.

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P57: Jak egzekwuje reguły?
Reguły biznesowe są egzekwowane w warstwie domeny, nie w API ani DB. Zmiany w regułach dokonywane są jedno miejsce i automatycznie propagowane do wszystkich punktów wyjściowych.

> ⚠ **Ambiguity Tax:** `automatycznie` — rozważ doprecyzowanie.

### P58: Jak zapobiega nieoczekiwanemu zachowaniu?
System zapobiega nieoczekiwanemu zachowaniu poprzez kontrakty API wersjonowane (v1.2) i testy property-based dla reguł cenowych, wykonane raz na tydzień.

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P59: Jak zachowuje się pod obciążeniem?
Pod obciążeniem system ma limit 100 żądań na sekundę na użytkownika z użyciem rate limiting; circuit breaker na zewnętrznych API Stripe i WMS zapobiega przekroczeniu granic.

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

### P60: Jak utrzymuje spójność?
System utrzymuje spójność poprzez transakcje DB dla operacji atomowych (np. tworzenie zamówienia) oraz saga pattern dla rozproszonych operacji (płatność + wysyłka).

> ⚠ **Ambiguity Tax:** `system` — rozważ doprecyzowanie.

## ILE — HOW MUCH — Skala i koszty

### P61: Ilu użytkowników będzie korzystać z systemu jednocześnie?
Peak 5000 concurrent users, average 800; target scalability to 20k.

### P62: Jaki jest maksymalny akceptowalny czas odpowiedzi?
p50 < 100ms, p95 < 300ms, p99 < 500ms for read operations.

### P63: Jaka ilość danych będzie przetwarzana (dziennie/miesięcznie)?
10k orders/day, 300k/month; ~50 GB new data/month.

### P64: Jaki jest budżet kosztów operacyjnych?
Max 0.05 PLN per order (compute + storage + integrations).

### P65: Jaki poziom dostępności (uptime) jest wymagany?
99.9% uptime (43 min downtime/month); checkout: 99.95%.

### P66: Jak długo dane muszą być przechowywane?
Orders: 5 years (PL law), audit logs: 2 years, sessions: 30 days.

### P67: Ile równoległych operacji system musi obsłużyć?
1000 concurrent transactions for checkout; 10k concurrent reads of catalog.

### P68: Jakie są limity rozmiaru danych wejściowych/wyjściowych?
Body request max 1 MB; upload invoice max 10 MB; list items max 100.

### P69: Ile czasu może zająć przetwarzanie zadań asynchronicznych?
Generating invoices < 30s; sync with Allegro < 5 min; monthly reports < 1h.

### P70: Jakie są progi skalowania?
Auto-scale up when CPU > 70% for 5 minutes; scale down when < 30% for 15 minutes.

## CO JEŚLI — WHAT IF — Scenariusze graniczne

### P71: Co jeśli zewnętrzne API/serwis jest niedostępny?
API Stripe down: tryb płatności 'pay later' z hold; WMS down: zamówienie w stanie 'w oczekiwaniu'; SAP down: faktura przechowywana w Redis (TTL 24h).

### P72: Co jeśli użytkownik prześle złośliwe lub nieprawidłowe dane?
Walidacja JSON Schema, sanitacja HTML w komentarzach, rate limiting per IP.

### P73: Co jeśli baza danych jest niedostępna?
Read repliki: czytamy z najnowszej dostępnej; zapisy: kolejka w Kafka, replay po recovery.

### P74: Co jeśli system jest przeciążony powyżej zakładanej przepustowości?
Rate limiting 429; priorytet checkoutu nad listingiem; 'busy page' dla nowych sesji.

### P75: Co jeśli operacja krytyczna zostanie przerwana w połowie?
Outbox + idempotent retry; saga compensation dla rozproszonych transakcji.

### P76: Co jeśli dwa procesy jednocześnie zmodyfikują ten sam zasób?
Optimistic locking z version field; konflikt → 409 Conflict, klient retry.

### P77: Co jeśli użytkownik straci połączenie podczas wieloetapowej operacji?
Checkout zachowuje stan w Redis (TTL 1h); klient może wrócić i kontynuować.

### P78: Co jeśli dane wejściowe są prawidłowe technicznie, ale logicznie sprzeczne?
Walidacje cross-field na warstwie domeny; np. data dostawy < data zamówienia → 422.

### P79: Co jeśli system nie może dotrzymać SLA?
Alert PagerDuty SEV-2 gdy p99 > 800ms przez 10 min; escalation do CTO po 30 min.

### P80: Co jeśli zmiany konfiguracji są potrzebne bez zatrzymywania systemu?
Feature flags w LaunchDarkly; rolling deploy z health checks; hot reload configów.

## JAK MIERZYĆ — HOW TO MEASURE — Obserwowalność

### P81: Po czym poznamy, że system działa poprawnie?
Conversion rate > 2.5%, error rate < 0.1%, p99 latency < 500ms, NPS > 40.

### P82: Jakie metryki biznesowe mierzą sukces?
GMV/dzień, conversion rate, AOV, refund rate, customer LTV.

### P83: Jakie metryki techniczne są kluczowe?
Request rate, error rate, latency p50/p95/p99, queue depth, DB connection pool usage.

### P84: Kiedy alert powinien obudzić inżyniera o 3 w nocy?
SEV-1: checkout error rate > 5% przez 5 min; baza niedostępna; payment provider down.

### P85: Jak wygląda 'dobra' odpowiedź systemu?
Status 2xx, latency w SLA, response zgodny z OpenAPI schema.

### P86: Jak mierzymy degradację jakości?
Tracking conversion funnel; A/B test każdej zmiany checkout > 1 tydzień.

### P87: Jakie logi są niezbędne do diagnostyki?
Structured JSON logs z trace_id, user_id, request_id; retention 30 dni hot, 1 rok cold.

### P88: Jak testujemy system przed wdrożeniem?
Unit (>80%), integration (krytyczne flow), E2E (checkout), load test (2x peak).

### P89: Jak mierzymy wpływ zmian?
Canary deploy 5% → 25% → 100%; metryki vs baseline; auto-rollback na regresji.

### P90: Jakie są kryteria akceptacji dla nowych funkcji?
Acceptance criteria w Given-When-Then; testy E2E zielone; performance regression < 5%.

## INTEGRACJE — INTEGRATIONS — Upstream/Downstream

### P91: Jakie systemy zewnętrzne dostarczają dane do systemu (inbound)?
Allegro API (katalog produktów), Stripe (płatności), WMS (wysyłka), SAP (faktury).

### P92: Do jakich systemów zewnętrznych system wysyła dane (outbound)?
Stripe (potwierdzenia płatności), SendGrid (email zwrotów i reklamacji), WMS (status zamówień), GA4 (analityka), SAP (aktualizacje faktur).

### P93: Jakie protokoły/API są używane?
REST/JSON dla Stripe, WMS oraz Allegro; webhooks z signature dla Stripe; SFTP dla SAP (dzienne batches); SMTP dla SendGrid.

### P94: Jakie są umowy SLA z zewnętrznymi systemami?
Stripe 99.99%; SendGrid 99.95%; WMS 99% (5h downtime/miesiąc); SAP best-effort.

### P95: Jakie dane są synchronizowane i jak często?
Allegro: katalog co 1h; Stripe: płatności codziennie 02:00; WMS: status zamówień real-time; SAP: faktury codziennie 04:00.

### P96: Kto odpowiada za utrzymanie każdej integracji?
Stripe/SendGrid: Platform Team; WMS: Logistics IT; SAP: Finance IT; Allegro: Catalog Team.

### P97: Jakie formaty danych są wymieniane?
JSON dla wszystkich REST; CSV/SFTP dla SAP; protobuf dla event bus wewnętrznego.

### P98: Jak system reaguje na breaking changes w API dostawców?
Wersjonowanie endpointów (v1, v2); contract tests Pact; alert na deprecation notices.

### P99: Jakie są granice odpowiedzialności?
My: integracja i mapowanie; Stripe: PCI compliance; WMS: status zamówień; SAP: faktury.

### P100: Które integracje są krytyczne dla działania systemu?
Krytyczne: Stripe, baza, Redis. Degraded-OK: SendGrid, WMS. Opcjonalne: GA4, Allegro.

---
## Zachman Summary

| Wymiar       | Wykryto |
|--------------|---------|
| Encje        | 1 ((fallback — synteza nieudana)) |
| Aktorzy      | 0 () |
| Reguły       | 0 |
| Zdarzenia    | 0 |
| Integracje   | 0 () |

## Wykryte konflikty spójności
- **Zmiany dozwolone vs zakazane** (P8 ↔ P9)  
  Nakładające się słowa: `adresu`, `dostawy`, `ilości`, `pozycji`, `stanie`, `zamówienia`
  _Te same operacje nie mogą być jednocześnie dozwolone i zakazane_
- **Informacje wymagane vs opcjonalne** (P5 ↔ P6)  
  Nakładające się słowa: `metoda`, `zamówienia`
  _Pole nie może być jednocześnie wymagane i opcjonalne_
- **Gdzie dane mogą trafiać vs gdzie nie mogą** (P13 ↔ P14)  
  Nakładające się słowa: `faktury`
  _Lokalizacje docelowe nie mogą się pokrywać_
- **Kto ma dostęp vs kto nie ma** (P32 ↔ P36)  
  Nakładające się słowa: `administrator`, `pracownicy`
  _Aktor nie może jednocześnie widzieć i nie widzieć tych samych danych_
- **Kto może działać vs komu nigdy nie wolno** (P33 ↔ P40)  
  Nakładające się słowa: `klienci`, `zamówienia`
  _Aktor nie może mieć permisji której nigdy nie ma mieć_

---
_Wygenerowano przez Logos Agent_