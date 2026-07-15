import sys
import json
from collections import defaultdict

from sqlalchemy import text

from db import get_session


HFKD_COLUMNS = [
    col for col in [
        "actor_hfid", "attacker_hfid", "attacker_general_hfid", "builder_hfid",
        "changee_hfid", "changer_hfid", "contact_hfid", "convicted_hfid",
        "corrupt_convicter_hfid", "corruptor_hfid", "creator_hfid", "fooled_hfid",
        "framer_hfid", "gambler_hfid", "giver_hist_figure_id", "group_1_hfid",
        "hfid", "hfid1", "hfid2", "hfid_target", "hist_fig_id", "hist_figure_id",
        "instigator_hfid", "interrogator_hfid", "last_owner_hfid", "leader_hfid",
        "lure_hfid", "modifier_hfid", "new_leader_hfid", "overthrown_hfid",
        "persecutor_hfid", "plotter_hfid", "pos_taker_hfid", "receiver_hist_figure_id",
        "seeker_hfid", "site_hfid", "slayer_hfid", "snatcher_hfid", "speaker_hfid",
        "student_hfid", "target_hfid", "teacher_hfid", "trader_hfid", "trickster_hfid",
        "winner_hfid", "woundee_hfid", "wounder_hfid", "acquirer_hfid",
        "coconspirator_hfid", "defender_general_hfid",
    ]
]

ENTITY_COLUMNS = [
    "acquirer_enid", "arresting_enid", "civ_entity_id", "convicter_enid",
    "dest_entity_id", "entity_1", "entity_2", "entity_id", "entity_id_1",
    "entity_id_2", "giver_entity_id", "initiating_enid", "join_entity_id",
    "joined_entity_id", "joiner_entity_id", "new_site_civ_id", "persecutor_enid",
    "receiver_entity_id", "relevant_entity_id", "site_civ_id", "site_entity_id",
    "source_entity_id", "target_enid", "trader_entity_id", "attacker_civ_id",
    "attacker_merc_enid", "confessed_after_apb_arrest_enid", "defender_civ_id",
    "defender_merc_enid", "civ_id", "resident_civ_id",
]

SITE_COLUMNS = [
    "dest_site_id", "source_site_id", "site_id", "site_id1", "site_id2",
    "site_id_1", "site_id_2",
]

ARTIFACT_COLUMNS = ["artifact_id", "slayer_item_id", "slayer_shooter_item_id"]


def _collect_referenced_ids(events):
    hfids = set()
    entity_ids = set()
    site_ids = set()
    artifact_ids = set()

    for ev in events:
        for col in HFKD_COLUMNS:
            v = getattr(ev, col, None)
            if v is not None:
                hfids.add(v)
        for col in ENTITY_COLUMNS:
            v = getattr(ev, col, None)
            if v is not None:
                entity_ids.add(v)
        for col in SITE_COLUMNS:
            v = getattr(ev, col, None)
            if v is not None:
                site_ids.add(v)
        for col in ARTIFACT_COLUMNS:
            v = getattr(ev, col, None)
            if v is not None:
                artifact_ids.add(v)

    return hfids, entity_ids, site_ids, artifact_ids


def _fetch_lookup(session, table, id_set, name_col="name"):
    if not id_set:
        return {}
    placeholders = ", ".join([f":id{i}" for i in range(len(id_set))])
    query = text(f"SELECT id, {name_col} FROM {table} WHERE id IN ({placeholders})")
    params = {f"id{i}": rid for i, rid in enumerate(id_set)}
    result = session.execute(query, params)
    return {row[0]: row[1] for row in result}


def _fetch_figure_details(session, id_set):
    if not id_set:
        return {}
    placeholders = ", ".join([f":id{i}" for i in range(len(id_set))])
    query = text(
        f"SELECT id, name, race, caste FROM historicalfigure WHERE id IN ({placeholders})"
    )
    params = {f"id{i}": rid for i, rid in enumerate(id_set)}
    result = session.execute(query, params)
    return {row[0]: {"name": row[1], "race": row[2], "caste": row[3]} for row in result}


