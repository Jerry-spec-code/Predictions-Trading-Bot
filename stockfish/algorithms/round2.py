"""
Round 2
"""
import math
from typing import Dict, List
from stockfish.datamodel import (
    Order, TradingState
)
from stockfish.utils import (
    get_moving_average,
    get_mid_price,
    get_spread,
    place_buy_order,
    place_sell_order,
    get_vwap_bid,
    get_vwap_ask,
    get_best_ask,
    get_best_bid,
    is_increasing,
    is_decreasing
)


class Round2:
    """
    Round 2 PnL: 28862 (Pearls: 1216, Bananas: 1356, Coconuts: 10272, Pina Coladas: 16019)
    Trading a stable, trending, and correlated market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
        self.spread_coefficient = {"PEARLS": 0.4, "BANANAS": 0.3, "COCONUTS": 0.2, "PINA_COLADAS": 0.1}
        self.moving_average_window = {"PEARLS": 5, "BANANAS": 5, "COCONUTS": 1, "PINA_COLADAS": 1}
        self.trend_length = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 9, "PINA_COLADAS": 0}
        self.mid_prices = {"PEARLS": [], "BANANAS": [], "COCONUTS": [], "PINA_COLADAS": []}
        self.vwap_bid_prices = {"PEARLS": [], "BANANAS": [], "COCONUTS": [], "PINA_COLADAS": []}
        self.vwap_ask_prices = {"PEARLS": [], "BANANAS": [], "COCONUTS": [], "PINA_COLADAS": []}
        self.correlation = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0, "PINA_COLADAS": 1.875}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []

            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, best_ask_volume = get_best_ask(order_depth)
            best_bid, best_bid_volume = get_best_bid(order_depth)
            best_ask_volume = min(-1 * best_ask_volume, buy_volume)
            best_bid_volume = min(best_bid_volume, sell_volume)
            vwap_ask = get_vwap_ask(order_depth)
            vwap_bid = get_vwap_bid(order_depth)
            mid_price = get_mid_price(order_depth)
            self.vwap_bid_prices[product].append(vwap_bid)
            self.vwap_ask_prices[product].append(vwap_ask)
            self.mid_prices[product].append(mid_price)

            if product == "PEARLS":
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == "BANANAS":
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == "COCONUTS":
                if len(self.vwap_bid_prices[product]) > self.trend_length[product] and self.sell_signal(self.vwap_bid_prices[product], self.trend_length[product]):
                    place_sell_order(product, orders, best_bid, best_bid_volume)
                if len(self.vwap_ask_prices[product]) > self.trend_length[product] and self.buy_signal(self.vwap_ask_prices[product], self.trend_length[product]):
                    place_buy_order(product, orders, best_ask, best_ask_volume)

            if product == "PINA_COLADAS":
                mid_price_coco = get_mid_price(state.order_depths["COCONUTS"])
                actual_correlation = mid_price / mid_price_coco
                target_correlation = self.correlation[product]
                if actual_correlation < target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] < self.mid_prices["COCONUTS"][-2]:
                    place_buy_order(product, orders, best_ask, best_ask_volume)
                if actual_correlation > target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] > self.mid_prices["COCONUTS"][-2]:
                    place_sell_order(product, orders, best_bid, best_bid_volume)

            result[product] = orders

        return result

    def sell_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] < vwaps[-2] and is_increasing(vwaps[-1-min_num_of_data:-1])

    def buy_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] > vwaps[-2] and is_decreasing(vwaps[-1-min_num_of_data:-1])
