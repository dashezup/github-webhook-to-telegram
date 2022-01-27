FROM python:3.9.4

ARG PYUSERGROUP=1000

ENV CONFIG_JSON='{ "bot_token": "", "port": 12345, "gh_webhooks": {} }'


RUN mkdir -p /var/project/app/
COPY .  /var/project/app/
WORKDIR /var/project/app/

RUN groupadd --force -g $PYUSERGROUP pyuser
RUN useradd -ms /bin/bash --no-user-group -g $PYUSERGROUP -u $PYUSERGROUP pyuser

RUN pip install -U -r requirements.txt
RUN chown -R pyuser:pyuser .
RUN chmod 755 /var/project/app/docker/docker-entrypoint.sh

USER pyuser

CMD ["bash", "/var/project/app/docker/docker-entrypoint.sh"]