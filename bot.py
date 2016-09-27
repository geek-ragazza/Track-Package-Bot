# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, Job
import logging
import tracking

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)
timers = dict()


def start(bot, update):
    update.message.reply_text(
        'Hello! Use /ups <tracking number> to get updates\n' +
        'if you want to receive your package status updates each hour in one day\n' +
        'Use /track <ups tracking number>'
        'Use /untrack to stop tracking'
    )


def ups(bot, update):
    text = update.message.text
    tracking_num = text[4:]
    tracking_num = tracking_num.lstrip()
    tracking_num = tracking_num.rstrip()
    tracking_rel = tracking.get_ups_info(tracking_num)
    bot.sendMessage(update.message.chat_id, text=tracking_rel)


def alarm(bot, job):
    chat_id = job.context['chat_id']
    tracking_num = job.context['tracking_num']
    tracking_rel = tracking.get_ups_info(tracking_num)
    bot.sendMessage(job.context['chat_id'], text=tracking_rel)
    job.context['updated_times'] += 1
    if job.context['updated_times'] == 23:
        job = timers[chat_id]
        job.schedule_removal()
        del timers[chat_id]
        finish_text = 'Tracking task completed !\nIf you want to continue tracking.\n Use track <tracking number> again.'
        bot.sendMessage(chat_id, text=finish_text)


def track(bot, update, args, job_queue):
    chat_id = update.message.chat_id
    try:
        tracking_num = args[0]
        tracking_num = tracking_num.lstrip()
        tracking_num = tracking_num.rstrip()
        tracking_rel = tracking.get_ups_info(tracking_num)
        update_interval = 3600

        context = {
            'chat_id': chat_id,
            'updated_times': 0,
            'tracking_num': tracking_num
        }
        job = Job(alarm, update_interval, repeat=True, context=context)
        timers[chat_id] = job
        job_queue.put(job)
        reply_text = 'Start tracking {0}\n{1}'.format(tracking_num, tracking_rel)
        update.message.reply_text(reply_text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /track <ups tracking number>')


def untrack(bot, update):

    chat_id = update.message.chat_id

    if chat_id not in timers:
        update.message.reply_text('You have no active tracking task.')
        return

    job = timers[chat_id]
    tracking_num = job.context['tracking_num']
    job.schedule_removal()
    del timers[chat_id]

    update.message.reply_text('Untrack {0}!'.format(tracking_num))


def error(bot, update, error):
    logger.warn('Update "%s"caused error"%s"' % (update, error))


token = 'Token'


def main():
    updater = Updater(token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("ups", ups))
    dp.add_handler(CommandHandler("track", track, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("untrack", untrack))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()

