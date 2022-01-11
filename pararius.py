import json
import os
import re
from typing import Any, Dict, List
import time
import mysql.connector
import ssl
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context
import random
import requests


from twilio.rest import Client

from dotenv import load_dotenv
from pathlib import Path
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


# you can also import SoftwareEngine, HardwareType, SoftwareType, Popularity from random_user_agent.params
# you can also set number of user agents required by providing `limit` as parameter

software_names = [SoftwareName.EDGE.value,]
operating_systems = [OperatingSystem.MAC.value,]

user_agent_rotator = UserAgent(limit=10000)
# Get list of user agents.
user_agents = user_agent_rotator.get_user_agents()
user_agent_list = [user['user_agent'] for user in user_agents]

rex_url = re.compile(r'href="/(?:huis|appartement)-te-(?:koop|huur)/[^"]+')


rex_json = re.compile(
    re.escape('<script type="application/ld+json">') + '(.+)' + re.escape('</script>'),
    re.DOTALL,
)

ROOT_URL = 'https://www.pararius.nl'



def sql_connection():
    mydb = mysql.connector.connect(host="5.255.98.125 ",
                                   user = "keshava",
                                   password = 'Dhanam_7',
                                   database = 'real_estate_db'
                                   )

    mycursor = mydb.cursor(prepared=True)
    return mydb, mycursor
def insert_result_in_table(result):
    mydb, mycursor = sql_connection()
    sql_query= "INSERT INTO pararius (`url`, `type`, street,city, postalCode, rooms, surfaceArea,offeredSince, price) VALUES (%s, %s, %s, %s, %s ,%s, %s,%s, %s)"

    mycursor.executemany(sql_query, result)
    mydb.commit()

def select_table():
    mydb, mycursor = sql_connection()
    sql_query = "select url from real_estate_db.pararius"
    mycursor.execute(sql_query)
    result = mycursor.fetchall()
    listing_list = [listing[0] for listing in result]
    return listing_list


def get_urls(url: str) -> List[str]:
    ua_final = random.choice(user_agent_list)
    HEADERS = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        # noqa
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        'cache-control': 'max-age=0',
        'referer': ROOT_URL,
        'user-agent': ua_final,  # noqa
    }
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return [f'{ROOT_URL}{u[6:]}' for u in rex_url.findall(r.text)]


def get_info(url: str) -> Dict[str, Any]:
    ua_final_info = random.choice(user_agent_list)
    # print(ua_final_info)
    HEADERS_NEW = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
        'cache-control': 'max-age=0',
        'referer': ROOT_URL,
        'user-agent': ua_final_info,  # noqa
    }
    if not url.startswith(ROOT_URL):
        raise ValueError('invalid URL')
    r = requests.get(url, headers=HEADERS_NEW)
    r.raise_for_status()
    # print(r.text)
    match = rex_json.search(r.text)
    if not match:
        print(url)
        # print(r.text)
        raise ValueError('cannot find JSON data on page')

    raw = match.group(1)
    return json.loads(raw.splitlines()[1].strip())

def pararius_get_urls_list():
    urls = []
    while len(urls) == 0:
        search_url = 'https://www.pararius.nl/huurwoningen/apeldoorn'
        urls_raw = get_urls(search_url)
        urls = list(set(urls_raw))
        time.sleep(3)
        print(len(urls))
    return urls

def pararius_get_data(urls):
    result_list = []
    for url in tqdm(urls):
        try:
            info = get_info(url)
            if int(info['floorSize']['value']) >= 0:
                result_dic = {
                    "url" : info['@id'],
                    "type" : info["@type"][0],
                    "street": info['address']['streetAddress'],
                    "city": info['address']['addressLocality'],
                    "postalCode": info['address']['postalCode'],
                    "rooms":info['numberOfRooms'][0]['value'],
                    "surfaceArea": info['floorSize']['value'],
                    'offeredSince': info['offers']['validFrom'],
                    'price': info['offers']['price']
                }
                result = (result_dic["url"], result_dic['type'], result_dic['street'], result_dic['city'], result_dic['postalCode'],
                          result_dic['rooms'], result_dic['surfaceArea'],result_dic['offeredSince'],result_dic['price'])
                result_list.append(result)
        except Exception as e:
            print(e)
            continue
    return result_list

def whatsapp_message(url_list):

    # dotenv_path = Path('./twilio.env')
    # print(dotenv_path)
    load_dotenv()

    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    print(account_sid)
    client = Client(account_sid, auth_token)

    body_message = """ Hi. You can click on {0} """.format("\n".join(url_list))

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=body_message,
        to='whatsapp:+31626654343'
    )
    # message = client.messages.create(
    #     from_='whatsapp:+14155238886',
    #     body=body_message,
    #     to='whatsapp:+31644273034'
    # )

def main():
    # urls = pararius_get_urls_list()
    urls_sql = select_table()
    urls_pararius = pararius_get_urls_list()
    urls_to_scrape = [url for url in urls_pararius if url not in urls_sql]
    results = pararius_get_data(urls_to_scrape)
    # urls_final = [result[0] for result in results if result[0] not in urls_sql]
    insert_result_in_table(results)
    whatsapp_url = [result[0] for result in results if int(result[6]) >= 75]
    if whatsapp_url != []:
        whatsapp_message(whatsapp_url)

if __name__ == "__main__":
    main()