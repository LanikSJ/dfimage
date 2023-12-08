FROM alpine:3.19.0

COPY entrypoint.py /root/entrypoint.py

COPY requirements.txt requirements.txt

RUN apk --no-cache update && apk add --no-cache python3 pipx \
    && export PATH="$HOME/.local/bin:$PATH" && pipx install pip \
    && pip install -U pip && pip install -r requirements.txt \
    && rm -f requirements.txt && yes | pip uninstall pip

ENTRYPOINT ["python", "/root/entrypoint.py"]

CMD ["/bin/sh"]
