#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import configparser
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
velvet_path = config['VELVET']['velvet']
los_path = config['LOS']['los']
beta_path = config['BETA']['beta']
stock_path = config['STOCK']['stock']
sudo_users = config['ADMIN']['sudo']
dispatcher = updater.dispatcher


def build(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Building and uploading to the chat")
        build_command = ['./build.sh']
        subprocess.call(build_command)
        subprocess.call(build_command)
#        clean_command=os.system("rm /home/arn4v/velvet/*/out/*.zip")
#        subprocess.call(clean_command)
#        filename=os.system("ls /home/arn4v/velvet/*/out/*.zip | tail -1")
#        bot.sendChatAction(chat_id=update.message.chat_id,
#                           action=ChatAction.UPLOAD_DOCUMENT)
#        bot.sendDocument(
#            document=open(filename, "rb"),
#            chat_id=update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot, update)

def los(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Switched to los directory")
#        los_path = '/home/arn4v/velvet/los'
        os.chdir(los_path)
        checkout_command = ['git checkout cm-14.1']
        pull_command = ['git pull git://github.com/velvetkernel/mido cm-14.1']
        reset_command = ['git reset --hard']
#        subprocess.call(reset_command)
#        subprocess.call(checkout_command)
#        subprocess.call(pull_command)
    else:
        sendNotAuthorizedMessage(bot, update)

def beta(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Switched to beta kernel directory")
        os.chdir(beta_path)
        pull_command = ['git pull git://github.com/velvetkernel/mido beta']
        reset_command = ['git reset --hard']
        subprocess.call(reset_command)
        subprocess.call(pull_command)
    else:
        sendNotAuthorizedMessage(bot, update)

def stock(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Switched to beta branch")
#        beta_path = ['/home/arn4v/velvet/beta']
        os.chdir(stock_path)
        checkout_command = ['git checkout beta']
        pull_command = ['git pull git://github.com/velvetkernel/mido beta']
        reset_command = ['git reset --hard']
#        subprocess.call(reset_command)
#        subprocess.call(checkout_command)
#        subprocess.call(pull_command)
    else:
        sendNotAuthorizedMessage(bot, update)

def upload(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Uploading to the chat")
#        clean_command=os.system("rm /home/arn4v/velvet/*/out/*.zip")
#        subprocess.call(clean_command)
#        rename_command=os.system("mv out/velvet* /home/arn4v/velvet.zip")
#        subprocess.call(rename_command)
        filename=os.system("ls out/velvet* | tail -1")
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.UPLOAD_DOCUMENT)
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)
#        delete_command=os.system("rm /home/arn4v/velvet.zip")
#        subprocess.call(delete_command)
    else:
        sendNotAuthorizedMessage(bot, update)


def restart(bot, update):
    if isAuthorized(update):
        bot.sendMessage(update.message.chat_id, "Bot is restarting...")
        time.sleep(0.2)
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        sendNotAuthorizedMessage(bot, update)

def isAuthorized(update):
    return update.message.from_user.id == int(sudo_users)

def sendNotAuthorizedMessage(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                        action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="@" + update.message.from_user.username + " isn't authorized for this task!")


build_handler = CommandHandler('build', build)
los_handler = CommandHandler('los', los)
beta_handler = CommandHandler('beta', beta)
stock_handler = CommandHandler('stock', stock)
upload_handler = CommandHandler('upload', upload)
restart_handler = CommandHandler('restart', restart)

dispatcher.add_handler(build_handler)
dispatcher.add_handler(los_handler)
dispatcher.add_handler(beta_handler)
dispatcher.add_handler(stock_handler)
dispatcher.add_handler(upload_handler)
dispatcher.add_handler(restart_handler)

updater.start_polling()
updater.idle()
# Paul's ID --> 171119240
