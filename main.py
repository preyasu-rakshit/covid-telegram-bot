import json
import logging
import requests
from telegram import Update, parsemode
from telegram.ext import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Covid data mangement functions
def update_database(context) -> None:
    global state_data, daily_data

    response = requests.get('https://api.covid19india.org/data.json')
    data = json.loads(response.text)
    state_data = data['statewise']

    response_daily = requests.get('https://api.covid19india.org/states_daily.json')
    data_list = json.loads(response_daily.text)
    daily_data = data_list['states_daily']

    print("Covid data updated successfully!")


def daily_deaths_from_code(code):
    for i in daily_data[::-1]:
        if i['status'] == "Deceased":
            deaths = i[code]
            #print(f"No. of deaths = {deaths}")
            return deaths


def daily_confirmed_from_code(code):
    for i in daily_data[::-1]:
        if i['status'] == "Confirmed":
            confirmed = i[code]
            #print(f"No. of confirmed cases = {confirmed}")
            return confirmed


def data_from_name(state) -> str:
    
    for i in state_data:
        if state.lower() == i['state'].lower() and state.lower() != 'total':
            code = i['statecode'].lower()
            daily_deaths = daily_deaths_from_code(code)
            daily_confirmed = daily_confirmed_from_code(code)
            
            t_1 = f"State: <b>{i['state']}</b>\n"
            t_2 = f"Number of confirmed cases: <b>{i['confirmed']}</b>\n"
            t_3 = f"Number of deaths: <b>{i['deaths']}</b>\n"
            t_4 = f"Number of confirmed cases in the last 24 hours: <b>{daily_confirmed if int(daily_confirmed) > 0 else 'Data not provided'}</b>\n"
            t_5 = f"Number of deaths in the last 24 hours: <b>{daily_deaths if int(daily_deaths) > 0 else 'Data not provided'}</b>\n"
            t_6 = f"Number of recovered patients: <b>{i['recovered']}</b>\n"

            text = t_1 + "\n" + t_2 + "\n" + t_3 + "\n" + t_4 + "\n" + t_5 + "\n" + t_6
            return text

        elif state.lower() == 'total' and state.lower() == i['state'].lower():
            code = i['statecode'].lower()
            daily_deaths = daily_deaths_from_code(code)
            daily_confirmed = daily_confirmed_from_code(code)

            t_1 = f"Number of confirmed cases in India: <b>{i['confirmed']}</b>\n"
            t_2 = f"Number of deaths in India: <b>{i['deaths']}</b>\n"
            t_3 = f"Number of confirmed cases in the last 24 hours: <b>{daily_confirmed}</b>\n"
            t_4 = f"Number of deaths in the last 24 hours: <b>{daily_deaths}</b>\n"
            t_5 = f"Number of recovered patients in India: <b>{i['recovered']}</b>\n"

            text = t_1 + "\n" + t_2 + "\n" + t_3 + "\n" + t_4 + "\n" + t_5
            return text

    raise AttributeError()


# User Database
def add_group(update: Update, context: CallbackContext):
    if context.bot.bot in update.message.new_chat_members:
        user_id = update.effective_chat.id
        help(update=update, context=context)


# bot commands
def start(update, context) -> None:
    user_id = update.effective_chat.id
    help(update= update, context= context)


def stateinfo(update, context):
    msg = update.message.text
    try:
        args = msg.split("/state ")[1]
        info = data_from_name(args)
        update.message.reply_text(info, parse_mode='HTML')
        return
    except:
        update.message.reply_text("Invalid usage of /state. Kindly see /help")
        return


def help(update, context):
    t_1 = "Hello there! I'm a bot that provides data about covid cases in different states of India. You can you the following commands:\n"
    t_2 = "/india - Get data about number active cases, recovered cases, deaths etc for India.\n"
    t_3 = "/state STATENAME - Get data about a specific state. Enter the name of the state instead of 'STATENAME'.\n"
    t_4 = "/info - More information about this bot and its creator\n"
    t_5 = "/help - See the list of available commands\n"

    msg = t_1 + "\n" + t_2 + "\n" + t_3 + "\n" + t_4

    update.message.reply_text(msg)


def india(update, context):
    info = data_from_name('total')
    update.message.reply_text(info, parse_mode='HTML')


def info(update, context):
    msg = '''This bot is written in Python using python-telegram-bot library. It uses data from https://api.covid19india.org/.
It is made by @preyasu_rakshit'''
    update.message.reply_text(msg)


# Main loop
def main() -> None:
    update_database(" ")
	
    updater = Updater("YOUR TELEGRAM API TOKEN")
    dispatcher = updater.dispatcher

    j = updater.job_queue

    add_group_handle = MessageHandler(
        Filters.status_update.new_chat_members, add_group)
    state_handle = CommandHandler('state', stateinfo)
    start_handle = CommandHandler('start', start)
    help_handle = CommandHandler('help', help)
    india_handle = CommandHandler('india', india)
    info_handle = CommandHandler('info', info)

    dispatcher.add_handler(add_group_handle)
    dispatcher.add_handler(state_handle)
    dispatcher.add_handler(start_handle)
    dispatcher.add_handler(help_handle)
    dispatcher.add_handler(india_handle)
    dispatcher.add_handler(info_handle)

    # Start the Bot
    updater.start_polling()
    # periodically update database
    j.run_repeating(update_database, interval=60*60, first=60)


    updater.idle()


if __name__ == '__main__':
    main()
