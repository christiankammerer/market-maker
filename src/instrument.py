from dataclasses import dataclass
@dataclass(frozen=True)
class Instrument:
    symbol: str
    tick_size: float

    def ticks_to_price(self, ticks: int) -> float:
        return ticks * self.tick_size

    def price_to_ticks(self, price: float) -> int:
        return int(price // self.tick_size)