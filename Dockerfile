FROM alpine:latest

RUN apk update && apk upgrade
RUN apk add --no-cache python3 git curl zsh py3-pip gcc python3-dev musl-dev linux-headers

SHELL ["/bin/zsh", "-c"]
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

WORKDIR /home/athena
COPY . .

RUN git checkout master
RUN git fetch
RUN git reset --hard origin/master
RUN git pull

RUN python3 -m venv .venv
RUN . .venv/bin/activate
RUN .venv/bin/pip install --no-cache-dir --upgrade -r requirements.txt

# RUN chmod +x setup.sh
# RUN ./setup.sh

CMD [".venv/bin/python", "athena.py"]