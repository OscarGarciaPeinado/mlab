FROM python:3.5-jessie
ARG DATABASE_NAME
ARG MLAB_MONGO_URI
ARG MLAB_ZOOKEEPER_URI
ARG WORKER_INSTANCES
ARG LDAP_URI
ARG PORT
ARG WORKER_PORT

ENV application_path /opt/dashboard
WORKDIR ${application_path}

COPY . .

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt install -y nodejs
RUN cd src/dashboard && \
    npm install
RUN cd src/dashboard && \
    ./node_modules/bower/bin/bower install --allow-root && \
    ./node_modules/gulp/bin/gulp.js
RUN python setup.py install --force
EXPOSE ${PORT}
ENTRYPOINT gunicorn -t 300 -w ${WORKER_INSTANCES} -b 0.0.0.0:${PORT} dashboard.app:app
