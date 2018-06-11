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

from worker.application.controllers.base_model_controller import BaseModelController


class DummyModelController(BaseModelController):
    def on_get(self, req, resp):
        model_wrapper = self.model_repository.get_current_model()
        if model_wrapper is not None:
            model = model_wrapper.get_model_instance()
        else:
            raise Exception("Model not found...")

        model_request = {}
        resp.media = {"model_response": model.run_model(model_request)}
