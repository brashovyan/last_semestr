from celery import shared_task
from .models import *
from datetime import datetime, timedelta
from django.conf import settings
from collections import Counter
import os
import requests
from bs4 import BeautifulSoup


@shared_task
def report_task():
    # от текущей даты отнимаю время, через которое периодически выполняется задача
    date_time = datetime.now() - timedelta(seconds=settings.CELERY_BEAT_TIMER)
    logs = CustomLog.objects.filter(date__gte = date_time)
    methods = []
    for log in logs:
        methods.append(log.method)
    rating = Counter(methods)
    rating_str = ""
    for key in rating.keys():
        rating_str += f'Кол-во вызовов: {rating[key]}, метод: {key}\n'
    if rating_str != "":
        if not os.path.isdir("reports"):
            os.mkdir("reports")
        my_file = open(f"reports/report-{datetime.now()}.txt", "w+")
        my_file.write(rating_str)
        my_file.close()
        print("Отчёт сформирован")
    print("Фоновая задача отчёта завершена")


@shared_task
def parsing_task():
    film = ""
    try:
        page = requests.get(f"https://randomfilm.ru")
        soup = BeautifulSoup(page.content, "html.parser")
        title = soup.find_all("h2")
        inf = soup.find_all("tr")
        st = str(inf).split('\n')
        year = st[0]
        year = year[173:len(year)-5]
        country = st[1]
        country = country[18:len(country)-5]
        genre = st[2]
        genre = genre[16:len(genre)-5]
        film = f"{str(title)[5:len(title)-7]}\n\nГод: {year}\nСтрана: {country}\nЖанр: {genre}"
        if film != "" or film is not None:
            if not os.path.isdir("parsings"):
                os.mkdir("parsings")
            my_file = open(f"parsings/parsing-{datetime.now()}.txt", "w+")
            my_file.write(film)
            my_file.close()
            print("Парсинг сформирован")
        print("Фоновая задача парсинга завершена")
    except Exception as error:
        print(error)



