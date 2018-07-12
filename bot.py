from timers import *
from files import *
import asyncio
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_polling
from ftplib import FTP

files = getfiles()
count = 0
after_number = 115 # The number of messages after which there will be chicken.
to_number = 2 # The number of messages to which there will be no chicken.
timer = 3600 # The time interval between regular chickens (not chickens for activity). (seconds)

API_TOKEN = token

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# States
FRIDAY = 'Friday'
NOT_FRIDAY = 'not_Friday'


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    state = dp.current_state(chat=message.chat.id)
    if is_Friday():
        await run(message.chat.id)
    else:
        await state.set_state(NOT_FRIDAY)
        await message.reply("Today isn't Chicken's Day, but I'll remind you in time.")
        await asyncio.sleep(wait_to_Friday(find_Friday()))
        await run(message.chat.id)

@dp.message_handler(commands=['test'])
async def start(message: types.Message):
    with file_to_send_path(files) as photo:
        await message.reply_photo(photo=photo.read())


async def run(chat_id):
    with dp.current_state(chat=chat_id) as state:
        await state.set_state(FRIDAY)
    await reset_files()
    global count
    await bot.send_message(chat_id, 'Friday is the Chicken\'s Day!')
    await send_chicken(chat_id)
    while is_Friday():
        if count >= to_number:
            await send_chicken(chat_id)
            count = 0
        await asyncio.sleep(timer)
    with dp.current_state(chat=chat_id) as state:
        await state.set_state(NOT_FRIDAY)

async def reset_files():
    global files
    files = getfiles()

async def send_chicken(chat_id):
    try:
        with file_to_send_path(files) as photo:
            await bot.send_photo(chat_id, photo)
    except:
        pass

@dp.message_handler(state='*', commands=['chicken'])
async def chicken_command(message: types.Message):
    await send_chicken(message.chat.id)


@dp.message_handler(state=FRIDAY, regexp='(^chicken[s]?$|^hen[s]?$|^кур|пету[х|ш]|^rooster$|^cock$|^цыпл)') ##
async def chicken_text(message: types.Message):
    try:
        with file_to_send_path(files) as photo:
            await bot.send_photo(message.chat.id, photo, caption='Did you ask for chickens?',
                                 reply_to_message_id=message.message_id)
    except:
        pass


@dp.message_handler(state=FRIDAY)
async def listen(message: types.Message):
    global count
    count += 1
    if count >= after_number:
        await send_chicken(message.chat.id)
        count = 0


if __name__ == '__main__':
    start_polling(dp, loop=loop, skip_updates=True)