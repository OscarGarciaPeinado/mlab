# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Bluekiri V5 BigData Team <bigdata@bluekiri.com>.
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception, the copyright holders give permission to link the
# code of portions of this program with the OpenSSL library under certain
# conditions as described in each individual source file and distribute
# linked combinations including the program with the OpenSSL library. You
# must comply with the GNU Affero General Public License in all respects for
# all of the code used other than as permitted herein. If you modify file(s)
# with this exception, you may extend this exception to your version of the
# file(s), but you are not obligated to do so. If you do not wish to do so,
# delete this exception statement from your version. If you delete this
# exception statement from all source files in the program, then also delete
# it in the license file.


import logging.config
import os

import yaml
from flask import Flask
from flask_security import MongoEngineUserDatastore
from flask_security import Security
from flask_security import utils

from dashboard.application.conf.config import SERVICE_PORT, CREATE_ADMIN_USER
from dashboard.application.interactor.logs.get_workers_load_model_status_imp \
    import GetWorkersLoadModelStatusImp
from dashboard.application.interactor.workers_obersable_imp import \
    WorkersListenerEventImp
from dashboard.application.api.api_dashboard import ApiDashboard
from dashboard.application.dashboard.dashboard_initialize import Dashboard
from dashboard.application.dashboard.views.forms.login_form import \
    CustomLoginForm
from dashboard.application.datasource.zk_datasource_imp import ZKDatasourceImp
from dashboard.application.interactor.logs.get_time_line_events_imp import \
    GetTimeLineEventsImp
from dashboard.application.interactor.logs.save_model_log_event_imp import \
    SaveModelModelLogEventImp
from dashboard.application.interactor.messages.send_message_imp import \
    SendMessageImp
from dashboard.application.interactor.mlmodel.create_ml_model_imp import \
    CreateMlModelImp
from dashboard.application.interactor.orchestation.orchestation_interactor_imp \
    import OrchestationInteractorImp
from dashboard.application.interactor.users.current_user_imp import \
    CurrentUserImp
from dashboard.application.interactor.users.token_verification import \
    TokenVerificationImp
from dashboard.application.interactor.users.user_messaging_imp import \
    UserMessagingImp
from dashboard.application.interactor.users.users_privileges_imp import \
    UsersPrivilegesImp
from dashboard.application.repositories.logs_repository_imp import \
    LogsRepositoryImp
from dashboard.application.repositories.message_repository_imp import \
    MessageRepositoryImp
from dashboard.application.repositories.model_repository_imp import \
    ModelRepositoryImp
from dashboard.application.repositories.mongo_repository import \
    get_mongo_connection
from dashboard.application.repositories.worker_repository_imp import \
    WorkerRepositoryImp
from dashboard.domain.entities.auth.login_model import User, Role
from dashboard.application.util import CONF_APPLICATION_PATH, \
    CURRENT_APPLICATION_PATH, STATIC_APPLICATION_PATH


def setup_logging(default_path=CONF_APPLICATION_PATH,
                  default_level=logging.INFO,
                  env_key='API-SERVER'):
    path = default_path + '/logging.yaml'
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    return logging.getLogger(__name__)


app = Flask(__name__)
app.config.from_pyfile(os.path.join(CONF_APPLICATION_PATH, 'config.py'))
app.template_folder = CURRENT_APPLICATION_PATH + "/dashboard/templates"
app.static_folder = STATIC_APPLICATION_PATH

# MongoDB settings
db = get_mongo_connection()
db.init_app(app)

logging.info("Initialize dashboard security")
user_datastore = MongoEngineUserDatastore(db, User, Role)
Security(app, user_datastore, login_form=CustomLoginForm)

# Dependencies
logging.info("Initialize dashboard dependencies")
zk_data_source = ZKDatasourceImp()

message_repository = MessageRepositoryImp()
logs_repository = LogsRepositoryImp()
model_repository = ModelRepositoryImp()
worker_repository = WorkerRepositoryImp(zk_data_source, model_repository)
worker_listener_event = WorkersListenerEventImp(worker_repository)
get_workers_load_model = GetWorkersLoadModelStatusImp(worker_repository)

token_verification = TokenVerificationImp()
orchestation_interactor = OrchestationInteractorImp(
    worker_repository=worker_repository)
users_privileges = UsersPrivilegesImp()
current_user = CurrentUserImp()
user_messaging = UserMessagingImp(current_user=current_user,
                                  message_repository=message_repository)
get_time_line_events = GetTimeLineEventsImp(logs_repository)
save_model_log_event = SaveModelModelLogEventImp(current_user=current_user,
                                                 log_repository=logs_repository)
send_message = SendMessageImp(message_repository)
create_ml_model = CreateMlModelImp(send_message=send_message,
                                   save_model_log_event=save_model_log_event,
                                   model_repository=model_repository)

# Blueprints
dashboard = Dashboard(app=app, worker_repository=worker_repository,
                      model_repository=model_repository,
                      save_model_log_event=save_model_log_event,
                      message_repository=message_repository,
                      logs_repository=logs_repository,
                      current_user=current_user,
                      orchestation_interactor=orchestation_interactor,
                      get_time_line_events=get_time_line_events,
                      user_messaging=user_messaging,
                      users_privileges=users_privileges,
                      get_workers_load_model_status=get_workers_load_model)

app.register_blueprint(dashboard.get_blueprint())

api_dashboard = ApiDashboard(create_ml_model=create_ml_model,
                             token_verification=token_verification,
                             worker_repository=worker_repository)

app.register_blueprint(api_dashboard.get_blueprint())

# This snippet of code is user with password create example
if CREATE_ADMIN_USER and not len(user_datastore.user_model.objects()):
    logging.info("Creating default admin user.")
    with app.app_context():
        admin_role = user_datastore.find_or_create_role('admin')
        user_datastore.create_user(email='admin',
                                   password=utils.hash_password('admin'),
                                   name='admin', username='admin',
                                   roles=[admin_role])

if __name__ == '__main__':
    # Start app
    app.run(debug=True, host='0.0.0.0', port=int(SERVICE_PORT))
