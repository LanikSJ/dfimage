FROM alpine:3.21.0

COPY entrypoint.py /app/entrypoint.py

COPY entrypoint.sh /app/entrypoint.sh

COPY requirements.txt /app/requirements.txt

RUN apk add --no-cache --update bash jq python3

RUN python3 -m venv /app

RUN source /app/bin/activate && python3 -m ensurepip --default-pip \
    && for i in $(pip list --outdated --format=json |jq -r '.[].name' ) \
    ; do pip install -U $i; done \
    && pip install -r /app/requirements.txt \
    && yes | pip uninstall pip

RUN rm -rf ~/.cache/* /usr/local/share/man /tmp/* /app/requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["/bin/bash"]
