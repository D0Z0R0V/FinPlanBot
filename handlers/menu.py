from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
from keyboards import replay, inline
from database.db_utils import register_user, get_financial_report_simple
import requests, os
from datetime import datetime

load_dotenv()
router = Router()


class UrlSmall(StatesGroup):
    LINK = State()
    
class ReportStates(StatesGroup):
    WAITING_PERIOD = State()
    

@router.message(Command("start"))
async def start_command(message: Message):
    # Регистрируем пользователя
    user_id = message.from_user.id
    user_name = message.from_user.full_name or message.from_user.username or "Пользователь"
    
    # Добавляем пользователя в БД
    success = await register_user(user_id, user_name)
    
    if success:
        welcome_text = (
            f"Привет, {user_name}! 👋\n\n"
            "Я бот для учета финансов и управления подарками.\n"
            "Выберите действие из меню."
        )
    else:
        welcome_text = (
            f"С возвращением, {user_name}! 👋\n\n"
            "Рад снова вас видеть! Выберите действие из меню."
        )
    
    await message.answer(welcome_text, reply_markup=replay.main)
    
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

@router.message(F.text == "Отчет")
async def request_report(message: Message, state: FSMContext):
    await message.answer(
        "Введите период для отчета в формате:\n"
        "ГГГГ-ММ-ДД ГГГГ-ММ-ДД\n\n"
        "Пример: 2024-01-01 2024-01-31\n"
        "Или введите 'месяц' для отчета за текущий месяц"
    )
    await state.set_state(ReportStates.WAITING_PERIOD)

@router.message(ReportStates.WAITING_PERIOD)
async def generate_report(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    
    if message.text.lower() == 'месяц':
        today = datetime.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    else:
        try:
            dates = message.text.split()
            if len(dates) != 2:
                raise ValueError
            
            start_date, end_date = dates[0], dates[1]
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            
        except ValueError:
            await message.answer(
                "Неверный формат. Пожалуйста, введите:\n"
                "1. 'месяц' для отчета за текущий месяц\n"
                "2. Или две даты в формате ГГГГ-ММ-ДД ГГГГ-ММ-ДД\n\n"
                "Пример: 2024-01-01 2024-01-31"
            )
            return
    
    # Показываем пользователю, что идет обработка
    await message.answer("Формирую отчет...")
    
    # Получаем упрощенный отчет
    report = await get_financial_report_simple(telegram_id, start_date, end_date)
    
    # Формируем текстовый файл
    file_content = create_report_file(report)
    
    # Создаем файл в памяти
    report_file = BufferedInputFile(
        file_content.encode('utf-8'),
        filename=f"отчет_{start_date}_{end_date}.txt"
    )
    
    # Отправляем файл пользователю
    await message.answer_document(
        report_file,
        caption=f"📊 Отчет за период {start_date} - {end_date}"
    )
    
    await state.clear()

def create_report_file(report_data: dict) -> str:
    """Создание текстового файла с отчетом"""
    period = report_data["period"]
    total_income = report_data["total_income"]
    total_expense = report_data["total_expense"]
    balance = report_data["balance"]
    categories = report_data["category_expenses"]
    
    # Формируем содержимое файла
    content = "=" * 50 + "\n"
    content += "ФИНАНСОВЫЙ ОТЧЕТ\n"
    content += f"Период: {period['start']} - {period['end']}\n"
    content += f"Дата формирования: {datetime.now().strftime('%Y-%m-%d')}\n"
    content += "=" * 50 + "\n\n"
    
    # Итоговые суммы
    content += "ИТОГО:\n"
    content += "-" * 30 + "\n"
    content += f"Заработано:     {total_income:>10.2f} руб.\n"
    content += f"Потрачено:      {total_expense:>10.2f} руб.\n"
    content += f"Баланс:         {balance:>10.2f} руб.\n\n"
    
    # Расходы по категориям
    if categories:
        content += "РАСХОДЫ ПО КАТЕГОРИЯМ:\n"
        content += "-" * 30 + "\n"
        for cat in categories:
            if cat['total'] > 0:  # Показываем только категории с расходами
                content += f"{cat['category']:<20} {cat['total']:>10.2f} руб.\n"
        content += "\n"
    
    # Статус
    content += "=" * 50 + "\n"
    if balance > 0:
        content += f"✅ Положительный баланс: +{balance:.2f} руб.\n"
    elif balance < 0:
        content += f"⚠️ Отрицательный баланс: {balance:.2f} руб.\n"
    else:
        content += f"⚖️ Баланс сведен\n"
    
    content += "=" * 50 + "\n"
    
    return content


@router.message(F.text == "Подарки")
async def wish_user(message: Message):
    await message.answer(text="Доступ открыт", reply_markup=inline.wish)
        
@router.message(F.text == "Посты")
async def post_tg(message: Message):
    await message.answer(text="Что дальше то...?", reply_markup=inline.post)
    
@router.message(F.text == "Финансы")
async def money(message: Message):
    await message.answer(text="Выберите опцию:", reply_markup=replay.money)
    
@router.message(F.text == "Дополнительно")
async def dop(message: Message):
    await message.answer(text="Выберите опцию:", reply_markup=replay.dop)
    
@router.message(F.text == "Расходы")
async def wastes(message: Message):
    await message.answer(text="Много не пиши...", reply_markup=inline.wastes)
    
@router.message(F.text == "Доход")
async def income(message: Message):
    await message.answer(text="Много пиши...", reply_markup=inline.income)
    
@router.message(F.text == "Назад")
async def back_to_main_text(message: Message):
    await message.answer(
        "Возвращаюсь в главное меню!",
        reply_markup=replay.main
    )
    
@router.message(Command("reply"))
async def cmd_reply(message: Message):
    await message.reply('Это ответ с "ответом"')
