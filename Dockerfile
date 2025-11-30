FROM python:3.9

WORKDIR /code

# 複製 requirements.txt 並安裝
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 複製所有檔案 (包含 app.py)
COPY . .

# 啟動 app.py
CMD ["solara", "run", "app.py", "--host=0.0.0.0", "--port=7860"]