def _event_to_dict(ev, hf_map, entity_map, site_map, artifact_map):
    d = {"id": ev.id, "type": ev.type}

    d["year"] = ev.year
    d["seconds72"] = ev.seconds72
    d["subtype"] = ev.subtype

    text_fields = [
        "action", "body_state", "cause", "circumstance", "claim", "crime",
        "dispute", "interaction", "knowledge", "link", "method", "modification",
        "mood", "name_only", "pop_race", "reason", "relationship", "secret_goal",
        "situation", "slayer_caste", "slayer_race", "state", "topic", "unit_type",
        "new_caste", "new_race", "old_caste", "old_race", "hf_rep_1_of_2",
        "hf_rep_2_of_1", "corruptor_seen_as", "target_seen_as", "top_facet",
        "top_relationship_factor", "top_value",
    ]
    for f in text_fields:
        v = getattr(ev, f, None)
        if v is not None:
            d[f] = v

    int_fields = [
        "account_shift", "allotment", "allotment_index", "ally_defense_bonus",
        "coconspirator_bonus", "pop_number_moved", "quality", "prison_months",
        "shrine_amount_destroyed", "feature_layer_id", "form_id", "identity_id",
        "identity_id1", "identity_id2", "master_wcid", "new_ab_id", "new_account",
        "old_ab_id", "old_account", "occasion_id", "pop_flid", "pop_srid",
        "position_id", "position_profile_id", "production_zone_id", "reason_id",
        "religion_id", "schedule_id", "structure_id", "subregion_id", "unit_id",
        "wcid", "wc_id", "circumstance_id", "agreement_id",
        "top_facet_modifier", "top_facet_rating", "top_relationship_modifier",
        "top_relationship_rating", "top_value_modifier", "top_value_rating",
        "relevant_id_for_method", "relevant_position_profile_id",
        "corruptor_identity", "target_identity", "building_profile_id",
        "dest_structure_id", "source_structure_id", "entity_population_id",
    ]
    for f in int_fields:
        v = getattr(ev, f, None)
        if v is not None:
            d[f] = v

    bool_fields = [
        "convict_is_contact", "death_penalty", "delegated", "detected",
        "failed_judgment_test", "first", "from_original", "held_firm_in_interrogation",
        "inherited", "partial_incorporation", "purchased_unowned", "rebuilt_ruined",
        "return_", "successful", "surveiled_coconspirator", "surveiled_contact",
        "surveiled_convicted", "surveiled_target", "wanted_and_recognized",
        "wrongful_conviction",
    ]
    for f in bool_fields:
        v = getattr(ev, f, None)
        if v is True:
            d[f] = True

    for col in HFKD_COLUMNS:
        v = getattr(ev, col, None)
        if v is not None:
            resolved = hf_map.get(v, None)
            if resolved:
                d[col.replace("_hfid", "").replace("hfid", "figure")] = resolved["name"]
            else:
                d[col] = v

    for col in ENTITY_COLUMNS:
        v = getattr(ev, col, None)
        if v is not None:
            resolved = entity_map.get(v)
            d[col.replace("_enid", "").replace("_entity_id", "").replace("entity", "entity_name")] = resolved if resolved else v

    for col in SITE_COLUMNS:
        v = getattr(ev, col, None)
        if v is not None:
            resolved = site_map.get(v)
            d[col.replace("_site_id", "").replace("site", "site_name")] = resolved if resolved else v

    for col in ARTIFACT_COLUMNS:
        v = getattr(ev, col, None)
        if v is not None:
            resolved = artifact_map.get(v)
            d[col.replace("_id", "").replace("artifact", "artifact_name")] = resolved if resolved else v

    return d


