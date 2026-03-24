#builder stage
FROM python:3.10 AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./app/requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential

#production-stage
FROM dhi.io/python:3.10

COPY --from=builder /usr/local/lib/python3.10/site-packages/ /opt/python/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local /usr/local
COPY --from=builder /usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu

COPY --chown=nonroot:nonroot ./backend /app

WORKDIR /app
ENTRYPOINT [ "gunicorn", "--bind", "0.0.0.0:8000", "divineapp.wsgi:application" ]
