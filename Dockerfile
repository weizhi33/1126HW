# 使用 Mamba (Conda 的快速版)，這是 GIS 界的標準神器
FROM mambaorg/micromamba:1.5.8

# 設定工作目錄，並處理權限 (避免 jovyan 權限問題)
COPY --chown=$MAMBA_USER:$MAMBA_USER . /tmp/app
WORKDIR /tmp/app

# ⚠️ 關鍵步驟：使用 conda-forge 安裝
# 這會直接下載已經編譯好的 GDAL、Leafmap 和 Solara，保證相容性
RUN micromamba install -y -n base -c conda-forge \
    python=3.10 \
    leafmap>=0.31.0 \
    solara \
    duckdb \
    pandas \
    geopandas \
    pyarrow \
    xyzservices \
    && micromamba clean --all --yes

# 啟動這個環境的魔法咒語
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# 啟動 Solara
CMD ["solara", "run", "app.py", "--host=0.0.0.0", "--port=7860"]