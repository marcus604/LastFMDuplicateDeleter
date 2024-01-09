FROM python:3.12-slim

ENV CHROME_VERSION=120.0.6099.199
#Install Google Chrome
RUN apt update && apt -y install libglib2.0-dev libxi6 libnss3-dev wget gnupg

RUN mkdir -m 0755 -p /etc/apt/keyrings/
RUN wget -O- https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /etc/apt/keyrings/google-chrome.gpg > /dev/null
RUN chmod 644 /etc/apt/keyrings/google-chrome.gpg

RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

RUN chmod 644 /etc/apt/sources.list.d/google-chrome.list
RUN apt update && apt -y install google-chrome-stable


#Install Chrome Driver
RUN CHROME_VERSION=$(google-chrome --version | sed -E "s/.* ([0-9.]+).*/\1/g")

RUN wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
