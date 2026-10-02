from dataclasses import dataclass
from orders import OrderBook, Order, Side
from instrument import Instrument


class MatchingEngine:
    def __init__(self, instrument: Instrument, book: OrderBook | None = None):
        self.instrument = instrument
        self.book = book if book is not None else OrderBook() 

    def submit(self, order: Order) -> MatchResult:
        if self._reject_reason(order):
            return MatchResult(trades=[], resting=None, reject_reason=self._reject_reason(order))
        trades = []
        while order.quantity > 0:
            resting = self.book.best_bid() if order.side == Side.SELL else self.book.best_ask()
            if resting is None or not self._crosses(order, resting): 
                break
            qty = min(order.quantity, resting.quantity)
            self.book.consume(resting.id, qty)
            order.quantity -= qty
            trades.append(Trade(resting.price, qty, order.id, resting.id, 
                                order.client_id, resting.client_id))
        resting_order = None
        if order.quantity > 0:
            self.book.add(order)
            resting_order = order
        return MatchResult(trades, resting_order, None)

    def cancel(self, order_id: str) -> CancelResult:
        order = self.book.cancel(order_id)
        return CancelResult(order)

    def _reject_reason(self, order: Order) -> str | None:
        if order.id in self.book:
            return "duplicate order_id"
        if order.price <= 0:
            return "non-positive price"
        if order.quantity <= 0:
            return "non-positive quantity"

    def _crosses(self, incoming, resting): 
        # Return True if ask price is below highest bid, or bid price is above lowest ask
        return incoming.side == Side.SELL and incoming.price <= resting.price \
            or incoming.side == Side.BUY and incoming.price >= resting.price


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
    order: Order | None 