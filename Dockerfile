FROM python:3.9-slim-buster

WORKDIR /starwars

COPY . /starwars

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
RUN chmod +x autostart.sh
CMD ["/starwars/autostart.sh"]