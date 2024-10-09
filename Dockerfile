FROM alpine:latest

RUN apk update && apk upgrade
RUN apk add --no-cache python3 python3-dev git curl zsh py3-pip gcc musl-dev linux-headers ffmpeg
# need gcc, python3-dev, musl-dev, linux-headers for psutil

SHELL ["/bin/zsh", "-c"]
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

WORKDIR /root
COPY . .

RUN git checkout prod
RUN git fetch
RUN git reset --hard origin/prod
RUN git pull

RUN touch cookies.txt && chmod 600 /root/cookies.txt

RUN pip3 install --break-system-packages --no-cache-dir --upgrade -r requirements.txt

CMD ["python3", "athena.py"]