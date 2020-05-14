#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import inflect

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

users = []

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#States for conversation
CGPA, GRADED_CU, MODS_THIS_SEM, GRADES, LETTERS = range(5) 

#Grade points according to letter grade
grades_dict = {"A+":4.3, "A":4.0, "A-":3.7, "B+":3.3, "B":3.0, "B-":2.7, "C+":2.3, "C":2.0, "C-":1.7, "D+":1.3, "D":1.0, "F":0.0}

def start(update, context):
    user = update.message.from_user
    
    if not user.username in users:
        users.append(user.username)
        logger.info("User %s started the conversation.", user.username)
        logger.info("Users to date: %s", len(users))

    update.message.reply_text(
        "Hi " + user.first_name + "! Welcome to our SMU S/U Decision Maker. We hope you will find this bot useful in helping you obtain the highest possible cGPA for this semester. To restart at any point, please type '/stop'. For any issues please contact @arshhlehhhh. Enjoy!!" 
        "\n\nPlease enter your cumulative GPA (Inclusive of this semester)"
    )
    return CGPA


def collect_cgpa(update, context):
    cgpa = update.message.text

    if (float(cgpa) < 0.0 or float(cgpa) > 4.3):
        update.message.reply_text("GPA must be within 0.0 and 4.3. Please try again.\n\n"
                    "Please enter your cumulative GPA (Inclusive of this semester)"
                )
        return CGPA
    else:
        context.user_data['CGPA'] = float(cgpa)
        update.message.reply_text("Great! Your CGPA is " + cgpa +
        "\n\nWhat is the total number of CUs you have taken so far (including this sem)"
        )
        return GRADED_CU
    
def collect_graded_CUs(update, context):
    gCUs = update.message.text
    user_data = context.user_data
    user = update.message.from_user
    context.user_data['gCUs'] = float(gCUs)

    if float(gCUs) == 0:
        update.message.reply_text("Sorry " + user.first_name + ", you do not have any mods to S/U this sem. Better luck next time!")
        user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text("Awesome! The number of graded CUs you have took including this semester is " + gCUs
                        +   "\n\nHow many graded mods are you taking this sem? (Round up to nearest whole number)"
        )
        return MODS_THIS_SEM

def collect_mods_this_sem(update, context):
    num_of_mod = update.message.text
    user_data = context.user_data
    user = update.message.from_user


    if float(num_of_mod) <= 0:
        update.message.reply_text("Sorry " + user.first_name + ", you do not have any mods to S/U this sem. Better luck next time!")
        user_data.clear()
        return ConversationHandler.END
    elif ((float(num_of_mod) * 0.5) > context.user_data['gCUs']) or float(num_of_mod) > 6:
        update.message.reply_text("Oh no. Are you sure you have " + num_of_mod + " modules this semester?"
                                "\n\nPlease enter the number of graded modules you are taking this sem"
        )
        return MODS_THIS_SEM
    else:
        try:

            context.user_data['mods'] = int(num_of_mod)
            update.message.reply_text("Fantastic! The number of modules you have this semester is " + num_of_mod +
                            "\nNow tell me. How many credit unit (CU) is the 1st module?")
        except:
            context.user_data['mods'] = round(float(num_of_mod),0)
            update.message.reply_text("Fantastic! The number of modules you have this semester is " + num_of_mod + ". I have rounded it up to " + str(context.user_data['mods']) + " for you!"
                                    "\n\nNow tell me. How many credit unit (CU) is the 1st module?")
    
    context.user_data['grades'] = []
    context.user_data['temp_cus'] = 0

    return GRADES

