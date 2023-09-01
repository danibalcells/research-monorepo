import os

import telebot
from telebot.types import ReplyKeyboardMarkup

from controller import MTMController
import mapping

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
ALLOWED_USERS_FILE = 'allowed_users'
with open(ALLOWED_USERS_FILE) as f:
    allowed_users = [l.strip() for l in f.readlines()]

controllers = {}


def request_location(message):
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    itembtn1 = telebot.types.KeyboardButton('Share my location', request_location=True)
    markup.add(itembtn1)
    bot.send_message(message.chat.id, "Please, share your location to continue.", reply_markup=markup)


# Handler for adding a user
@bot.message_handler(commands=['adduser'])
def add_user(message):
    username = message.from_user.username
    if username == 'danibalcells':
        new_username = message.text.split()[-1] 
        if new_username.startswith('@'):
            new_username = new_username[1:] 
        if new_username not in allowed_users:
            allowed_users.append(new_username)
            with open(ALLOWED_USERS_FILE, 'a') as f:
                f.write(f"{new_username}")
            bot.reply_to(message, f"User @{new_username} added successfully!")
        else:
            bot.reply_to(message, f"User @{new_username} is already in the allowed list.")

# Handler for removing a user
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    username = message.from_user.username
    if username == 'danibalcells':
        remove_username = message.text.split()[-1]
        if remove_username.startswith('@'):
            remove_username = remove_username[1:]  
        if remove_username in allowed_users:
            allowed_users.remove(remove_username)
            with open(ALLOWED_USERS_FILE, 'w') as f:
                for user in allowed_users:
                    f.write(f"{user}\n")
            bot.reply_to(message, f"User @{remove_username} removed successfully!")
        else:
            bot.reply_to(message, f"User @{remove_username} is not in the allowed list.")


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
        controller.locations_by_question = {}
        bot.send_message(chat_id=message.from_user.id, text="What's on your mind?")
        return

    if (not hasattr(controller, 'initial_location'))\
            or (message.text.lower() == "restart"):
        controller.restart()
        request_location(message)
        return
    
    if message.text:
        center = None
        if message.reply_to_message is not None:
            replied_message_id = message.reply_to_message.message_id
            center = controller.locations_by_question.get(replied_message_id)
        if center is None:
            center = controller.initial_location

        if hasattr(controller, 'prev_point'):
            blocked_point = controller.prev_point
        else:
            blocked_point = None

        controller.responses.append(message.text)
        follow_up_questions = controller.get_questions(message.text)

        reply = bot.send_message(
            chat_id=message.from_user.id, 
            text='Please reply (swipe left) to one of the questions below.')
        for question in follow_up_questions:
            new_lat, new_lng = mapping.generate_random_point(
                center[0], 
                center[1], 
                150, 200,
                blocked_point
            )
            snapped_lat, snapped_lng = mapping.snap_to_road(new_lat, new_lng)
            map_link = mapping.get_map_link(snapped_lat, snapped_lng)

            ai_response = f"{question}\n{map_link}\n"
            reply = bot.send_message(chat_id=message.from_user.id, 
                                     text=ai_response)
            controller.locations_by_question[reply.message_id] = (
                snapped_lat,
                snapped_lng)
            controller.prev_point = (snapped_lat, snapped_lng)

if __name__ == '__main__':
    bot.infinity_polling()
