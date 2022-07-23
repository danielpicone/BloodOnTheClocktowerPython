#syntax=docker/dockerfile:1
FROM python:3.9.2
COPY Requirements.txt ./
RUN pip install --no-cache-dir -r Requirements.txt
COPY . .
CMD ["python", "bot.py"]
