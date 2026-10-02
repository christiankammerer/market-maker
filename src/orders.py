from dataclasses import dataclass
from collections import deque
from sortedcontainers import SortedDict    
from enum import Enum
from uuid import uuid4

class Side(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Order:
    id: str
    client_id: str
    side: Side
    # Price and quantity are integers, in order to avoid messy float arithmetics. Both represent discrete tick sizes
    price: int 
    quantity: int

class OrderBook:
    def __init__(self):
        self.asks = SortedDict()
        self.bids = SortedDict()
        self.orders_by_id = dict()

    def add(self, order: Order):
        if order.side == Side.SELL:
            if self.asks.get(order.price):
                self.asks[order.price].append(order)
            else: 
                self.asks[order.price] = deque([order])
        elif order.side == Side.BUY:
            if self.bids.get(order.price):
                self.bids[order.price].append(order)
            else: 
                self.bids[order.price] = deque([order])
        self.orders_by_id[order.id] = order

    def consume(self, order_id: str, quantity: int) -> None:
        order = self.orders_by_id[order_id]
        front = self.best_ask() if order.side == Side.SELL else self.best_bid()
        if front is None or front.id != order_id:
            raise ValueError(f"{order_id} is not at the inside")
        elif quantity <= 0 or quantity > order.quantity:
            raise ValueError(f"cannot consume {quantity} from {order_id}")
        levels = self.asks if order.side == Side.SELL else self.bids
        order.quantity -= quantity
        if order.quantity == 0:
            queue = levels[order.price]
            queue.popleft()
            del self.orders_by_id[order_id]
            if not queue:
                del levels[order.price]


    def best_ask(self) -> Order | None:
        if len(self.asks) == 0: 
            return None
        else: 
            price, queue = self.asks.peekitem(0)
            return queue[0]

    def best_bid(self) -> Order | None:
        if len(self.bids) == 0: 
            return None
        else: 
            price, queue = self.bids.peekitem(-1)
            return queue[0]

    def __str__(self) -> str:
        s = "ASKS:\n"
        for price_level in self.asks.keys():
            for order in self.asks[price_level]:
                s += str(order) + "\n" 
        s += "BIDS:\n"
        for price_level in self.bids.keys():
                for order in self.bids[price_level]:
                    s += str(order) + "\n" 
        return s

    def __contains__(self, order_id: str) -> bool:
        return order_id in self.orders_by_id

    def cancel(self, order_id: str) -> None:
        order = self.orders_by_id.get(order_id)
        if order is None:
            raise KeyError(f"Order with id {order_id} does not exist")
        del self.orders_by_id[order_id]
        levels = self.asks if order.side == Side.SELL else self.bids
        queue = levels[order.price]
        queue.remove(order)
        if not queue: # queue is now empty
            del levels[order.price]
        return order
