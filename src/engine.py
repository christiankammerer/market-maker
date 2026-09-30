from dataclasses import dataclass
from orders import OrderBook, Order
from instrument import Instrument


class MatchingEngine:
    def __init__(self, instrument: Instrument, book: OrderBook | None):
        self.instrument = instrument
        self.book = book if book is not None else OrderBook() 

    def submit(self, order: Order) -> MatchResult:
        return None

    def cancel(self, order_id: str) -> CancelResult:
        return CancelResult()

    def _reject_reason(self, order: Order) -> str | None:
        return None

    def _crosses(self, incoming, resting): 
        pass

@dataclass
class Trade:
    price: int
    quantity: int
    aggressor_id: str
    resting_id: str
    aggressor_client_id: str
    resting_client_id: str

@dataclass
class MatchResult:
    trades: list[Trade]
    resting: Order | None
    reject_reason: str | None
    
@dataclass 
class CancelResult:
    pass