FROM python:alpine

COPY dfimage.py /app/dfimage.py

COPY dfimage.sh /app/dfimage.sh

COPY pyproject.toml /app/pyproject.toml

RUN apk add --no-cache --update bash jq

RUN python3 -m venv /app

RUN source /app/bin/activate

RUN python3 -m venv /app/dfimage

RUN source /app/dfimage/bin/activate

RUN for i in $(pip list --outdated --format=json |jq -r '.[].name' ) ; do pip install -U $i; done

RUN pip install -e /app

RUN yes | pip uninstall pip

RUN rm -rf ~/.cache/* /usr/local/share/man /tmp/* /app/pyproject.toml

ENTRYPOINT ["/app/dfimage.sh"]

CMD ["/bin/bash"]
