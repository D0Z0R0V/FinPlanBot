from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_utils import add_income, delete_income, get_income_list
from dotenv import load_dotenv

load_dotenv()
router = Router()

class IncomeStates(StatesGroup):
    WAITING_AMOUNT = State()
    WAITING_COMMENT = State()
    DELETE_INCOME = State()


# Обработчик для ВСЕХ источников дохода
@router.callback_query(F.data.in_(["job", "salary"]))
async def handle_income_source(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора источника дохода"""
    # Маппинг callback_data на русские названия
    source_names = {
        "job": "Подработка",
        "salary": "Зарплата"
    }
    
    source_name = source_names.get(callback.data, "Другой доход")
    await state.update_data(source_name=source_name)
    
    await callback.message.answer(
        f"Источник дохода: {source_name}\n\n"
        "Введите сумму дохода:\n"
        "Пример: 1500 или 125.50"
    )
    await state.set_state(IncomeStates.WAITING_AMOUNT)
    await callback.answer()

@router.message(IncomeStates.WAITING_AMOUNT)
async def process_income_amount(message: Message, state: FSMContext):
    """Обработка введенной суммы дохода"""
    try:
        amount_text = message.text.strip().replace(',', '.')
        amount = float(amount_text)
        
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0!")
            return
        
        await state.update_data(amount=amount)
        
        await message.answer(
            "Хотите добавить комментарий к доходу?\n\n"
            "• Напишите комментарий (например: \"Аванс за март\")\n"
            "• Или отправьте \"-\" чтобы пропустить\n"
            "• Или отправьте \"нет\" чтобы оставить без комментария"
        )
        await state.set_state(IncomeStates.WAITING_COMMENT)
        
    except ValueError:
        await message.answer("❌ Введите число! Например: 1500 или 125.50")

@router.message(IncomeStates.WAITING_COMMENT)
async def process_income_comment(message: Message, state: FSMContext):
    """Обработка комментария к доходу"""
    comment = message.text.strip()
    if comment.lower() in ["-", "нет", "нет комментария", "без комментария", "пропустить"]:
        comment = None
    
    data = await state.get_data()
    amount = data.get("amount")
    source_name = data.get("source_name", "Другой доход")
    
    telegram_id = message.from_user.id
    
    # Используем вашу существующую функцию
    await add_income(
        telegram_id=telegram_id,
        amount=amount,
        source=source_name,
        comments=comment
    )
    
    amount_str = f"{amount:.2f}".rstrip('0').rstrip('.')
    
    response = (
        f"Доход добавлен!\n\n"
        f"Источник: {source_name}\n"
        f"Сумма: {amount_str} руб.\n"
    )
    
    if comment:
        response += f"📝 Комментарий: {comment}"
    
    await message.answer(response)
    await state.clear()


@router.callback_query(F.data == "delete_income")
async def delete_income_prompt(callback: CallbackQuery, state: FSMContext):
    """Показать список доходов и запросить номер для удаления"""
    telegram_id = callback.from_user.id
    
    # Получаем последние 10 доходов
    incomes = await get_income_list(telegram_id)
    
    if not incomes:
        await callback.message.answer("У вас нет доходов для удаления.")
        await callback.answer()
        return
    
    # Формируем текст со списком доходов
    income_text = "Ваши последние доходы:\n\n"
    
    for income in incomes[:10]:  # Берем последние 10
        date_str = income['record_date'].strftime('%d.%m') if income['record_date'] else ""
        amount_str = f"{income['amount']:.2f}".rstrip('0').rstrip('.')
        income_text += f"#{income['id']} - {income['source']} - {amount_str} руб."
        if date_str:
            income_text += f" ({date_str})"
        
        if income.get('comments'):
            income_text += f"\n   📝 {income['comments'][:30]}"
        
        income_text += "\n\n"
    
    income_text += "Введите номер дохода для удаления:\n(например: 1)"
    
    await callback.message.answer(income_text)
    await state.set_state(IncomeStates.DELETE_INCOME)
    await callback.answer()

@router.message(IncomeStates.DELETE_INCOME)
async def process_delete_income(message: Message, state: FSMContext):
    """Обработка удаления дохода"""
    try:
        income_id = int(message.text.strip())
        telegram_id = message.from_user.id
        
        success = await delete_income(income_id=income_id, telegram_id=telegram_id)
        
        if success:
            await message.answer(f"✅ Доход #{income_id} удален!")
        else:
            await message.answer(f"❌ Доход #{income_id} не найден.")
            
    except ValueError:
        await message.answer("❌ Введите корректный номер (только цифры).")
    finally:
        await state.clear()