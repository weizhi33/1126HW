FROM python:3.9

WORKDIR /code

# ⚠️ 注意這裡：我們直接在這裡指定套件，不讀取 requirements.txt 了
# 這樣可以保證一定會安裝到 leafmap 的新版本
RUN pip install --no-cache-dir \
    "leafmap>=0.31.0" \
    solara \
    duckdb \
    pandas \
    geopandas \
    pyarrow \
    fiona \
    ipyleaflet

# 複製程式碼
COPY . .

# 啟動指令
CMD ["solara", "run", "app.py", "--host=0.0.0.0", "--port=7860"]