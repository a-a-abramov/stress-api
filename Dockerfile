FROM python:3.10-alpine

RUN apk add --no-cache uwsgi-python3 uwsgi-http stress-ng && \
    mkdir /opt/stress-api

WORKDIR /opt/stress-api
ENV SNG_TOKEN="default"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    chown uwsgi:uwsgi -R /opt/stress-api

COPY --chown=uwsgi:uwsgi app.py openapi.yaml ./

USER uwsgi

ENTRYPOINT ["uwsgi"]
CMD \
    ["--plugin", "python,http", \
    "--http", ":80", \
    "--log-master", \
    "--uid", "uwsgi", \
    "--gid", "uwsgi", \
    "--cap", "setgid,setuid", \
    "--env", "PYTHONPATH=/usr/local/lib/python3.10/site-packages:/usr/lib/python3.10/site-packages", \
    "--wsgi-file", "app.py", \
    "--callable", "application", \
    "--log-format", "[%(ctime)] %(addr) %(method) %(uri) %(msecs) msecs %(status)", \
    "--workers", "8"\
    ]
