FROM python:3.10-alpine

RUN apk add --no-cache uwsgi-python3 stress-ng && \
    mkdir /opt/stress-api

WORKDIR /opt/stress-api
ENV SNG_TOKEN="default"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    chown uwsgi:uwsgi -R /opt/stress-api

COPY --chown=uwsgi:uwsgi app.py openapi.yaml uwsgi.yaml ./

USER uwsgi

ENTRYPOINT ["uwsgi"]
CMD ["--yaml", "uwsgi.yaml"]
