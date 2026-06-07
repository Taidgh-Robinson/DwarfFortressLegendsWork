# DFLLM — Dwarf Fortress Legends Loader & Model

Parses a Dwarf Fortress Legends mode XML export (`a.xml`) and loads it into PostgreSQL using [SQLModel](https://sqlmodel.tiangolo.com/) for type-safe, validated models.

## Quick Start

```bash
docker compose up --build
```

This starts a Postgres 16 container, then runs the seed service which:

1. Drops and recreates all tables
2. Parses `a.xml` using a generic, data-driven XML parser
3. Inserts all parsed objects in batches of 1000

## Models

Every major Legends XML element has a corresponding SQLModel in `models/`:

| Model | XML Tag | File |
|---|---|---|
| Region | `<region>` | `models/region.py` |
| UndergroundRegion | `<underground_region>` | `models/underground_region.py` |
| Site | `<site>` | `models/site.py` |
| Artifact | `<artifact>` | `models/artifact.py` |
| HistoricalFigure | `<historical_figure>` | `models/historical_figure.py` |
| HistoricalEvent | `<historical_event>` | `models/historical_event.py` |
| HistoricalEventCollection | `<historical_event_collection>` | `models/historical_event_collection.py` |
| HistoricalEra | `<historical_era>` | `models/historical_era.py` |
| WrittenContent | `<written_content>` | `models/written_content.py` |
| PoeticForm | `<poetic_form>` | `models/poetic_form.py` |
| DanceForm | `<dance_form>` | `models/dance_form.py` |
| MusicalForm | `<musical_form>` | `models/musical_form.py` |
| Entity | `<entity>` | `models/entity.py` |
| EntityPopulation | `<entity_population>` | `models/entity_population.py` |

Nested sub-models (e.g. `Structure` inside `Site`, `Honor` inside `Entity`) are stored as JSON columns.

## Parser

`test.py` contains a generic `process_element()` function that introspects SQLModel fields at runtime, handling:

- Scalar fields (strings, ints, bools)
- Nested sub-models (recursive parsing)
- List fields (both primitive lists and lists of sub-models)
- Tag remapping for Python keyword conflicts (`return` → `return_`)
- Type coercion for boolean and sentinel (`-1` → `None`) values

To add a new XML element type, add the model class to `models/`, register it in `TAG_TO_MODEL`, and it's handled automatically.

## Standalone Usage

```bash
# Parse and print all objects
uv run test.py

# Load into database (requires Postgres running)
uv run load_data.py
```

## Database

Connection configured via `DATABASE_URL` env var (defaults to `postgresql://dfuser:dfpass@localhost:5432/dflegends`).

## Project Status

All Legends XML types except `world_constructions` are supported.
