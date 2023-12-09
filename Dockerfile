FROM alpine:3.19.0

COPY entrypoint.py /app/entrypoint.py

COPY entrypoint.sh /app/entrypoint.sh

COPY requirements.txt /app/requirements.txt

RUN apk add --no-cache --update \
        python3 \
        py3-pip \
        bash

RUN python3 -m venv /app

RUN source /app/bin/activate && pip install -U pip \
    && pip install -r /app/requirements.txt \
    && yes | pip uninstall pip

RUN rm -rf ~/.cache/* /usr/local/share/man /tmp/* /app/requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["/bin/bash"]
