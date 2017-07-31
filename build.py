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

def buildvelvet(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        variant=update.message.text.split(' ')[1]
        command=update.message.text.split(' ')[2]
        os.chdir("/home/arn4v/velvet/%s" % variant)
        bot.sendMessage(update.message.chat_id, "Building Velvet for mido: %s variant, %s command" % (variant, command))
        os.system('bash build2.sh %s' % command)
        os.system("mv out/velvet* /home/arn4v/velvet.zip")
        filename = "/home/arn4v/velvet.zip"
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.UPLOAD_DOCUMENT)
        bot.sendDocument(
            document=open(filename, "rb"),
            chat_id=update.message.chat_id)
        os.system("rm /home/arn4v/velvet.zip")
    else:
        sendNotAuthorizedMessage(bot, update)

def sync(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        romdir=update.message.text.split(' ')[1]
        command=update.message.text.split(' ')[2]
        bot.sendMessage(update.message.chat_id, "Syncing %s into /home/arn4v/%s" % romdir)
        os.system("mkdir /home/arn4v/%s" % romdir)
        os.chdir('/home/arn4v/%s' % romdir)
        os.system("%s" % command)
        os.system("repo sync -j128 -q")
        bot.sendMessage(update.message.chat_id, "%s synced in /home/arn4v/%s" % romdir)
    else:
        sendNotAuthorizedMessage(bot, update)

def builder(bot, update):
    if isAuthorized(update):
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
        rom=update.message.text.split(' ')[1]
        device=update.message.text.split(' ')[2]
        command=update.message.text.split(' ')[3]
        os.system("rm ${HOME}/velvet/builderbot/romlink.txt")
        os.system("rm ${HOME}/.rombuild")
        os.system("echo ROM=%s >> /home/arn4v/.rombuild" % rom)
        os.system("echo DEVICE=%s >> /home/arn4v/.rombuild" % device)
        os.system("echo COMMAND=%s >> /home/arn4v/.rombuild" % command)
        bot.sendMessage(update.message.chat_id, "Building %s for %s" % (rom, device))
        os.system("bash ${HOME}/bin/rombuild")
        romlinkfile = open("romlink.txt", "r")
        romlink = romlinkfile.readlines()
        romlink[0]
        bot.sendMessage(update.message.chat_id, parse_mode="Markdown", text = romlink[0])
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
syncHandler = CommandHandler('sync', sync)
uploadHandler = CommandHandler('upload', upload)
restartHandler = CommandHandler('restart', restart)
pullHandler = CommandHandler('pull', pull)
pushHandler = CommandHandler('push', push)

dispatcher.add_handler(idHandler)
dispatcher.add_handler(buildvelvetHandler)
dispatcher.add_handler(builderHandler)
dispatcher.add_handler(syncHandler)
dispatcher.add_handler(uploadHandler)
dispatcher.add_handler(restartHandler)
dispatcher.add_handler(pullHandler)
dispatcher.add_handler(pushHandler)

updater.start_polling()
updater.idle()
