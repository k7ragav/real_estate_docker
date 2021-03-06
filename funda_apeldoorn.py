import mysql.connector
import ssl
from bs4 import BeautifulSoup
import time

ssl._create_default_https_context = ssl._create_unverified_context

import requests

from twilio.rest import Client
from dotenv import load_dotenv
import os

from send_telegram_message import send_message

HEADERS = {
        'Authority': 'www.funda.nl',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': '*/*',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4544.0 Safari/537.36 Edg/93.0.933.1',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.funda.nl',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.funda.nl/koop/apeldoorn',
        'Accept-Language': 'en-US,en;q=0.9',
        'dnt': '1',
        'sec-gpc': '1',
    }


def sql_connection():
    mydb = mysql.connector.connect(host="5.255.98.125 ",
                                   user = "keshava",
                                   password = 'Dhanam_7',
                                   database = 'real_estate_db'
                                   )

    mycursor = mydb.cursor(prepared=True)
    return mydb, mycursor

def check_last_known_number():
    mydb, mycursor = sql_connection()
    sql_query= "SELECT result_number from funda_apeldoorn where city = 'Apeldoorn'"
    mycursor.execute(sql_query)
    results = mycursor.fetchall()
    recent_result_number = [result[0] for result in results]
    return str(recent_result_number[0])

def update_table(result_number, city):
    mydb, mycursor = sql_connection()
    sql_query = "UPDATE funda_apeldoorn SET result_number = %s WHERE city = %s"
    val =  (result_number, city)

    mycursor.execute(sql_query, val)
    mydb.commit()


def get_funda_data(city):
    url = f"https://www.funda.nl/koop/{city}/300000-550000/100+woonopp/woonhuis/sorteer-datum-af/"

    html_content = requests.get(url, headers=
    HEADERS).content

    soup = BeautifulSoup(html_content, "html.parser")
    table_div = soup.find_all("div", attrs={"class": "search-result__header-title-col"})
    for i in table_div[0:1]:
        first_result_url = str(i.find('a')['href'])

    return first_result_url

def whatsapp_message(city):
    load_dotenv()
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    body_message = f" Hi. There might be new results in funda for {city}"

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=body_message,
        to='whatsapp:+31626654343'
    )
    time.sleep(10)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=body_message,
        to='whatsapp:+31626654340'
    )
    time.sleep(10)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=body_message,
        to='whatsapp:+31618420974'
    )

def main():
    # urls = pararius_get_urls_list()
    city = 'apeldoorn'
    result_number_last_known = check_last_known_number()
    result_number_funda = get_funda_data(city=city)
    if result_number_funda != result_number_last_known:
        update_table(result_number_funda, city=city)
        whatsapp_message(city=city)
        send_message(message = "There might be some new addresses")


if __name__ == "__main__":
    main()