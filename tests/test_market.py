import pytest 

from engine import MatchingEngine, MatchResult, CancelResult, Trade
from orders import Side, Order, OrderBook
from instrument import Instrument

@pytest.fixture
def engine():
    return MatchingEngine(Instrument("WHEAT", 0.1))

def test_buy_at_ask_fills_completely(engine):
    ask = Order("ask", "seller", Side.SELL, 100, 10)
    bid = Order("bid", "buyer", Side.BUY, 100, 10)

    engine.submit(ask)
    result = engine.submit(bid)
    assert [(t.quantity, t.price) for t in result.trades] == [(10, 100)]
    assert result.resting is None
    assert "ask" not in engine.book
    assert "bid" not in engine.book

def test_cancel_order(engine): 
    ask = Order("ask", "seller", Side.SELL, 100, 10)
    bid = Order("bid", "buyer", Side.BUY, 100, 10)
    engine.submit(ask)
    cancel_result = engine.cancel(ask.id)
    match_result = engine.submit(bid)
    assert cancel_result == CancelResult(ask)
    assert "ask" not in engine.book
    assert "bid" in engine.book
    assert match_result == MatchResult([], bid, None)

def test_cancel_none_existing_order(engine):
    ask = Order("ask", "seller", Side.SELL, 100, 10)
    engine.submit(ask)
    with pytest.raises(KeyError, match = "Order with id bid does not exist"):
        cancel_result = engine.cancel("bid")
    assert "ask" in engine.book

def test_best_ask(engine): 
    ask1 = Order("ask1", "seller", Side.SELL, 100, 10)
    engine.submit(ask1)
    ask2= Order("ask2", "seller", Side.SELL, 80, 10)
    engine.submit(ask2)
    ask3 = Order("ask3", "seller", Side.SELL, 70, 10)
    engine.submit(ask3)
    ask4 = Order("ask4", "seller", Side.SELL, 80, 10)
    engine.submit(ask4)
    ask5 = Order("ask5", "seller", Side.SELL, 70, 10)
    engine.submit(ask5)
    assert engine.book.best_ask() == ask3
    assert engine.book.best_bid() is None

def test_best_bid(engine): 
    bid1 = Order("bid1", "buyer", Side.BUY, 100, 10)
    engine.submit(bid1)
    bid2 = Order("bid2", "buyer", Side.BUY, 120, 10)
    engine.submit(bid2)
    bid3 = Order("bid3", "buyer", Side.BUY, 110, 10)
    engine.submit(bid3)
    bid4 = Order("bid4", "buyer", Side.BUY, 120, 10)
    engine.submit(bid4)
    bid5 = Order("bid5", "buyer", Side.BUY, 120, 10)
    engine.submit(bid5)
    assert engine.book.best_bid() == bid2
    assert engine.book.best_ask() is None

def test_order_rejections(engine):
    bid = Order("bid", "buyer", Side.BUY, 100, 10)
    engine.submit(bid)
    result = engine.submit(bid)
    assert result == MatchResult([], None, "duplicate order_id")
    ask = Order("ask", "seller", Side.SELL, -2, 10)
    result = engine.submit(ask)
    assert result == MatchResult([], None, "non-positive price")
    ask = Order("ask", "seller", Side.SELL, 100, 0)
    result = engine.submit(ask)
    assert result == MatchResult([], None, "non-positive quantity")

def test_partial_fill(engine):
    bid = Order("bid", "buyer", Side.BUY, 100, 10)
    engine.submit(bid)
    ask = Order("ask", "seller", Side.SELL, 80, 6)
    result = engine.submit(ask)
    assert result.trades == [Trade(100, 6, ask.id, bid.id, ask.client_id, bid.client_id)]
    assert result.resting is None
    assert engine.book.best_bid().quantity == 4
    assert "ask" not in engine.book
    ask = Order("ask", "seller", Side.SELL, 80, 10)
    result = engine.submit(ask)
    assert result.trades == [Trade(100, 4, ask.id, bid.id, ask.client_id, bid.client_id)]
    assert result.resting == Order("ask", "seller", Side.SELL, 80, 6)
    assert engine.book.best_ask().quantity == 6
    assert "bid" not in engine.book

def test_buy_below_ask_rests(engine):
    ask = Order("ask", "seller", Side.SELL, 100, 10)
    engine.submit(ask)
    bid = Order("bid", "buyer", Side.BUY, 90, 5)
    result = engine.submit(bid)
    assert result.trades == []
    assert result.resting == bid
    assert result.reject_reason is None
    assert engine.book.best_ask() == ask
    assert engine.book.best_bid() == bid

def test_buy_partially_fills_ask(engine):
    ask = Order("ask", "seller", Side.SELL, 100, 10)
    engine.submit(ask)
    bid = Order("bid", "buyer", Side.BUY, 110, 4)
    result = engine.submit(bid)
    assert result.trades == [Trade(100, 4, bid.id, ask.id, bid.client_id, ask.client_id)]
    assert result.resting is None
    assert engine.book.best_ask().quantity == 6
    assert "bid" not in engine.book

def test_buy_walks_two_price_levels(engine):
    first = Order("ask-100", "seller", Side.SELL, 100, 5)
    second = Order("ask-105", "seller", Side.SELL, 105, 5)
    too_high = Order("ask-120", "seller", Side.SELL, 120, 10)
    engine.submit(first)
    engine.submit(second)
    engine.submit(too_high)
    bid = Order("bid", "buyer", Side.BUY, 110, 12)
    result = engine.submit(bid)
    assert result.trades == [
        Trade(100, 5, "bid", "ask-100", "buyer", "seller"),
        Trade(105, 5, "bid", "ask-105", "buyer", "seller"),
    ]
    assert result.resting == Order("bid", "buyer", Side.BUY, 110, 2)
    assert engine.book.best_ask().id == "ask-120"
    assert engine.book.best_bid().quantity == 2

def test_same_price_fills_oldest_first(engine):
    first = Order("first", "seller-a", Side.SELL, 100, 4)
    second = Order("second", "seller-b", Side.SELL, 100, 4)
    engine.submit(first)
    engine.submit(second)
    bid = Order("bid", "buyer", Side.BUY, 100, 6)
    result = engine.submit(bid)
    assert result.trades == [
        Trade(100, 4, "bid", "first", "buyer", "seller-a"),
        Trade(100, 2, "bid", "second", "buyer", "seller-b"),
    ]
    assert result.resting is None
    assert engine.book.best_ask().id == "second"
    assert engine.book.best_ask().quantity == 2
    assert "first" not in engine.book

def test_cancel_order_behind_front(engine):
    front = Order("front", "seller-a", Side.SELL, 100, 5)
    behind = Order("behind", "seller-b", Side.SELL, 100, 7)
    engine.submit(front)
    engine.submit(behind)
    cancelled = engine.cancel("behind")
    assert cancelled == CancelResult(behind)
    assert engine.book.best_ask() == front
    assert "behind" not in engine.book
    bid = Order("bid", "buyer", Side.BUY, 100, 5)
    result = engine.submit(bid)
    assert result.trades == [Trade(100, 5, "bid", "front", "buyer", "seller-a")]
    assert engine.book.best_ask() is None
