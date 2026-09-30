from dataclasses import dataclass
from collections import deque
from sortedcontainers import SortedDict    
from enum import Enum
from uuid import uuid4
from engine import CancelResult, MatchResult

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

    def best_ask(self) -> Order | None:
        if len(self.asks) == 0: 
            print(self.asks.peekitem(0)[0])
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

    def cancel(self, order_id: str) -> 

if __name__ == "__main__":
    book = OrderBook()
    order1 = Order(str(uuid4()), str(uuid4()), Side.SELL, 100, 20)
    order2 = Order(str(uuid4()), str(uuid4()), Side.BUY, 115, 20)
    order3 = Order(str(uuid4()), str(uuid4()), Side.BUY, 108, 20)
    order4 = Order(str(uuid4()), str(uuid4()), Side.SELL, 120, 20)
    order5 = Order(str(uuid4()), str(uuid4()), Side.SELL, 111, 20)
    order6 = Order(str(uuid4()), str(uuid4()), Side.BUY, 100, 20)
    book.add(order1)
    book.add(order2)
    book.add(order3)
    book.add(order4)
    book.add(order5)
    book.add(order6)
