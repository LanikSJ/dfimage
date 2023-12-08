FROM alpine:3.19.0

COPY entrypoint.py /root/entrypoint.py

COPY entrypoint.sh /root/entrypoint.sh

COPY requirements.txt requirements.txt

RUN apk add --no-cache --update \
        python3 \
        pipx \
        bash                                              

RUN python3 -m pipx ensurepath

RUN PATH="$PATH:/root/.local/bin" && pipx install pip \
    && pipx upgrade-all && pipx install cookiecutter \
    && pipx runpip cookiecutter install -r requirements.txt

RUN rm -rf ~/.cache/* /usr/local/share/man /tmp/* requirements.txt 

ENTRYPOINT ["/root/entrypoint.sh"]

CMD ["/bin/bash"]
