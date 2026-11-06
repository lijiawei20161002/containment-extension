"""Incident library: schema, loader, and analysis helpers for public agent incidents.

Design goals (see incidents/README.md):
- one JSON record per incident, claim-level evidence, explicit counting units;
- controlled vocabularies for pathway, failure mechanisms (Raftari 2026 §8),
  design propositions (§9), leading indicators (§12) and BAS layers (§11);
- lineage and date fields so the library can be split for development vs
  held-out evaluation (v2 design, docs/incident-aware-optimization.md);
- pointers to figures, specs and (future) executable replay cases.

No model calls. Pure pydantic + stdlib; duckdb is optional for queries.
"""
from __future__ import annotations

import json
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Iterable, Literal, Optional

from pydantic import BaseModel, Field, model_validator

LIBRARY_VERSION = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
RECORDS_DIR = REPO / "incidents" / "records"


# ----------------------------------------------------------------- vocabularies
class Category(str, Enum):
    agent_scope_violation = "agent_scope_violation"        # research/eval agent exceeded authorization on real systems
    evaluation_exposure = "evaluation_exposure"            # third-party cyber evaluation reached real systems
    training_time_behavior = "training_time_behavior"      # behavior inside training/eval samples (Sept 16 disclosures)
    external_attack_on_ai_infra = "external_attack_on_ai_infra"  # humans attacking AI-lab/evaluator systems
    human_directed_misuse = "human_directed_misuse"        # humans using agents offensively against third parties
    attribution_unresolved = "attribution_unresolved"      # platform abuse confirmed, AI attribution not established


class Pathway(str, Enum):
    """Raftari (2026) distinguishes the first two; the briefing requires three more."""
    adaptive_escape = "adaptive_escape"                    # agent defeated an intended isolation boundary
    misconfiguration_exposure = "misconfiguration_exposure"  # unintended live route; agent told it was simulated
    live_access_overreach = "live_access_overreach"        # internet access intended; authorization exceeded
    training_sample_boundary = "training_sample_boundary"  # crossed sample/context boundaries inside training
    external_adversary = "external_adversary"              # a person drove the harmful path
    unresolved = "unresolved"


class Mechanism(str, Enum):
    """Cross-case failure mechanisms, Raftari (2026) §8.1–8.6."""
    M1_objective_pressure_no_safe_exit = "M1"
    M2_capability_composition = "M2"
    M3_shared_state_coordination = "M3"
    M4_detection_without_escalation = "M4"
    M5_environment_grounding_audit_gaps = "M5"
    M6_fragmented_ownership = "M6"


MECHANISM_LABELS = {
    "M1": "Objective pressure without a safe terminal state",
    "M2": "Capability composition",
    "M3": "Shared services became coordination infrastructure",
    "M4": "Detection without decisive escalation",
    "M5": "Environment-grounding and audit blind spots",
    "M6": "Fragmented ownership",
}

PROPOSITION_LABELS = {
    "P1": "Containment is a system invariant",
    "P2": "Environment claims require measurement",
    "P3": "Authorization must survive configuration failure",
    "P4": "Impossible tasks are security inputs",
    "P5": "Shared state changes the threat model",
    "P6": "Effects matter more than stated intent",
    "P7": "Audit completeness must be demonstrated",
    "P8": "Resumption requires causal evidence",
    "P9": "No consequential autonomy without human accountability",
}

INDICATOR_LABELS = {  # leading-indicator vector z_t, Raftari §12
    "f": "repeated task failure",
    "p": "boundary probing",
    "x": "unexpected external contact",
    "c": "cross-run communication",
    "v": "privilege change",
    "o": "observability loss",
}

BAS_LAYERS = {
    "L1": "Executable scope and safe exit",
    "L2": "Least capability",
    "L3": "Independent containment",
    "L4": "Action and effect monitoring",
    "L5": "Response and reauthorization",
}

Status = Literal["present", "partial", "absent", "unknown"]
Tri = Literal["yes", "no", "unknown"]
Relation = Literal["violated", "demonstrated", "mixed", "not_applicable"]
EvidenceLevel = Literal["A", "B", "C"]
StopBehavior = Literal["none_observed", "self_stop_after_access", "automatic_stop", "automatic_stop_failed_then_manual",
                       "manual_stop", "contained_by_third_party", "human_stop_ignored", "retrospective_only", "not_applicable"]


