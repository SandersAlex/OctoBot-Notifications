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

from octobot_channels.util import create_channel_instance

from octobot_channels.channels.channel import set_chan, get_chan, Channel
from octobot_notifications.channel.notifications import NotificationChannel, NotificationChannelProducer
from octobot_commons.constants import CONFIG_CATEGORY_NOTIFICATION, CONFIG_NOTIFICATION_TYPE
from octobot_notifications.notification.notification import Notification
from octobot_services.abstract_service_user import AbstractServiceUser


class AbstractNotifier(AbstractServiceUser):
    # Override this key with the identifier of the notifier (used to know if enabled)
    NOTIFICATION_TYPE_KEY = None
    # The service required to run this notifier
    REQUIRED_SERVICE = None

    def __init__(self, config):
        AbstractServiceUser.__init__(self, config)
        self.logger = self.get_logger()
        self.enabled = self.is_enabled(config)
        self.service = None

    # Override this method to use a notification when received
    @abstractmethod
    async def _handle_notification(self, notification: Notification):
        raise NotImplementedError(f"_handle_notification is not implemented")

    async def _notification_callback(self, notification: Notification = None):
        try:
            if self._is_notification_category_enabled(notification):
                await self._handle_notification(notification)
        except Exception as e:
            self.logger.error(f"Exception when handling notification: {e}")
            self.logger.exception(e)

    async def initialize(self, backtesting_enabled) -> bool:
        if await AbstractServiceUser.initialize(self, backtesting_enabled):
            self.service = self.REQUIRED_SERVICE.instance()
            channel = await self._create_notification_channel_if_not_existing()
            await channel.new_consumer(self._notification_callback)
            self.logger.debug("Registered as notification consumer")
            return True
        return False

    @classmethod
    def is_enabled(cls, config):
        if cls.NOTIFICATION_TYPE_KEY is None:
            cls.get_logger().warning(f"{cls.get_name()}.NOTIFICATION_TYPE_KEY is not set, it has to be set to identify "
                                     f"and activate this notifier.")
        return cls.NOTIFICATION_TYPE_KEY in AbstractNotifier._get_activated_notification_keys(config)

    @staticmethod
    def _get_activated_notification_keys(config):
        if CONFIG_CATEGORY_NOTIFICATION in config and CONFIG_NOTIFICATION_TYPE in config[CONFIG_CATEGORY_NOTIFICATION]:
            return config[CONFIG_CATEGORY_NOTIFICATION][CONFIG_NOTIFICATION_TYPE]
        return []

    @staticmethod
    async def _create_notification_channel_if_not_existing() -> Channel:
        try:
            return get_chan(NotificationChannel.get_name())
        except KeyError:
            channel = await create_channel_instance(NotificationChannel, set_chan)
            await channel.register_producer(NotificationChannelProducer.instance(channel))
            return channel

    def _is_notification_category_enabled(self, notification):
        return CONFIG_CATEGORY_NOTIFICATION in self.config and \
               notification.category.value in self.config[CONFIG_CATEGORY_NOTIFICATION]
