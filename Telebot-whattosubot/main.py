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

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CGPA, GRADED_CU, MODS_THIS_SEM, GRADES, LETTERS = range(5)

grades_dict = {"A+":4.3, "A":4.0, "A-":3.7, "B+":3.3, "B":3.0, "B-":2.7, "C+":2.3, "C":2.0, "C-":1.7, "D+":1.3, "D":1.0, "F":0.0}

reply_keyboard = [['A+'], ['A'], ['A-'], ['B+'], ['B'], ['B-'], ['C+'], ['C'], ['C-'], ['D+'], ['D'], ['F']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def check_cu(cu):
    try:
        if (float(cu) == 0) or (float(cu) % 0.5 != 0) or (float(cu) < 0.5):
            return False
        return True
    except:
        return False

def start(update, context):
    update.message.reply_text(
        "Hi! Welcome to our SMU S/U Decision Maker. We hope you will find this bot useful in helping you obtain the highest possible cGPA for this semester. To restart at any point, click on the profile and click 'stop' and 'restart'. For any issues please contact @arshhlehhhh. Enjoy!!" 
        "\n\nPlease enter your cumulative GPA (Inclusive of this semester)"
        )

    return CGPA

def collect_cgpa(update, context):
    cgpa = update.message.text
    
    try:
        if (float(cgpa) < 0.0 or float(cgpa) > 4.3):
            update.message.reply_text("Invalid CGPA. Please try again.\n"
                            "Please enter your cumulative GPA (Inclusive of this semester)"
            )
            return CGPA
        else:
            context.user_data['CGPA'] = float(cgpa)
            update.message.reply_text("Thanks! Your CGPA is " + cgpa +
            "\n\nWhat is the total number of CUs you have taken so far (including this sem)"
            )
            return GRADED_CU
    except:
        update.message.reply_text("Invalid CGPA. Please try again.\n"
                                "Please enter your cumulative GPA (Inclusive of this semester)"
        )
        return CGPA

def collect_graded_CUs(update, context):
    gCUs = update.message.text
    
    if not check_cu(gCUs):
        update.message.reply_text("Invalid CUs please try again.\n"
                            "What is the total number of CUs you have taken so far (including this sem)"
        )
        return GRADED_CU
    else:
        context.user_data['gCUs'] = float(gCUs)
        update.message.reply_text("Thanks! The number of graded CUs you have took including this semester is " + gCUs
                            +   "\n\nHow many graded mods are you taking this sem? (Round up to nearest whole number)"
        )
        return MODS_THIS_SEM

def collect_mods_this_sem(update, context):
    num_of_mod = update.message.text
    
    if not (num_of_mod.isdigit() and int(num_of_mod) > 0.0):
        update.message.reply_text("Invalid number of modules please try again.\n"
                                "How many graded mods are you taking this sem? (Round up to nearest whole number)"
        )
        return MODS_THIS_SEM
    else:
        context.user_data['mods'] = int(num_of_mod)
        update.message.reply_text("Thanks! The number of modules you have this semester is " + num_of_mod)

        if num_of_mod != 0:
            update.message.reply_text("How many credit unit (CU) is the 1st module?")
            context.user_data['grades'] = []
            
            return GRADES

def collect_grades(update, context):
    p = inflect.engine()
    cu = update.message.text
    
    if len(context.user_data['grades']) < context.user_data['mods']:
        i = len(context.user_data['grades'])+1

        if not (check_cu(cu) and float(cu) <= 2.0):
            update.message.reply_text("Invalid CUs please try again.")
            update.message.reply_text("How many credit unit (CU) is the " + p.ordinal(i) + " module?")
            return GRADES
        else:
            update.message.reply_text("What is the grade achieved for the " + p.ordinal(i) + " module?", reply_markup=markup)
            context.user_data['grades_temp'] = float(cu)
            return LETTERS

def collect_letter_grades(update, context):
    p = inflect.engine()
    letter_grade = update.message.text.upper()
    i = len(context.user_data['grades'])+1
    if not letter_grade in ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']:
        update.message.reply_text("Invalid Grade\n"
                    "What is the grade achieved for the " + p.ordinal(i) + " module?", reply_markup=markup)
        return LETTERS
    context.user_data['grades'].append([letter_grade, context.user_data['grades_temp'], grades_dict[letter_grade]])
    
    i = len(context.user_data['grades'])+1
    
    if i <= context.user_data['mods']:
        update.message.reply_text("How many credit unit (CU) is the " + p.ordinal(i) + " module?")
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
            current_gpa = round(cgpa/num_of_gmod,2)
            
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

def done(update, context):
    update.message.reply_text("hello")
    user_data = context.user_data

    max_gpa = {'gpa': context.user_data['cgpa'], 'mods': []}
    num_of_gmod = user_data['gCUs']
    cgpa = user_data['CGPA']
    this_sem = user_data['GRADES']
    cgpa *= num_of_gmod

    counter = 0
    for i in this_sem[::-1]:
        num_of_gmod -= i[1]
        cgpa -= i[2]
        current_gpa = round(cgpa/num_of_gmod,2)
        
        if (current_gpa > max_gpa['gpa']):
            max_gpa['gpa'] = current_gpa
            max_gpa['mods'].append(i)

        if(counter == 0):
            update.message.reply_text("If you S/U 1 " + i[0] + " module with " + str(i[1]) + " credit unit, you will get a cumulative GPA of: " + str(current_gpa))
        else:
            update.message.reply_text("If you S/U another 1 " + i[0] + " module with " + str(i[1]) + " credit unit, you will get a cumulative GPA of: " + str(current_gpa))
    
    counter += 1

    user_data.clear()
    return ConversationHandler.END

def error(update, context):
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

        states={
            CGPA: [MessageHandler(Filters.text,
                                      collect_cgpa)
                ],

            GRADED_CU: [MessageHandler(Filters.text,
                                           collect_graded_CUs)
                            ],

            MODS_THIS_SEM: [MessageHandler(Filters.text,
                                          collect_mods_this_sem),
                           ],
            
            GRADES: [MessageHandler(Filters.text,
                                collect_grades),
                    ],
            LETTERS: [MessageHandler(Filters.text,
                    collect_letter_grades),

                ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
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
    

# token = '1280567863:AAGeaQcqhq-ttptqCPp9q167yUky2ASqaEo'