# 1. 使用 Mamba 處理最難搞的底層環境
FROM mambaorg/micromamba:1.5.8

# 設定工作目錄與權限
COPY --chown=$MAMBA_USER:$MAMBA_USER . /tmp/app
WORKDIR /tmp/app

# 2. 用 Conda 安裝 Python 3.10 和 GDAL (地圖底層)
# 我們只讓 Conda 負責這些「重兵器」
RUN micromamba install -y -n base -c conda-forge \
    python=3.10 \
    gdal \
    geopandas \
    pyarrow \
    && micromamba clean --all --yes

# 3. 啟動環境變數 (這是讓下面的 pip 知道要裝在哪裡)
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# 4. 🔥 關鍵修正：用 pip 安裝 Leafmap 和 Solara 🔥
# pip 會直接從 PyPI 下載官方原始碼，絕對會有 solara 模組！
RUN pip install --no-cache-dir \
    "leafmap>=0.31.0" \
    solara \
    duckdb \
    fiona \
    matplotlib \
    mapclassify

# 5. 啟動
CMD ["solara", "run", "app.py", "--host=0.0.0.0", "--port=7860"]