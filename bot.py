from timers import *
from files import *
import asyncio
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_polling

chats_files = {}
chats_count = {}

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
    add_chat(message.chat.id)
    global chats_files
    chats_files[message.chat.id] = getfiles()
    if is_Friday():
        global chats_count
        chats_count[message.chat.id] = 0
        await greeting(message.chat.id)
    else:
        await message.reply("Today isn't Chicken\'s Day, but I'll remind you in time.")

@dp.message_handler(commands=['test'])
async def start(message: types.Message):
    try:
        with file_to_send(chats_files.get(message.chat.id)) as photo:
            await message.reply_photo(photo=photo)
    except:
        await message.reply('Something went wrong')


async def run():
    chats = get_chats()
    global chats_files
    chats_files = {chat: getfiles() for chat in chats}
    global chats_count
    chats_count = {chat: 0 for chat in chats}
    for chat_id in chats:
        with dp.current_state(chat=chat_id) as state:
            await state.set_state(FRIDAY)
        await greeting(chat_id)
    while is_Friday():
        chats = get_chats()
        for chat_id in chats:
            count = chats_count.get(chat_id)
            if count >= to_number:
                await send_chicken(chat_id)
                chats_count[chat_id] = 0
        await asyncio.sleep(timer)

    for chat_id in chats:
        with dp.current_state(chat=chat_id) as state:
            await state.set_state(NOT_FRIDAY)

    await wait()

async def greeting(chat_id):
    await bot.send_message(chat_id, 'Friday is the Chicken\'s Day!')
    await send_chicken(chat_id)

async def send_chicken(chat_id):
    try:
        with file_to_send(chats_files.get(chat_id)) as photo:
            await bot.send_photo(chat_id, photo)
    except:
        pass

@dp.message_handler(state='*', commands=['chicken'])
async def chicken_command(message: types.Message):
    await send_chicken(message.chat.id)


@dp.message_handler(state=FRIDAY, regexp='(chicken[s]?|hen[s]?|кур.*|пету[хш].*|rooster[s]?|cock[s]?|цыпл.*)') ##
async def chicken_text(message: types.Message):
    try:
        with file_to_send(chats_files.get(message.chat.id)) as photo:
            await bot.send_photo(message.chat.id, photo, caption='Did you ask for chickens?',
                                 reply_to_message_id=message.message_id)
    except:
        pass

@dp.message_handler(state=None)
async def state_listen(message: types.Message):
    state = dp.current_state(chat=message.chat.id)
    if is_Friday():
        today = FRIDAY
    else:
        today = NOT_FRIDAY
    await state.set_state(today)

@dp.message_handler(state=FRIDAY)
async def listen(message: types.Message):
    try:
        global chats_count
        chats_count[message.chat.id] += 1
        if chats_count.get(message.chat.id) >= after_number:
            await send_chicken(message.chat.id)
            chats_count[message.chat.id] = 0
    except:
        pass

async def wait():
    await asyncio.sleep(wait_to_Friday(find_Friday()))
    await run()

if __name__ == '__main__':
    chats = get_chats()
    chats_files = {chat: getfiles() for chat in chats}
    chats_count = {chat: 0 for chat in chats}
    if is_Friday():
        loop.create_task(run())
    else:
        loop.create_task(wait())

    start_polling(dp, loop=loop, skip_updates=True)
