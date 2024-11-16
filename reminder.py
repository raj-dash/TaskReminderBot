import os
from typing import Final
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# loading in secrets

load_dotenv
TOKEN: Final = os.getenv("TOKEN")
BOT_NAME: Final = "@TaskReminder_REJ_Bot"

# Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thank you for chatting with me!")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This will contain all the commands that I can execute")

# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if processed == "done":
        return "Okay"
    if processed == "snooze":
        return "You snooze you lose"
    
    return "Come again?"


# Messages

def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
