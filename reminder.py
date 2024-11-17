import os, asyncio
from typing import Final
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime, timedelta

# known issues
'''
* Tasks with the same can be created, this can create confusion when deleting tasks, pls fix
* Need to enter text twice before finished is executed
'''

# to do
'''
* Create a reminder system, make sure that it can be snoozed and it can also be shut up via mentioning that the task is done
* Add a completed tasks list
* Create a function to show the completed function
* Create a way to pause reminders
* Add a way to add persistent storage for tasks'
* undo function
'''


# loading in secrets

load_dotenv
TOKEN: Final = os.getenv("TOKEN")
BOT_NAME: Final = "@TaskReminder_REJ_Bot"

# shared variables
user_data = [[7624783354, 'no', datetime(2024, 11, 17, 11, 4), True, 2]]

# variables for add_task
ASK_NAME, ASK_DATETIME, ASK_REPETITION, IS_REPEAT, HOW_OFTEN, FINISHED = range(6)

# variables for delete_task
DELETE_TASK = 0

# Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thank you for chatting with me!")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This will contain all the commands that I can execute")

# set of functions to add an item to task reminders

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the name of the task.")
    return ASK_NAME

async def ask_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_name = update.message.text
    user_id = update.effective_chat.id
    user_data.append([user_id,task_name])
    await update.message.reply_text(f"When would you like to be reminded of {task_name} (YYYY-MM-DD HH:MM): ")
    return ASK_DATETIME

async def ask_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        reminder_time = datetime.strptime(user_input, r"%Y-%m-%d %H:%M")
        user_data[-1].append(reminder_time)
        await update.message.reply_text("Would you like this reminder to repeat? [Yes/No]")
        return ASK_REPETITION
    except ValueError:
        await update.message.reply_text("Wrong format. Please enter the date and time in YYYY-MM-DD HH:MM format")
        return ASK_DATETIME

async def ask_repetition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    processed_user_input = user_input[0].lower()
    if processed_user_input == "y":
        user_data[-1].append(True)
        await update.message.reply_text("Please enter in how many days do you want to repeat the reminder(>0)")
        return HOW_OFTEN
    elif processed_user_input == "n":
        user_data[-1].append(False)
        user_data[-1].append(0)
        return FINISHED
    else:
        await update.message.reply_text("Please enter Yes/No")
        return ASK_REPETITION

async def ask_how_often(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input: int = int(update.message.text)
    if user_input <= 0:
        await update.message.reply_text("Please enter a positive number")
        return HOW_OFTEN
    user_data[-1].append(user_input)
    return FINISHED

async def finished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = user_data[-1][1]
    await update.message.reply_text(f"The task {name} has been added!")
    print(user_data)
    return ConversationHandler.END

# End of functions that add an item to task reminders

# show all tasks 

async def show_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(user_data) == 0:
        await update.message.reply_text("There are currently no tasks left to complete! Congratulations!")
    else:
        tasks_string = ''
        for task in user_data:
            tasks_string += f"'{task[1]}' : '{str(task[2])}' \n"
        await update.message.reply_text(tasks_string)

# delete tasks

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the name of the task you wish to delete")
    return DELETE_TASK

async def finish_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_name: str = update.message.text
    delete_item(task_name, user_data)
    print(user_data)
    await update.message.reply_text(f"'{task_name}' has been deleted")
    return ConversationHandler.END

def delete_item(item, array):
    temp = []
    for element in array:
        if element[1] == item:
            temp = element
            break
    print(temp)
    array.remove(temp)

# End of delete task functions

# function to check reminders

async def reminder_check(application):
    if (len(user_data) == 0):
        return
    if len(user_data[0]) < 5:
        return
    now = datetime.now()
    for task in user_data:
        if task[2] <= now:
            await application.bot.send_message(chat_id=task[0], text=f"{task[1]} is due now!")
            if task[3]:
                task[2] += timedelta(days=task[4])
            else:
                user_data.remove(task)
            print(user_data)
        elif task[2] - timedelta(minutes=5) <= now:
            due = int((task[2] - now).total_seconds() // 60)
            if_s = "s" if due > 1 else ""
            await application.bot.send_message(chat_id=task[0], text=f"{task[1]} is due in {due} minute{if_s}!")


# clear tasks function
async def clear_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_data
    if len(user_data) == 0:
        await update.message.reply_text("Tasks are already clear")
        return
    user_data = []
    print(user_data)
    await update.message.reply_text("All tasks have been cleared")



# error function
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled")
    return ConversationHandler.END


# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if processed == "done":
        return "Okay"
    if processed == "snooze":
        return "You snooze you lose"
    
    return "Come again?"


# Messages

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: '{text}'")

    if message_type == 'group':
        return
    
    response: str = handle_response(text)

    print(f"Bot: {response}")

    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} cause the following error {context.error}")

if __name__ == "__main__":
    print("Starting Bot")
    app = Application.builder().token(TOKEN).build()

    # create a conversation handler

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add_task", add_task)],
        states={
            ASK_NAME : [MessageHandler(filters.TEXT, ask_task)],
            ASK_DATETIME : [MessageHandler(filters.TEXT, ask_datetime)],
            ASK_REPETITION : [MessageHandler(filters.TEXT, ask_repetition)],
            HOW_OFTEN : [MessageHandler(filters.TEXT, ask_how_often)],
            FINISHED : [MessageHandler(filters.TEXT, finished)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    delete_handler = ConversationHandler(
        entry_points=[CommandHandler("delete_task", delete_task)],
        states={
            DELETE_TASK : [MessageHandler(filters.TEXT, finish_delete)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("show_tasks", show_tasks))
    app.add_handler(CommandHandler("clear_tasks", clear_tasks))
    app.add_handler(conv_handler)
    app.add_handler(delete_handler)
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # background tasks
    app.job_queue.run_repeating(reminder_check, first=0, interval=60)

    # errors
    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)