# ----------------------------------------------------------------- record parts
class Source(BaseModel):
    name: str
    publisher: str
    date: Optional[str] = None          # ISO date or "2026-09" when only month known
    kind: Literal["primary", "affected_party", "independent_investigation", "researcher", "press", "litigation", "government"]
    url: Optional[str] = None
    note: Optional[str] = None


class Evidence(BaseModel):
    level: EvidenceLevel = Field(description="Highest evidence level supporting the core claim (Raftari §3.2)")
    sources: list[Source]
    confirmed_by: list[str] = Field(default_factory=list, description="Parties that confirmed the core facts")
    disputed: bool = False
    counting_unit: str = Field(description="What the reported numbers count (actions, runs, instances, organizations)")
    limits: list[str] = Field(default_factory=list, description="What the public record does not establish")


class TimelineEvent(BaseModel):
    date: str = Field(description="ISO date, 'YYYY-MM' for month precision, or free text if unknown")
    kind: Literal["occurred", "detected", "contained", "notified", "disclosed", "updated", "response"]
    label: str
    precision: Literal["day", "month", "year", "unknown"] = "day"


class Dates(BaseModel):
    occurred_start: Optional[str] = None
    occurred_end: Optional[str] = None
    detected: Optional[str] = None
    contained: Optional[str] = None
    disclosed: Optional[str] = None
    detail_report: Optional[str] = None


class Coding(BaseModel):
    """Raftari §3.3 coding dimensions, one short phrase each (lists where plural)."""
    objective: str
    capability: list[str]
    environment: str
    resource: list[str]
    boundary: str
    signals: list[str]
    actions: list[str]
    response: list[str]


class MechanismCoding(BaseModel):
    status: Status
    note: str = ""


class PropositionCoding(BaseModel):
    relation: Relation
    note: str = ""


class Impact(BaseModel):
    external_systems: Optional[int] = None
    external_systems_note: str = ""
    data_exposed: Tri = "unknown"
    credentials_exposed: Tri = "unknown"
    persistence: Tri = "unknown"
    harm_reported: str = ""


class Controls(BaseModel):
    failed: list[str] = Field(default_factory=list)
    worked: list[str] = Field(default_factory=list)
    added_after: list[str] = Field(default_factory=list)
    bas_layers_implicated: list[Literal["L1", "L2", "L3", "L4", "L5"]] = Field(default_factory=list)


class Lineage(BaseModel):
    group: str = Field(description="Shared-cause group used for lineage splits (dev vs held-out)")
    related: list[str] = Field(default_factory=list, description="Other record ids")


class Executable(BaseModel):
    replayable: bool = False
    replay_case: Optional[str] = None
    synthetic_twin: Optional[str] = None
    benign_twin: Optional[str] = None
    note: str = ""


class Provenance(BaseModel):
    record_version: str = LIBRARY_VERSION
    compiled_from: str
    compiled_on: str
    compiler: str
    review_status: Literal["draft", "reviewed", "verified"] = "draft"


# ----------------------------------------------------------------- record
class IncidentRecord(BaseModel):
    id: str = Field(pattern=r"^INC-\d{4}-\d{3}$")
    entry_number: int = Field(description="Entry number in the 27 Sep 2026 briefing")
    slug: str
    title: str
    short_title: str
    actor: str = Field(description="Organization whose model/system acted or was attacked")
    models: list[str] = Field(default_factory=list)
    category: Category
    pathway: Pathway
    pathway_note: str = ""
    summary: str
    dates: Dates
    timeline: list[TimelineEvent]
    evidence: Evidence
    coding: Coding
    mechanisms: dict[Literal["M1", "M2", "M3", "M4", "M5", "M6"], MechanismCoding]
    propositions: dict[Literal["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"], PropositionCoding]
    indicators: dict[Literal["f", "p", "x", "c", "v", "o"], Tri]
    stop_behavior: StopBehavior
    impact: Impact
    controls: Controls
    lineage: Lineage
    figure: Optional[str] = None
    figure_spec: Optional[str] = None
    executable: Executable = Field(default_factory=Executable)
    external_ids: dict[str, Optional[str]] = Field(default_factory=dict, description="AIID / MIT tracker / OECD AIM ids when known")
    provenance: Provenance

    @model_validator(mode="after")
    def _complete_codings(self):
        for k in ("M1", "M2", "M3", "M4", "M5", "M6"):
            self.mechanisms.setdefault(k, MechanismCoding(status="unknown"))
        for k in PROPOSITION_LABELS:
            self.propositions.setdefault(k, PropositionCoding(relation="not_applicable"))
        for k in INDICATOR_LABELS:
            self.indicators.setdefault(k, "unknown")
        return self

    # ------------------------------------------------------------- derived
    @staticmethod
    def _parse(d: Optional[str]) -> Optional[date]:
        if not d:
            return None
        parts = d.split("-")
        try:
            if len(parts) == 3:
                return date(int(parts[0]), int(parts[1]), int(parts[2]))
            if len(parts) == 2:
                return date(int(parts[0]), int(parts[1]), 15)
            if len(parts) == 1 and parts[0].isdigit():
                return date(int(parts[0]), 7, 1)
        except ValueError:
            return None
        return None

    def latency_days(self, start: str, end: str) -> Optional[int]:
        a, b = self._parse(getattr(self.dates, start)), self._parse(getattr(self.dates, end))
        return (b - a).days if a and b else None

    @property
    def detection_latency_days(self) -> Optional[int]:
        return self.latency_days("occurred_start", "detected")

    @property
    def disclosure_latency_days(self) -> Optional[int]:
        return self.latency_days("occurred_start", "disclosed")


