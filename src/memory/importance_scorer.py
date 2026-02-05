from typing import List

from src.event_schemas import EventRecord

SALIENCE_WEIGHT = {
    "TODO": 1.0,
    "ISSUE": 0.95,
    "DECISION": 0.9,
    "NOTE": 0.5,
    "ACTION": 0.6,
}


def score_events(events: List[EventRecord], recency_weight: float = 0.2) -> List[EventRecord]:
    n = len(events)
    for i, ev in enumerate(events):
        sal = SALIENCE_WEIGHT.get(ev.event_type, 0.5)
        rec = (i + 1) / max(n, 1)
        score = sal * (1.0 - recency_weight) + rec * recency_weight
        ev.score = round(score, 4)
    return events
