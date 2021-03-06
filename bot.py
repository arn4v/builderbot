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
sudo_users = config['ADMIN']['sudo']
dispatcher = updater.dispatcher

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

def velvet(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        variant=update.message.text.split(' ')[1]
        command=update.message.text.split(' ')[2]
        os.chdir("/home/arn4v/velvet/kernel/%s" % variant)
        bot.sendMessage(update.message.chat_id, "Building Velvet for mido: %s variant, %s command" % (variant, command))
        os.system('bash build2.sh %s' % command)
        os.chdir("/home/arn4v/velvet/builderbot")
        velvetfile = open("velvet.txt", "r")
        velvetfile2 = velvetfile.read().replace('\n', '')
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.UPLOAD_DOCUMENT)
        bot.sendDocument(
            document=open(velvetfile2, "rb"),
            chat_id=update.message.chat_id)
    else:
        sendNotAuthorizedMessage(bot, update)

def sync(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        romdir=update.message.text.split(' ')[1]
        bot.sendMessage(update.message.chat_id, "Syncing %s" % romdir)
        os.chdir('/home/arn4v/%s' % romdir)
        os.system("time repo sync -f -c --no-clone-bundle -j128 --no-tags")
        bot.sendMessage(update.message.chat_id, "%s synced." % romdir) 
    else:
        sendNotAuthorizedMessage(bot, update)

def builder(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        rom=update.message.text.split(' ')[1]
        device=update.message.text.split(' ')[2]
        command=update.message.text.split(' ')[3]
        os.system("rm /home/arn4v/velvet/builderbot/romlink.txt")
        bot.sendMessage(update.message.chat_id, "Building %s for %s" % (rom, device))
        os.system("bash /home/arn4v/velvet/builderbot/exportrb.sh")
        os.system("bash /home/arn4v/bin/rombuild %s %s %s | tee /home/arn4v/velvet/builderbot/romlog" % (rom, device, command))
        romlinkfile2='/home/arn4v/velvet/builderbot/romlink.txt'
        if os.path.exists(romlinkfile2):
            os.chdir("/home/arn4v/velvet/builderbot")
            romlinkfile = open("romlink.txt", "r")
            romlink = romlinkfile.readlines()
            romlink[0]
            bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text = romlink[0])
        else:
            bot.sendMessage(update.message.chat_id, "FAILED: %s build for %s. Sending log." % (rom, device))
            romlog='/home/arn4v/velvet/builderbot/romlog'
            bot.sendChatAction(chat_id=update.message.chat_id,
                               action=ChatAction.UPLOAD_DOCUMENT)
            bot.sendDocument(
                document=open(romlog, "rb"),
                chat_id=update.message.chat_id)
            os.chdir("/home/arn4v/velvet/builderbot")
            os.system("rm romlog")
    else:
        sendNotAuthorizedMessage(bot, update)

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

def pull(bot, update):
    if isAuthorized(update):
        os.chdir("/home/arn4v/velvet/builderbot")
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
        os.chdir("/home/arn4v/velvet/builderbot")
        subprocess.call(['git', 'push', 'origin', 'master'])
        bot.sendMessage(update.message.chat_id, text="Pushed.")
    else:
        sendNotAuthorizedMessage(bot, update)

idHandler = CommandHandler('id', id)
velvetHandler = CommandHandler('velvet', velvet)
builderHandler = CommandHandler('builder', builder)
syncHandler = CommandHandler('sync', sync)
uploadHandler = CommandHandler('upload', upload)
restartHandler = CommandHandler('restart', restart)
pullHandler = CommandHandler('pull', pull)
pushHandler = CommandHandler('push', push)

dispatcher.add_handler(idHandler)
dispatcher.add_handler(velvetHandler)
dispatcher.add_handler(builderHandler)
dispatcher.add_handler(syncHandler)
dispatcher.add_handler(uploadHandler)
dispatcher.add_handler(restartHandler)
dispatcher.add_handler(pullHandler)
dispatcher.add_handler(pushHandler)

updater.start_polling()
updater.idle()
