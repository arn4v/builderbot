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

logfile = '/home/akhil/downloads/.ts/bot-log.txt'

def id(bot, update):
    chatid=str(update.message.chat_id)
    try:
        username=str(update.message.reply_to_message.from_user.username)
        userid=str(update.message.reply_to_message.from_user.id)
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        time.sleep(1)
        bot.sendMessage(update.message.chat_id, text="ID of @" + username + " is " +userid, reply_to_message_id=update.message.reply_to_message.message_id)
    except AttributeError:
        bot.sendMessage(update.message.chat_id, text="ID of this group is " + chatid, reply_to_message_id=update.message.message_id)


def build(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        variant=update.message.text.split(' ')[1]
        os.chdir("/home/arn4v/velvet/%s" % variant)
        bot.sendMessage(update.message.chat_id, "Building Velvet for mido: %s variant" % variant)
        build_command = ['./build.sh']
        subprocess.call(build_command)
        subprocess.call(build_command)
        os.system("mv out/velvet* /home/arn4v/velvet.zip")
        filename = "/home/arn4v/velvet.zip"
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.UPLOAD_DOCUMENT)
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot, update)

#def builder(bot, update):
#    if isAuthorized(update):
#        bot.sendChatAction(chat_id=update.message.chat_id,
#                           action=ChatAction.TYPING)
#        rom=update.message.text.split(' ')[1]
#        device=update.message.text.split(' ')[2]
#        os.chdir("/home/arn4v/%s" % rom)
#        bot.sendMessage(update.message.chat_id, "Building %s" % rom)
#        subprocess.call(['source build/envsetup.sh'])
#        os.system("breakfast %s" % device)
#        os.system("make -j21 bacon")
#        os.system("bash build/envsetup.sh && breakfast %s && make -j21 bacon && cd $OUT" % device)
#        os.system("cd $OUT")
#    else:
#        sendNotAuthorizedMessage(bot, update)

def los(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Switched to los directory")
        os.chdir(los_path)
        checkout_command = ['git checkout cm-14.1']
        pull_command = ['git pull git://github.com/velvetkernel/mido cm-14.1']
        reset_command = ['git reset --hard']
    else:
        sendNotAuthorizedMessage(bot, update)

def beta(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Switched to beta kernel directory")
        os.chdir(beta_path)
    else:
        sendNotAuthorizedMessage(bot, update)

def stock(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Switched to stock kernel directory")
        os.chdir(stock_path)
        pull_command = ['git pull git://github.com/velvetkernel/mido stock']
        reset_command = ['git reset --hard']
        subprocess.call(reset_command)
        subprocess.call(pull_command)
    else:
        sendNotAuthorizedMessage(bot, update)

#def upload(bot, update):
#    if isAuthorized(update):
#        bot.sendChatAction(chat_id=update.message.chat_id,
#                           action=ChatAction.TYPING)
#        bot.sendMessage(chat_id=update.message.chat_id,
#                        text="Uploading to the chat")
#        clean_command=os.system("rm /home/arn4v/velvet/*/out/*.zip")
#        subprocess.call(clean_command)
#        rename_command=os.system("mv out/velvet* /home/arn4v/velvet.zip")
#        subprocess.call(rename_command)
#        filename=os.system("ls out/velvet* | tail -1")
#        filename = "/home/arn4v/velvet.zip"
#        bot.sendChatAction(chat_id=update.message.chat_id,
#                           action=ChatAction.UPLOAD_DOCUMENT)
#        bot.sendDocument(
#            document=open(filename, "rb"),
#            chat_id=update.message.chat_id)
#        delete_command=os.system("rm /home/arn4v/velvet.zip")
#        subprocess.call(delete_command)
#    else:
#        sendNotAuthorizedMessage(bot, update)

def upload(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        filename=update.message.text.split(' ')[1]
        bot.sendMessage(update.message.chat_id, "Uploading %s to chat" % filename)
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.UPLOAD_DOCUMENT)
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)
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

def getlog(bot, update):
    bot.sendDocument(update.message.chat_id, open(logfile, 'rb'))

def clearlog(bot, update):
    if isAuthorized(update):
        subprocess.call(['rm', '-fv', logfile])
        bot.sendMessage(update.message.chat_id, "Cleared logs.")

def pull(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Fetching remote repo")
        subprocess.call(['git', 'fetch', 'origin', 'master', '-f'])
        bot.sendMessage(update.message.chat_id, reply_to_message_id=update.message.message_id, text="Resetting to latest commit")
        subprocess.call(['git', 'reset', '--hard', 'origin/master'])
        restart(bot, update)
    else:
        sendNotAuthorizedMessage(bot, update)

def push(bot, update):
    if isAuthorized(update):
        subprocess.call(['git', 'push', 'origin', 'master'])
        bot.sendMessage(update.message.chat_id, text="K pushed")
    else:
        sendNotAuthorizedMessage(bot, update)

idHandler = CommandHandler('id', id)
buildvelvetHandler = CommandHandler('buildvelvet', buildvelvet)
builderHandler = CommandHandler('builder', builder)
losHandler = CommandHandler('los', los)
betaHandler = CommandHandler('beta', beta)
stockHandler = CommandHandler('stock', stock)
uploadHandler = CommandHandler('upload', upload)
restartHandler = CommandHandler('restart', restart)
pullHandler = CommandHandler('pull', pull)
pushHandler = CommandHandler('push', push)

dispatcher.add_handler(idHandler)
dispatcher.add_handler(buildHandler)
dispatcher.add_handler(builderHandler)
dispatcher.add_handler(losHandler)
dispatcher.add_handler(betaHandler)
dispatcher.add_handler(stockHandler)
dispatcher.add_handler(uploadHandler)
dispatcher.add_handler(restartHandler)
dispatcher.add_handler(pullHandler)
dispatcher.add_handler(pushHandler)

updater.start_polling()
updater.idle()
