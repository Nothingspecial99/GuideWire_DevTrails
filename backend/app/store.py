from datetime import datetime
from itertools import count

from .models import Claim, LocationPing, Policy, Payout, TriggerEvent, Worker


class MemoryStore:
    def __init__(self) -> None:
        self.workers: dict[str, Worker] = {}
        self.locations: dict[str, list[LocationPing]] = {}
        self.policies: dict[str, Policy] = {}
        self.events: dict[str, TriggerEvent] = {}
        self.claims: dict[str, Claim] = {}
        self.payouts: dict[str, Payout] = {}
        self.zone_event_counter: dict[str, int] = {}
        self._worker_seq = count(1)
        self._policy_seq = count(1)
        self._event_seq = count(1)
        self._claim_seq = count(1)
        self._payout_seq = count(1)

    def new_worker_id(self) -> str:
        return f"w{next(self._worker_seq)}"

    def new_policy_id(self) -> str:
        return f"p{next(self._policy_seq)}"

    def new_event_id(self) -> str:
        return f"e{next(self._event_seq)}"

    def new_claim_id(self) -> str:
        return f"c{next(self._claim_seq)}"

    def new_payout_id(self) -> str:
        return f"t{next(self._payout_seq)}"

    def now(self) -> datetime:
        return datetime.utcnow()


store = MemoryStore()
