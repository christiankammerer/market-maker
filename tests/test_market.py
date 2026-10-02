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