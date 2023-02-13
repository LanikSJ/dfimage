FROM alpine:3.17.2

COPY entrypoint.py /root/entrypoint.py

COPY requirements.txt requirements.txt

RUN apk --no-cache update && apk add --no-cache python3 wget \
    && wget -q --no-check-certificate https://bootstrap.pypa.io/get-pip.py \
    && apk del wget && python3 get-pip.py && rm -f get-pip.py \
    && pip install -U pip && pip install -r requirements.txt \
    && rm -f requirements.txt && yes | pip uninstall pip

ENTRYPOINT ["/root/entrypoint.py"]

CMD ["/bin/sh"]