def collect_grades(update, context):
    
    p = inflect.engine()
    cu = update.message.text
    user_data = context.user_data
    user = update.message.from_user

    if float(cu) > context.user_data['gCUs']:
        update.message.reply_text("Credit units for this module should not exceed your total number of credit units taken so far."
                                "\nPlease enter the credit unit again")
        return GRADES
    elif context.user_data['temp_cus'] + float(cu) > context.user_data['gCUs']:
        update.message.reply_text("Sorry " + user.first_name + ", there seem to be some issue with the calculations."
                                "\n\nPlease restart the calculations.")
        user_data.clear()
        return ConversationHandler.END
    else:
        context.user_data['temp_cus'] += float(cu)

    if len(context.user_data['grades']) < context.user_data['mods']:
        i = len(context.user_data['grades'])+1
        reply_keyboard = [['A+'], ['A'], ['A-'], ['B+'], ['B'], ['B-'], ['C+'], ['C'], ['C-'], ['D+'], ['D'], ['F']]
        update.message.reply_text("What is the grade achieved for the " + p.ordinal(i) + " module?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        context.user_data['grades_temp'] = float(cu)
        return LETTERS

def collect_letter_grades(update, context):
    p = inflect.engine()
    letter_grade = update.message.text.upper()
    i = len(context.user_data['grades'])+1
    context.user_data['grades'].append([letter_grade, context.user_data['grades_temp'], grades_dict[letter_grade]])
    
    i = len(context.user_data['grades'])+1
    
    if i <= context.user_data['mods']:
        update.message.reply_text("How many credit unit (CU) is the " + p.ordinal(i) + " module?", reply_markup=ReplyKeyboardRemove())
        return GRADES
    else:
        context.user_data['grades'] = sorted(sorted(context.user_data['grades'], key= lambda x: x[1]), key = lambda x: x[-1], reverse=True)
        user_data = context.user_data

        max_gpa = {'gpa': context.user_data['CGPA'], 'mods': []}
        num_of_gmod = user_data['gCUs']
        cgpa = user_data['CGPA']
        this_sem = user_data['grades']
        cgpa *= num_of_gmod #current total grade point

        counter = 0
        output = ""
        for i in this_sem[::-1]:
            num_of_gmod -= i[1] #current number of cu - mod cu

            cgpa -= (i[2] * i[1])  #current gp - module gpa
            
            try:
                current_gpa = round((cgpa/num_of_gmod),2)
            except:
                current_gpa = 0.00

            if (current_gpa > max_gpa['gpa']):
                max_gpa['gpa'] = current_gpa
                max_gpa['mods'].append(i)

            if(counter == 0):
                output += "If you S/U 1 " + i[0] + " module with " + str(i[1]) + " credit unit, you will get a cumulative GPA of: " + str(current_gpa)
            else:
                output += "\nIf you S/U another 1 " + i[0] + " module with " + str(i[1]) + " credit unit, you will get a cumulative GPA of: " + str(current_gpa)
        
            counter += 1

        output += "\n\nTo get the highest GPA of " + str(max_gpa['gpa'])
        
        if len(max_gpa['mods']) == 0:
            output += "\nYou should not S/U any modules."
        else:
            output += "\nYou should S/U the following modules:"
            for i in max_gpa['mods']:
                output += "\n\tThe " + str(i[1]) + " cu module with grade of " + str(i[0])

        update.message.reply_text(output + "\n\nAll the best! Goodbye!\nType '/start' to calculate again")
    
        user_data.clear()
        return ConversationHandler.END
    

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s ended the conversation.", user.first_name)
    logger.info("Users to date: %s", len(users))
    update.message.reply_text("\n\nAll the best! Goodbye!\nType '/start' to calculate again",
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def help_doc(update, context):
    update.message.reply_text("This bot aims to help SMU students find out which modules to S/U to get the highest cumulative GPA. To begin, type '/start'"
                            "\n\nIf the bot is unresponsive, please check your input or type '/stop' to stop and restart the bot."
                            "\n\nFor any issues and feedback, do contact me at @arshhlehhhh",
                            reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def credits(update, context):
    update.message.reply_text("Thank you for using my bot. This bot is jointly developed by @trevordino and myself @arshhlehhhh. I hope that this bot has been helpful in making a decision to choose the modules to S/U. Do stay tune for more bots!",
                            reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END



def error(update, context):
    update.message.reply_text("Sorry, there is something wrong with your input. Please try again!",
                        reply_markup=ReplyKeyboardRemove())
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1280567863:AAGeaQcqhq-ttptqCPp9q167yUky2ASqaEo", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        #[0]\.[0]|[0-4]\.(\d?\d?)|[4].[3]|[0-4]$
        states={
            CGPA: [MessageHandler(Filters.regex(r"^[0-9]\.[0-9][0-9]|[0-9]\.[0-9]|[0-9]$"), collect_cgpa)
                    ],

            GRADED_CU: [MessageHandler(Filters.regex(r"^[1-9][0-9]\.[05]|[0-9]\.[05]|[1-9][0-9]|[0-9]$"), collect_graded_CUs)
                    ],

            MODS_THIS_SEM: [MessageHandler(Filters.regex(r"^[0]\.[0]|[1][0-2]|[0-9]$"), collect_mods_this_sem)
                    ],
            
            GRADES: [MessageHandler(Filters.regex(r"^[1]\.[05]|[2]\.[0]|[0]\.[5]|\.[5]|[12]$"),collect_grades),
                    ],

            LETTERS: [MessageHandler(Filters.regex(r"^[A-C][+-]|[a-c][+-]|[D]\+|[d+]\+|[A-F]|[a-f]$"),collect_letter_grades)
                    ],
        },

        fallbacks=[CommandHandler('stop', cancel),
                CommandHandler('help', help_doc),
                (CommandHandler('credits',credits))]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
    

# token = '1219486167:AAE4kPuY9bv7FDh6VoN3esRFFzlFeDp-A_k'