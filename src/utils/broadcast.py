from aiogram import Bot
from aiogram import exceptions
import typing as tp
import asyncio
import logging
from datetime import datetime as dt

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

async def send_message(bot: Bot, user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param bot:
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    except exceptions.AiogramError:
        log.error(f"Target [ID:{user_id}]: failed")
    else:
        log.debug(f"Target [ID:{user_id}]: success")
        return True
    return False

async def send_broadcast(bot: Bot, message: str, users: tp.List[int], disable_notification: bool = False) -> None:
    count = 0
    try:
        for user_id in users:
            if await send_message(bot, user_id, message, disable_notification):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        log.info(f"{count} messages successful sent.")

async def schedule_broadcast(
        bot: Bot,
        scheduler: AsyncIOScheduler,
        date_time_exec: dt,
        message: str,
        users: tp.List[int],
        disable_notification: bool = False) -> None:
    """
    Schedule broadcast to users

    :param bot:
    :param scheduler:
    :param date_time_exec:
    :param message:
    :param users:
    :param disable_notification:
    :return:
    """
    scheduler.add_job(
        send_broadcast,
        args=[bot, message, users, disable_notification],
        trigger="date",
        run_date=date_time_exec,
        id="coworking_status_broadcast",
        replace_existing=True,
    )
    log.info("Broadcast finished.")