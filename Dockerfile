# 1. ابدأ بصورة بايثون رسمية
FROM python:3.11-slim

# 2. قم بتعيين مجلد العمل داخل الحاوية
WORKDIR /app

# 3. انسخ ملف الاعتماديات أولاً للاستفادة من التخزين المؤقت لـ Docker
COPY requirements.txt .

# 4. قم بتثبيت الاعتماديات
RUN pip install --no-cache-dir -r requirements.txt

# 5. انسخ باقي كود التطبيق
COPY . .

# 6. قم بتعريض المنفذ الذي سيعمل عليه Gunicorn
EXPOSE 8000

# 7. الأمر لتشغيل التطبيق
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend_api:app", "--bind", "0.0.0.0:8000"]
