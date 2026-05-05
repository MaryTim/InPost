# InPost Sender Companion

**A locker recommender that optimizes for what happens when your locker is full.**

---

## Author

- **Name:** Maria Budkevich
- **Email:** mar.budkevich@gmail.com

---

## Overview

A backend service plus web demo that helps users pick a parcel locker for **sending** a package, ranking lockers not just by proximity but by **how acceptable the user's reroute would be** if the chosen locker is full when the user arrives. Built on top of the public InPost points API, with a Django + PostGIS backend and a single-page Leaflet frontend.

The core question the tool answers: *"If this locker is full when I get there, will the alternative the system reroutes me to also work for me?"*

---

## Demo & Description

### The problem

When you have a parcel to send, you walk to an InPost locker and try to drop it off. Several things can go wrong, and none of them are visible to you in advance:

- It accepts sends but is closed when you arrive.
- It's full when you arrive, so you have to walk to whichever alternative is nearest - which may not match what you needed in the first place (e.g., you needed 24/7 access; the reroute closes at 6 PM).

### The design philosophy

The tool does not predict locker fullness — the public API does not expose occupancy data. Instead, it picks lockers whose **fallback set is also acceptable**: if the primary is full when the user arrives, the nearest alternative also satisfies the same filters. A locker is "robust" if both the locker *and* its likely reroute neighbors meet the user's stated requirements. A locker that satisfies the filters but whose neighbors don't is fragile, even if it's the closest.

### What the tool does

A user opens the demo, drags a pin to their location, ticks the filters that matter to them (e.g., "24/7 only", "easy access"), and hits "Find lockers." The backend:

1. Spatially queries lockers within 500m of the anchor.
2. Drops candidates that don't satisfy the user's filters.
3. For each surviving candidate, examines its **precomputed neighbor set** — the lockers within 300m that the courier would likely reroute to. Counts how many of those neighbors *also* match the user's filters.
4. Scores each candidate using a 50/50 split of `proximity` and `fallback robustness`.
5. Returns the top 5 ranked best-first.

### Demo

The demo shows the main flow: selecting filters, ranking nearby lockers, and comparing robust versus fragile fallback clusters.


https://github.com/user-attachments/assets/e7ab21f6-d3ff-4e98-bdc6-0b81008d5aa9


### The data discoveries

**Compartment-size data is universally `NO_DATA`.** Every record returns `locker_availability.details.{A, B, C} = "NO_DATA"`. The API exposes the structure but never populates the values. Any `parcel_size` filter would be filter theater; the project drops it explicitly.

**Most "interesting" filter dimensions are universal.** Live audit against ~32,000 Polish lockers showed:

- `accepts_returns`: 100% of active lockers carry a returns function.
- `accepts_sends`: 100% of active lockers carry a send function.
- `payment_card`: 0% — InPost lockers route payment through the InPost app + PayByLink, not card terminals.

These were dropped from both the user-facing UI and the database schema. The user-facing filter set is intentionally just three: `require_24_7` (narrows ~12% of lockers), `require_easy_access` (narrows ~10%), and an optional `open_at(day, time)` for the 12% of non-24/7 lockers.

### Architecture at a glance

```
[InPost public API]                      ← walked once, cached locally
     │
     │  refresh_lockers (Django command)
     ▼
[PostgreSQL + PostGIS]                   ← 31,712 active Polish lockers
     │
     │  compute_neighbors (one-time spatial self-join in SQL)
     ▼
[Locker.neighbors JSON]                  ← precomputed "if full, where else?"
     │
     │  recommender.engine (per request)
     ▼
[POST /api/recommend]                    ← Django REST Framework endpoint
     │
     ▼
[Leaflet single-page demo]               ← served by Django at /
```

Two key architectural choices:

