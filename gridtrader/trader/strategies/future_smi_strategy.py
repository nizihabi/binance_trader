from datetime import datetime
from ..engine import CtaEngine, EVENT_TIMER

from gridtrader.trader.object import Status
from typing import Union, Optional
from gridtrader.trader.utility import floor_to
from gridtrader.trader.object import OrderData, TickData, TradeData, ContractData
from .template import CtaTemplate
from gridtrader.trader.utility import GridPositionCalculator


class FutureSMIStrategy(CtaTemplate):
    """
    币安合约SMI策略

    """
    author = "nizihabi"

    # parameters
    lever = 5 #杠杆
    target_profit = 0.3 #目标收益

    # the strategy will stop when the price break the upper/bottom price, if you set the close_position when stop True,
    # it will automatically close your position.

    # variables
    avg_price = 0.0  # current average price for the position  持仓的均价
    cur_profit = 0.0  # current profit for the position 当前持仓收益
    total_profit = 0.0 # total profit since start 当前总收益
    trade_times = 0  # trade times

    parameters = ["lever", "target_profit"]

    variables = ["avg_price", "cur_profit","total_profit", "trade_times"]

    def __init__(self, cta_engine: CtaEngine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.long_orders_dict = {}  # long orders dict {'orderid': price}
        self.short_orders_dict = {}  # short orders dict {'orderid': price}

        self.tick: Union[TickData, None] = None
        self.contract_data: Optional[ContractData] = None

        self.timer_count = 0

    def on_init(self):
        """
        Callback when strategy is inited.
        """
        self.write_log("Init Strategy")

    def on_start(self):
        """
        Callback when strategy is started.
        """
        self.write_log("Start Strategy")
        self.contract_data: Optional[ContractData] = self.cta_engine.main_engine.get_contract(self.vt_symbol)

        if not self.contract_data:
            self.write_log(f"Could Not Find The Symbol:{self.vt_symbol}, Please Connect the Api First.")
            self.inited = False
        else:
            self.inited = True

        

        self.cta_engine.event_engine.register(EVENT_TIMER, self.process_timer)

    def on_stop(self):
        """
        Callback when strategy is stopped.
        """
        self.write_log("Stop Strategy")
        self.cta_engine.event_engine.unregister(EVENT_TIMER, self.process_timer)

    def process_timer(self, event):
        self.timer_count += 1
        if self.timer_count >= 30:
            self.write_log(datetime.now())
            self.timer_count = 0
            self.put_event()

    def on_tick(self, tick: TickData):
        """
        Callback of new tick data update.
        """
        
        if tick and tick.bid_price_1 > 0 and self.contract_data:
            self.tick = tick
            

    def on_order(self, order: OrderData):
        """
        Callback of new order data update.
        """
        self.put_event()

    def on_trade(self, trade: TradeData):
        """
        Callback of new trade data update.
        """
        self.put_event()
