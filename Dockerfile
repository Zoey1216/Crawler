# 使用輕量版的 Python 3.10 作為基礎基底
FROM python:3.10-slim

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 更新系統並安裝 wget 工具
# 接著直接下載 Chrome 的 .deb 安裝檔並進行安裝，最後清理暫存檔縮小映像檔體積
RUN apt-get update && apt-get install -y wget \
    && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 在容器內建立一個名為 /app 的工作目錄
WORKDIR /app

# 先複製套件清單，並安裝所有 Python 依賴套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 將你本機資料夾的所有檔案複製進容器的 /app 目錄下
COPY . .

# 當容器啟動時，預設執行的指令
CMD ["python", "crawler.py"]