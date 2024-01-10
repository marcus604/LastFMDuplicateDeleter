FROM python:3.12-slim

#Install Google Chrome
RUN apt update && apt -y install libglib2.0-dev libxi6 libnss3-dev wget gnupg zip

RUN mkdir -m 0755 -p /etc/apt/keyrings/
RUN wget -O- https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /etc/apt/keyrings/google-chrome.gpg > /dev/null
RUN chmod 644 /etc/apt/keyrings/google-chrome.gpg

RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

RUN chmod 644 /etc/apt/sources.list.d/google-chrome.list
RUN apt update && apt -y install google-chrome-stable


#Install Chrome Driver
ENV CHROME_VERSION=120.0.6099.109

RUN wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip && rm -dfr chromedriver_linux64.zip \
    && mv /chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver


#Install Selenium
ENV DISPLAY=:99

COPY ./app /app
WORKDIR /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python", "./main.py"]







