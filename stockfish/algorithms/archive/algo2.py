from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


"""
Algo1 refactored
"""
class Algo2:
    """
    Contains the logic for the trading algorithm.
    """

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                self.buy_all(state, order_depth.sell_orders, product, orders)
                self.sell_all(state, order_depth.buy_orders, product, orders)
                # Add all the above orders to the result dict
                result[product] = orders

        return result

    def buy_all(self, state: TradingState, orders: Dict[int, int], product: str, all_orders: list[Order]):
        acceptable_price = 10000
        # If statement checks if there are any SELL orders in the PEARLS market
        if len(orders) > 0:
            # Variable keeping track of how much room we have left to buy
            # We can only buy up to 20 PEARLS at a time
            # This variable is initialized to 20, and is decremented by the volume of each order
            limit = 20 - state.position[product] if product in state.position else 20
            # Go through every single sell order from lowest to acceptable_price - 1
            for best_ask in range(min(orders.keys()), acceptable_price):
                # Check if the current price has any orders
                if best_ask in orders:
                    # If there are orders, retrieve the volume
                    best_ask_volume = min(orders[best_ask], limit)
                    # Send a BUY order at the price level of the ask, with the same quantity
                    self.display_buy(best_ask_volume, best_ask)
                    all_orders.append(Order(product, best_ask, best_ask_volume))
                    limit -= best_ask_volume
                    if limit <= 0:
                        break

    def sell_all(self, state: TradingState, orders: Dict[int, int], product: str, all_orders: list[Order]):
        acceptable_price = 10000
        if len(orders) != 0:
            limit = state.position[product] + 20 if product in state.position else 20
            # Go through every single buy order from highest to acceptable_price + 1
            for best_bid in range(max(orders.keys()), acceptable_price, -1):
                # Check if the current price has any orders
                if best_bid in orders:
                    # If there are orders, retrieve the volume
                    best_bid_volume = min(orders[best_bid], limit)
                    # Send a SELL order at the price level of the bid, with the same quantity
                    self.display_sell(best_bid_volume, best_bid)
                    all_orders.append(Order(product, best_bid, -best_bid_volume))
                    limit -= best_bid_volume
                    if limit <= 0:
                        break

    def display_buy(self, best_volume: int, best_ask_or_bid: int):
        self.display_buy_or_sell("BUY", best_volume, best_ask_or_bid)

    def display_sell(self, best_volume: int, best_ask_or_bid: int):
        self.display_buy_or_sell("SELL", best_volume, best_ask_or_bid)

    def display_buy_or_sell(self, key_string: str, best_volume: int, best_ask_or_bid: int):
        print(key_string, str(best_volume) + "x", best_ask_or_bid)