# ----------------------------------------------------------------- io
def load_records(records_dir: Path = RECORDS_DIR) -> list[IncidentRecord]:
    recs = [IncidentRecord.model_validate_json(p.read_text(encoding="utf-8")) for p in sorted(records_dir.glob("*.json"))]
    return sorted(recs, key=lambda r: r.entry_number)


def write_record(rec: IncidentRecord, records_dir: Path = RECORDS_DIR) -> Path:
    records_dir.mkdir(parents=True, exist_ok=True)
    p = records_dir / f"{rec.entry_number:02d}-{rec.slug}.json"
    p.write_text(rec.model_dump_json(indent=1, exclude_none=False), encoding="utf-8")
    return p


def json_schema() -> dict:
    return IncidentRecord.model_json_schema()


def taxonomy() -> dict:
    return {
        "library_version": LIBRARY_VERSION,
        "categories": [c.value for c in Category],
        "pathways": {p.value: p.name for p in Pathway},
        "mechanisms": MECHANISM_LABELS,
        "propositions": PROPOSITION_LABELS,
        "indicators": INDICATOR_LABELS,
        "bas_layers": BAS_LAYERS,
        "evidence_levels": {"A": "primary, attributable (incident party, technical report, regulator)",
                            "B": "reputable secondary reporting with clear attribution",
                            "C": "unverified synthesis or inference"},
    }


# ----------------------------------------------------------------- tabular views
def flat_rows(recs: Iterable[IncidentRecord]) -> list[dict]:
    rows = []
    for r in recs:
        row = dict(id=r.id, n=r.entry_number, short_title=r.short_title, actor=r.actor, category=r.category.value,
                   pathway=r.pathway.value, evidence_level=r.evidence.level, stop_behavior=r.stop_behavior,
                   occurred_start=r.dates.occurred_start, detected=r.dates.detected, disclosed=r.dates.disclosed,
                   detection_latency_days=r.detection_latency_days, disclosure_latency_days=r.disclosure_latency_days,
                   lineage_group=r.lineage.group)
        for k, v in r.mechanisms.items():
            row[f"mech_{k}"] = v.status
        for k, v in r.propositions.items():
            row[f"prop_{k}"] = v.relation
        for k, v in r.indicators.items():
            row[f"ind_{k}"] = v
        rows.append(row)
    return rows


def to_duckdb(recs: Iterable[IncidentRecord], path: Optional[Path] = None):
    """Materialize a flat `incidents` table (and the raw JSON) in DuckDB for ad-hoc SQL."""
    import duckdb  # optional dependency

    con = duckdb.connect(str(path) if path else ":memory:")
    rows = flat_rows(recs)
    cols = list(rows[0].keys())
    con.execute(f"CREATE OR REPLACE TABLE incidents ({', '.join(c + ' VARCHAR' if not c.endswith('days') and c != 'n' else c + ' INTEGER' for c in cols)})")
    con.executemany(f"INSERT INTO incidents VALUES ({', '.join('?' for _ in cols)})", [[row[c] for c in cols] for row in rows])
    con.execute("CREATE OR REPLACE TABLE incident_json (id VARCHAR, doc JSON)")
    con.executemany("INSERT INTO incident_json VALUES (?, ?)", [[r.id, r.model_dump_json()] for r in recs])
    return con
