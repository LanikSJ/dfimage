FROM alpine:3.21.2

COPY dfimage.py /app/dfimage.py

COPY dfimage.sh /app/dfimage.sh

COPY pyproject.toml /app/pyproject.toml

RUN apk add --no-cache --update bash jq python3

RUN python3 -m venv /app

RUN source /app/bin/activate && python3 -m ensurepip --default-pip \
    && for i in $(pip list --outdated --format=json |jq -r '.[].name' ) \
    ; do pip install -U $i; done \
    && pip install -e /app \
    && yes | pip uninstall pip

RUN rm -rf ~/.cache/* /usr/local/share/man /tmp/* /app/pyproject.toml

ENTRYPOINT ["/app/dfimage.sh"]

CMD ["/bin/bash"]
