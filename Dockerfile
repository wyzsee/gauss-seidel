# Gunakan base image Python 3.11
FROM python:3.11-slim

# Set direktori kerja di dalam container
WORKDIR /code

# Salin file requirements dan install dependensi
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Salin semua file proyek lainnya ke dalam container
COPY ./ /code/

# Beritahu container port mana yang akan diekspos
EXPOSE 7860

# Perintah untuk menjalankan aplikasi saat container start
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:7860", "app:app"]