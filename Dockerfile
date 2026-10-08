# 角色 D 维护。第 1 周目标：镜像内 python 可用，并能跑通冒烟脚本。
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY tests ./tests
COPY docs ./docs
COPY README.md .

# 行情与图片走卷，不打进镜像
RUN mkdir -p /app/data/processed /app/output

CMD ["python", "-m", "src.main"]