**Local snapshot rather than live proxy.** The dataset is ingested once via `refresh_lockers` and queried locally. Reasons: spatial preprocessing (300m neighbor sets per locker) requires the full dataset in one place; a 50ms PostGIS spatial query is dramatically cheaper than walking 68 paginated API pages per user request; the data changes slowly (lockers are physical infrastructure); an InPost API outage doesn't break our app.

**Neighbor sets precomputed via SQL spatial self-join.** For each locker, the lockers within 300m are computed once after ingestion using a single PostGIS `UPDATE ... FROM ...` statement. The bounding-box `&&` operator uses the gist spatial index to filter candidate pairs, then `ST_Distance(...::geography)` does the precise meter-distance check. The full 31,712-locker preprocessing completes in ~2 seconds.

### Filters tested and deliberately dropped

The audit story in one table:

| Filter | Live data | Status | Why |
|---|---|---|---|
| `require_24_7` | 88.4% true | **Kept** | Narrows ~12% of lockers, real signal |
| `require_easy_access` | 90.4% true | **Kept** | Narrows ~10% of lockers |
| `open_at(day, time)` | varies | **Kept** | Useful for the 12% non-24/7 lockers |
| `accepts_returns` | 100% true | Dropped | Every locker has it |
| `accepts_sends` | 100% true | Dropped | Every locker has it|
| `payment_card` | 0% true | Dropped | InPost uses app-based payment, not card terminals |
| `parcel_size` | unavailable | Dropped | API returns `NO_DATA` for every locker |

The dropped fields were also removed from the database schema and the API response, not just the UI. The schema reflects what the application actually uses.

---

## Technologies

### Backend

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.11** | Standard, well-supported |
| Web framework | **Django 5 + Django REST Framework** | GeoDjango ships with Django and handles PostGIS idiomatically; admin interface for free dataset inspection; management commands for ingestion |
| Database | **PostgreSQL 16 + PostGIS 3.4** | First-class spatial queries (radius, neighbor lookup) without writing geometry math by hand. The gist index makes the precomputed neighbor self-join run in seconds |
| API documentation | **drf-spectacular** | Auto-generates OpenAPI schema and interactive Swagger UI at `/api/docs/` |
| HTTP client (ingestion) | **httpx** | Modern, simple, async-friendly |
| Tests | **pytest + pytest-django** | Cleaner test syntax than Django's built-in `unittest.TestCase`; better assertion errors |

### Frontend

| Layer | Choice | Why |
|---|---|---|
| Map | **Leaflet 1.9** | Loaded from CDN; no build step; sufficient for the demo surface |
| HTTP | **fetch()** (vanilla JS) | No frameworks needed for a single page |

The frontend is a single HTML file served by Django at `/`. No webpack, no React, no TypeScript — by deliberate choice. The backend is the project's substance; the frontend's job is to make the backend's behavior visible.

### Containerization

| Tool | Why |
|---|---|
| **Docker Compose** | Two services (PostgreSQL+PostGIS, Django app). One command (`docker compose up`) boots the whole stack |

---

## How to run

### Prerequisites

- **Docker** and **Docker Compose v2** installed (Docker Desktop on macOS/Windows, or `docker.io` + `docker-compose-plugin` on Linux).
- A web browser (any modern Chrome/Safari/Firefox).
- Internet access on first run (to fetch the InPost dataset and pull Docker images).

No Python, Node, or Postgres installation needed on the host — everything runs inside containers.

### Build & run

```bash
# 1. Clone the repository
git clone https://github.com/MaryTim/InPost.git
cd InPost

# 2. Create the .env file from the template
cp .env.example .env

# 3. Boot the database + Django app
docker compose up -d

# 4. Apply database migrations
docker compose run --rm app python manage.py migrate

# 5. Ingest the InPost dataset (~30 seconds, walks 68 API pages)
docker compose run --rm app python manage.py refresh_lockers

# 6. Precompute neighbor sets (~2 seconds, single PostGIS spatial self-join)
docker compose run --rm app python manage.py compute_neighbors

# 7. Open the demo
open http://localhost:8000/
```

---

## What I would do with more time

