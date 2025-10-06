FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget curl gnupg tzdata unzip python3.10 python3-pip fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 xdg-utils --no-install-recommends

# 安裝 Google Chrome (非 snap)
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# 安裝相容的 chromedriver（對應 chrome 版本）
RUN CHROME_VERSION=$(google-chrome --version | grep -oP "\d+\.\d+\.\d+\.\d+") && \
    mkdir -p /usr/local/bin && \
    mkdir -p /tmp && \
    mkdir -p /usr/local/bin && \
    wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip && \
    ls && \
    mv ./chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

ENV PATH="/usr/local/bin:/usr/local/bin/chromedriver:$PATH"

# Set the timezone to CST (Taipei)
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 設定工作目錄與安裝 Python 套件
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]

# 如果需要初始化資料庫，可以取消下面的註解
RUN flask init-db