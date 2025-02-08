from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
from keyboards import replay, inline
import requests

load_dotenv()
router = Router()

class UrlSmall(StatesGroup):
    LINK = State()

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Я бот для учета финансов и управления подарками.\
        Выберите действие из меню.", reply_markup=replay.main)
    
@router.message(Command("link"))
async def small_url(message: Message, state: FSMContext):
    await message.answer("Введите искомую ссылку")
    await state.set_state(UrlSmall.LINK)
    
@router.message(State(UrlSmall.LINK))
async def process_link(message: Message, state: FSMContext):
    url_link = message.text
    api_url = f'https://tinyurl.com/api-create.php?url={url_link}'
    response = requests.get(api_url)
    await message.answer(f"Сокращенная ссылка: {response.text}")
    await state.clear()

users = {}

def user_allowed(message: types.Message):
    return message.from_user.id in users

@router.message(F.text == "Подарки")
async def wish_user(message: Message):
    if user_allowed(message):
        await message.answer(text="Доступ открыт", reply_markup=inline.wish)
    else:
        await message.answer(text="Только для многоуважаемых персон")
        
@router.message(F.text == "Посты")
async def post_tg(message: Message):
    await message.answer(text="Что дальше то...?", reply_markup=inline.post)
    
@router.message(F.text == "Финансы")
async def money(message: Message):
    await message.answer(text="Выберите опцию:", reply_markup=replay.money)
    
@router.message(F.text == "Траты")
async def wastes(message: Message):
    await message.answer(text="Много не пиши...", reply_markup=inline.wastes)
    
@router.message(Command("reply"))
async def cmd_reply(message: Message):
    await message.reply('Это ответ с "ответом"')
