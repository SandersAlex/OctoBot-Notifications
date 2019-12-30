#  Drakkar-Software OctoBot-Notifications
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
from abc import abstractmethod

from octobot_trading.api.orders import get_order_exchange_name
from octobot_trading.api.trader import is_trader_simulated
from octobot_trading.data.order import Order

from octobot_commons.enums import MarkdownFormat
from octobot_commons.pretty_printer import PrettyPrinter
from octobot_notifications.notification.notification import Notification
from octobot_notifications.enums import NotificationLevel, NotificationCategory
from octobot_trading.constants import REAL_TRADER_STR, SIMULATOR_TRADER_STR


class _OrderNotification(Notification):
    def __init__(self, text, evaluator_notification: Notification):
        super().__init__("", text, MarkdownFormat.IGNORE, NotificationLevel.INFO,
                         NotificationCategory.TRADES, evaluator_notification)

        self._build_text()

    @abstractmethod
    def _build_text(self):
        raise NotImplementedError("_build_text is not implemented")


class OrderCreationNotification(_OrderNotification):
    def __init__(self, evaluator_notification: Notification, order: Order):
        self.order = order
        super().__init__("Order creation", evaluator_notification)

    def _build_text(self):
        self.text = self.title
        self.markdown_text = self.title
        exchange_name = get_order_exchange_name(self.order).capitalize()
        self.text += f"\n- {PrettyPrinter.open_order_pretty_printer(exchange_name, self.order, markdown=False)}"
        self.markdown_text += f"\n- {PrettyPrinter.open_order_pretty_printer(exchange_name, self.order, markdown=True)}"


class OrderEndNotification(_OrderNotification):
    def __init__(self, evaluator_notification: Notification, order_filled: Order, orders_canceled: list,
                 trade_profitability: float, portfolio_profitability: float, portfolio_diff: float,
                 add_profitability: bool):
        self.order_filled = order_filled
        self.orders_canceled = orders_canceled
        self.trade_profitability = trade_profitability
        self.portfolio_profitability = portfolio_profitability
        self.portfolio_diff = portfolio_diff
        self.add_profitability = add_profitability
        super().__init__("Order status updated", evaluator_notification)

    def _build_text(self):
        self.text = ""
        self.markdown_text = ""
        if self.order_filled is not None:
            exchange_name = get_order_exchange_name(self.order_filled).capitalize()
            trader_type = SIMULATOR_TRADER_STR if is_trader_simulated(self.order_filled.exchange_manager) \
                else REAL_TRADER_STR
            self.text += f"\n{trader_type}Order(s) filled : " \
                         f"\n- {PrettyPrinter.open_order_pretty_printer(exchange_name, self.order_filled)}"
            self.markdown_text += \
                f"\n*{trader_type}*Order(s) filled : " \
                f"\n- {PrettyPrinter.open_order_pretty_printer(exchange_name, self.order_filled, markdown=True)}"

        if self.orders_canceled is not None and self.orders_canceled:
            exchange_name = get_order_exchange_name(self.orders_canceled[0]).capitalize()
            trader_type = SIMULATOR_TRADER_STR if is_trader_simulated(self.orders_canceled[0].exchange_manager) \
                else REAL_TRADER_STR
            self.text += f"\n{trader_type}Order(s) canceled :"
            self.markdown_text += f"\n*{trader_type}*Order(s) canceled :"
            for order in self.orders_canceled:
                self.text += f"\n- {PrettyPrinter.open_order_pretty_printer(exchange_name, order)}"
                self.markdown_text += \
                    f"\n- {PrettyPrinter.open_order_pretty_printer(exchange_name, order, markdown=True)}"

        if self.trade_profitability is not None and self.add_profitability:
            self.text += f"\n\nTrade profitability : {'+' if self.trade_profitability >= 0 else ''}" \
                         f"{round(self.trade_profitability * 100, 4)}%"
            self.markdown_text += f"\nTrade profitability : *{'+' if self.trade_profitability >= 0 else ''}" \
                                  f"{round(self.trade_profitability * 100, 4)}%*"

        if self.portfolio_profitability is not None and self.add_profitability:
            self.text += f"\nPortfolio profitability : {round(self.portfolio_profitability, 4)}% " \
                       f"{'+' if self.portfolio_diff >= 0 else ''}{round(self.portfolio_diff, 4)}%"
            self.markdown_text += f"\nPortfolio profitability : `{round(self.portfolio_profitability, 4)}% " \
                                  f"{'+' if self.portfolio_diff >= 0 else ''}{round(self.portfolio_diff, 4)}%`"
