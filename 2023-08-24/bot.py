import os

import telebot
from telebot.types import ReplyKeyboardMarkup

from controller import MTMController
import mapping

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
allowed_users = [
    'danibalcells',
    'cheriehu42',
    'ajflores1604',
]
controllers = {}


def request_location(message):
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    itembtn1 = telebot.types.KeyboardButton('Share my location', request_location=True)
    markup.add(itembtn1)
    bot.send_message(message.chat.id, "Please, share your location to continue.", reply_markup=markup)


@bot.message_handler(content_types=['location'])
@bot.message_handler(func=lambda msg: True)
def handle(message):
    username = message.from_user.username
    global controllers
    global allowed_users
    if username not in allowed_users:
        bot.reply_to(message, "You're not on the list!")
        return

    if username not in controllers.keys():
        controller = MTMController()
        controllers[username] = controller
    controller = controllers[username]

    if message.location is not None:
        lat = message.location.latitude
        lng = message.location.longitude
        controller.initial_location = mapping.snap_to_road(lat, lng)
        bot.send_message(chat_id=message.from_user.id, text="What's on your mind?")
        return

    if (not hasattr(controller, 'initial_location'))\
            or (message.text.lower() == "restart"):
        controller.restart()
        request_location(message)
        return
    
    if message.text:
        controller.responses.append(message.text)
        follow_up_questions = controller.get_questions(message.text)

        for question in follow_up_questions:
            new_lat, new_lng = mapping.generate_random_point(
                controller.initial_location[0], 
                controller.initial_location[1], 
                300, 500)
            snapped_lat, snapped_lng = mapping.snap_to_road(new_lat, new_lng)
            map_link = mapping.get_map_link(snapped_lat, snapped_lng)

            ai_response = f"{question}\n{map_link}\n"
            bot.send_message(chat_id=message.from_user.id, text=ai_response)


if __name__ == '__main__':
    bot.infinity_polling()
