# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from typing import List

from dashboard.domain.entities.auth.login_model import User
from dashboard.domain.entities.message import Message


class MessageRepository:
    def get_all_messages(self) -> List[Message]:
        raise NotImplementedError()

    def get_messages_by_topics(self, topic: List[str]) -> List[Message]:
        raise NotImplementedError()

    def set_message_as_read(self, message_id: str, current_user: User):
        raise NotImplementedError()

    def get_direct_message(self, user: User) -> Message:
        raise NotImplementedError()

    def get_message_by_id(self, message_id: str) -> Message:
        raise NotImplementedError()

    def save_message(self, message: Message):
        raise NotImplementedError()