def get_year_context(year):
    with get_session() as session:
        events = session.execute(
            text("SELECT * FROM historicalevent WHERE year = :year"), {"year": year}
        ).fetchall()

        event_cols = [c for c in events[0]._mapping.keys()] if events else []
        event_dicts = []
        if events:
            hfids, entity_ids, site_ids, artifact_ids = set(), set(), set(), set()
            for row in events:
                m = row._mapping
                for col in HFKD_COLUMNS:
                    if col in m and m[col] is not None:
                        hfids.add(m[col])
                for col in ENTITY_COLUMNS:
                    if col in m and m[col] is not None:
                        entity_ids.add(m[col])
                for col in SITE_COLUMNS:
                    if col in m and m[col] is not None:
                        site_ids.add(m[col])
                for col in ARTIFACT_COLUMNS:
                    if col in m and m[col] is not None:
                        artifact_ids.add(m[col])

            hf_details = _fetch_figure_details(session, hfids)
            hf_map = {k: v for k, v in hf_details.items()}
            entity_map = _fetch_lookup(session, "entity", entity_ids)
            site_map = _fetch_lookup(session, "site", site_ids)
            artifact_map = _fetch_lookup(session, "artifact", artifact_ids)

            for row in events:
                m = row._mapping
                d = {"id": m["id"], "type": m["type"], "year": m.get("year"), "seconds72": m.get("seconds72"), "subtype": m.get("subtype")}

                for col in event_cols:
                    if col in ("id", "type", "year", "seconds72", "subtype"):
                        continue
                    v = m[col]
                    if v is None:
                        continue

                    if col in HFKD_COLUMNS:
                        resolved = hf_map.get(v)
                        if resolved:
                            d[col] = f"{resolved['name']} ({resolved['race'] or 'unknown'} {resolved['caste'] or ''})".strip()
                        else:
                            d[col] = v
                    elif col in ENTITY_COLUMNS:
                        resolved = entity_map.get(v)
                        d[col] = resolved if resolved else v
                    elif col in SITE_COLUMNS:
                        resolved = site_map.get(v)
                        d[col] = resolved if resolved else v
                    elif col in ARTIFACT_COLUMNS:
                        resolved = artifact_map.get(v)
                        d[col] = resolved if resolved else v
                    else:
                        d[col] = v

                event_dicts.append(d)

        collections = session.execute(
            text("SELECT * FROM historicaleventcollection WHERE start_year <= :year AND end_year >= :year"),
            {"year": year},
        ).fetchall()

        collection_dicts = []
        if collections:
            civ_ids = {row._mapping["civ_id"] for row in collections if row._mapping.get("civ_id")}
            civ_map = _fetch_lookup(session, "entity", civ_ids) if civ_ids else {}
            for row in collections:
                m = row._mapping
                cd = {
                    "id": m["id"],
                    "type": m["type"],
                    "start_year": m["start_year"],
                    "end_year": m["end_year"],
                    "civ": civ_map.get(m.get("civ_id"), m.get("civ_id")),
                    "event_count": len(m.get("event_ids", [])),
                }
                collection_dicts.append(cd)

        alive_figures = session.execute(
            text(
                "SELECT id, name, race, caste FROM historicalfigure "
                "WHERE (birth_year IS NULL OR birth_year <= :year) "
                "AND (death_year IS NULL OR death_year >= :year)"
            ),
            {"year": year},
        ).fetchall()

        active_sites = session.execute(text("SELECT id, name, type FROM site")).fetchall()
        active_entities = session.execute(text("SELECT id, name FROM entity")).fetchall()

        event_type_counts = defaultdict(int)
        for ev in event_dicts:
            event_type_counts[ev["type"]] += 1

    return {
        "year": year,
        "events": event_dicts,
        "event_collections": collection_dicts,
        "background": {
            "alive_figures": [{"id": r[0], "name": r[1], "race": r[2], "caste": r[3]} for r in alive_figures],
            "active_sites": [{"id": r[0], "name": r[1], "type": r[2]} for r in active_sites],
            "active_entities": [{"id": r[0], "name": r[1]} for r in active_entities],
            "total_events_this_year": len(event_dicts),
            "event_type_counts": dict(event_type_counts),
        },
    }


def get_year_text(year):
    ctx = get_year_context(year)
    lines = [f"=== Year {year} ===\n"]

    bg = ctx["background"]
    lines.append(f"Population: {len(bg['alive_figures'])} historical figures alive, {len(bg['active_sites'])} sites, {len(bg['active_entities'])} entities.\n")

    lines.append(f"Events this year: {bg['total_events_this_year']}")
    if bg["event_type_counts"]:
        for etype, count in sorted(bg["event_type_counts"].items(), key=lambda x: -x[1]):
            lines.append(f"  - {etype}: {count}")
    lines.append("")

    if ctx["event_collections"]:
        lines.append("--- Ongoing event collections ---")
        for col in ctx["event_collections"]:
            lines.append(
                f"  [{col['type']}] #{col['id']} ({col['start_year']}-{col['end_year']}) "
                f"civ={col['civ']}, {col['event_count']} events"
            )
        lines.append("")

    lines.append("--- Events ---")
    for ev in ctx["events"]:
        parts = [f"[{ev['type']}]"]
        if ev.get("subtype"):
            parts.append(f"({ev['subtype']})")
        for k, v in ev.items():
            if k in ("id", "type", "subtype", "year", "seconds72"):
                continue
            if isinstance(v, list) and len(v) == 0:
                continue
            parts.append(f"{k}={v}")
        lines.append("  " + " ".join(parts))

    return "\n".join(lines)


def get_year_json(year):
    ctx = get_year_context(year)

    def _clean(obj):
        if isinstance(obj, dict):
            return {k: _clean(v) for k, v in obj.items() if not (isinstance(v, list) and len(v) == 0)}
        if isinstance(obj, list):
            return [_clean(i) for i in obj]
        return obj

    return json.dumps(_clean(ctx), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run story.py <year> [--json]")
        sys.exit(1)

    year = int(sys.argv[1])
    use_json = "--json" in sys.argv

    if use_json:
        print(get_year_json(year))
    else:
        print(get_year_text(year))
