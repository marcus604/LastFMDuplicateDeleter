FROM --platform=linux/amd64 python:3.12-slim

RUN apt update && apt -y install libglib2.0-dev libxi6 libnss3-dev wget gnupg zip curl

RUN mkdir -m 0755 -p /etc/apt/keyrings/
RUN wget -O- https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /etc/apt/keyrings/google-chrome.gpg > /dev/null
RUN chmod 644 /etc/apt/keyrings/google-chrome.gpg

RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

RUN chmod 644 /etc/apt/sources.list.d/google-chrome.list
RUN apt update && apt -y install google-chrome-stable


RUN CHROMEDRIVER_VERSION=$(curl https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE); \
    wget -N https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip -P ~/ && \
    unzip ~/chromedriver-linux64.zip -d ~/ && \
    rm ~/chromedriver-linux64.zip && \
    mv -f ~/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    rm -rf ~/chromedriver-linux64

#Required for Selenium
ENV DISPLAY=:99

RUN mkdir -p /app/csv

COPY ./app /app
WORKDIR /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "./main.py"]
