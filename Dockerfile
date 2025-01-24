FROM python:alpine

COPY dfimage.py /app/dfimage.py

COPY pyproject.toml /app/pyproject.toml

RUN apk add --no-cache --update bash jq

RUN python3 -m venv /app

RUN source /app/bin/activate

RUN pip install -e /app

RUN yes | pip uninstall pip

RUN rm -rf ~/.cache/* /usr/local/share/man /tmp/* /app/pyproject.toml

ENTRYPOINT ["/app/dfimage.py"]

CMD ["/bin/bash"]
