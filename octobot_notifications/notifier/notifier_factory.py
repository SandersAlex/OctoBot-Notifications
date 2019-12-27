#  Drakkar-Software OctoBot-Interfaces
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

from octobot_commons.tentacles_management import get_all_classes_from_parent
from octobot_notifications.notifier.abstract_notifier import AbstractNotifier


class NotifierFactory:
    def __init__(self, config):
        self.config = config

    @staticmethod
    def get_available_notifiers():
        return get_all_classes_from_parent(AbstractNotifier)

    async def create_notifier(self, notifier_class):
        return notifier_class(self.config)
