#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
import json
import logging
import os
import subprocess

import time

import sys
from telegram import ChatAction
from telegram.ext import CommandHandler
from telegram.ext import Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('bot.ini')

updater = Updater(token=config['KEYS']['bot_api'])
path = config['PATH']['path']
sudo_users = json.loads(config['ADMIN']['sudo'])
dispatcher = updater.dispatcher


def build(bot, update):
    if update.message.from_user.id in sudo_users:
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Building and uploading to the chat")
        os.chdir(path)
        build_command = ['./build.sh', '-b']
        subprocess.call(build_command)
        filename = "out/" + os.listdir("out")[0]
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)


def upload(bot, update):
    if update.message.from_user.id in sudo_users:
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Uploading to the chat")
        os.chdir(path + "/out")
        filename = os.listdir(".")[0]
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)


def restart(bot, update):
    if update.message.from_user.id in sudo_users:
        bot.sendMessage(update.message.chat_id, "Bot is restarting...")
        time.sleep(0.2)
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        bot.sendMessage(update.message.chat_id, "Ummm, nope.")


build_handler = CommandHandler('build', build)
upload_handler = CommandHandler('upload', upload)
restart_handler = CommandHandler('restart', restart)

dispatcher.add_handler(build_handler)
dispatcher.add_handler(upload_handler)
dispatcher.add_handler(restart_handler)

updater.start_polling()
updater.idle()
# Paul's ID --> 171119240