**1. Real-time locker availability.** The biggest improvement would be access to live locker occupancy data. If the API exposed how full each locker is, the recommender could move to availability-aware recommendations — ranking lockers by both location and the likelihood that the user can actually send their parcel there. That would be a game changer for users: instead of choosing the nearest acceptable locker and hoping it has space, they could choose the best nearby locker with real capacity signals.

**2. More polished client experience, ideally native iOS.** My original plan included building a native iOS app, since this kind of location-based locker recommendation flow fits naturally on mobile and iOS is where I have the most experience. With more time, I would either turn the current Leaflet demo into a more polished frontend or build a partial SwiftUI client on top of the existing API. The backend is already API-first, so the main work would be around the user experience: location permissions, map interactions, filter controls, result cards, and clearer visual comparison between robust and fragile locker choices.

**3. "Where to build next" recommender.** Given the existing locker network, identify areas with high population density and weak coverage, suggesting where InPost should add lockers. Would turn the project from descriptive to prescriptive.

**4. Multi-language UI.** All filter labels, badges, and warnings are currently English. Polish translations would be the most natural next step given the dataset.

**5. CoreLocation default anchor.** Pre-fill the user's location instead of defaulting to Warsaw.

---

## AI usage

I used Claude Cowork and ChatGPT throughout the project, mostly as a sparring partner for product decisions, backend design, code review and documentation.

Specifically, AI helped with:

- **Spec and plan iteration.** I wrote the original SPEC and PLAN myself, then used AI to challenge assumptions, prune scope and stress-test the core idea.
- **API exploration debugging.** AI helped me reason through the shape of the InPost API responses, identify which fields were actually useful and avoid building filters around data that was unavailable or not meaningful.
- **Backend design review.** I used AI as a senior-engineer-style reviewer for the Django/PostGIS architecture, the recommendation flow, and the tradeoffs between live API calls and a locally ingested dataset.
- **Unit tests and documentation.** AI helped draft test cases, improve README structure and make the project narrative clearer. I reviewed and adapted the output rather than accepting it blindly.
- **General code review.** I used AI to look for dead code, confusing naming, unnecessary complexity, and places where the implementation no longer matched the README.

All AI-generated suggestions were reviewed by me before being used. The core product idea, scope decisions, implementation tradeoffs and final responsibility for the code are mine.

---

## Anything else?

### Design tradeoffs

I originally planned to build a native iOS app, since that is where I have the most experience. During implementation, I decided to prioritize the backend engine: data ingestion, spatial queries, fallback-neighbor computation, filter auditing, and the recommendation logic. The web frontend is intentionally simple and exists mainly to make the backend behavior visible.

I also cut several features after validating the API data. `accepts_returns` and `accepts_sends` looked like useful filters at first, but they did not distinguish lockers in practice. `payment_card` was also removed because it was not meaningful for this flow. Similarly, I dropped parcel-size filtering because the API did not expose reliable compartment availability data.

The result is a smaller project, but one with a clearer product idea: recommend lockers based not only on proximity, but also on how safe the fallback options are if the first locker is full.

### Scoring choice

The score uses an equal split between proximity and fallback robustness:

`0.5 * proximity + 0.5 * fallback_robustness`

That is intentional. A user who only wants the closest locker can already use a map. The purpose of this project is to show that the closest locker is not always the best choice if its nearby fallback options are poor.

### Limitations

- **The 300m fallback radius is a heuristic.** It is roughly a short walking distance, but it would need to be validated against real user reroute data.
- **Walking distance is approximated as straight-line distance.** This is acceptable for a demo in dense urban areas, but production recommendations should use actual walking routes.
- **The dataset is Polish-only by design.** I limited the project to Polish lockers to keep the dataset smaller and the demo easier to reason about. The same approach could be extended to other countries, but each market should be audited separately because locker features may differ.
- **No real-time occupancy data.** The project cannot know whether a locker is currently full. With live availability data, the recommender could become much more useful.
