import telegram
from dotenv import load_dotenv
import os

def send_message(message:str):
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id="-648193235", text=message)

