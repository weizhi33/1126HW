# 1. 使用 Leafmap 作者做好的官方映像檔 (裡面已經有最新版 leafmap 和地圖工具)
FROM ghcr.io/opengeos/leafmap:latest

# 2. 設定工作目錄
WORKDIR /code

# 3. 雖然裡面有 leafmap，但我們還需要裝 solara 和 duckdb
# (使用 root 權限安裝，避免權限錯誤)
USER root
RUN pip install solara duckdb pandas

# 4. 複製程式碼
COPY . .

# 5. 啟動 Solara
CMD ["solara", "run", "app.py", "--host=0.0.0.0", "--port=7860"]