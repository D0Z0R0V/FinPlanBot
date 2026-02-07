from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_utils import add_expense, delete_expense, get_expense_list
from dotenv import load_dotenv

load_dotenv()
router = Router()

class ExpenseStates(StatesGroup):
    WAITING_AMOUNT = State()
    DELETE_EXPENSE = State()
    

# Обработчик для ВСЕХ категорий расходов
@router.callback_query(F.data.in_(["housing", "products", "car", "nursing", "hobby", "leisure"]))
async def handle_category(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории расхода"""
    # Маппинг callback_data на русские названия
    category_names = {
        "housing": "Жилье",
        "products": "Продукты", 
        "car": "Машина",
        "nursing": "Уходовое", 
        "hobby": "Хобби",
        "leisure": "Досуг"
    }
    
    category_name = category_names.get(callback.data, "Другое")
    await state.update_data(category_name=category_name)
    
    await callback.message.answer(
        f"Категория: {category_name}\n\n"
        "Введите сумму расхода:\n"
        "Пример: 1500 или 125.50"
    )
    await state.set_state(ExpenseStates.WAITING_AMOUNT)
    await callback.answer()

@router.message(ExpenseStates.WAITING_AMOUNT)
async def process_amount(message: Message, state: FSMContext):
    """Обработка введенной суммы расхода"""
    try:
        amount_text = message.text.strip().replace(',', '.')
        amount = float(amount_text)
        
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0!")
            return
        
        data = await state.get_data()
        category_name = data.get("category_name", "Другое")
        
        telegram_id = message.from_user.id
        await add_expense(
            telegram_id=telegram_id,
            total_sum=amount,
            category_name=category_name
        )
        
        amount_str = f"{amount:.2f}".rstrip('0').rstrip('.')
        
        await message.answer(
            f"Расход добавлен!\n\n"
            f"Категория: {category_name}\n"
            f"Сумма: {amount_str} руб."
        )
        
    except ValueError:
        await message.answer("❌ Введите число! Например: 1500 или 125.50")
    finally:
        await state.clear()

@router.callback_query(F.data == "delete_expense")
async def delete_expense_prompt(callback: CallbackQuery, state: FSMContext):
    """Показать список расходов и запросить номер для удаления"""
    telegram_id = callback.from_user.id
    
    # Получаем последние 10 расходов
    expenses = await get_expense_list(telegram_id, limit=10)
    
    if not expenses:
        await callback.message.answer("У вас нет расходов для удаления.")
        await callback.answer()
        return
    
    # Формируем текст со списком расходов
    expense_text = "Ваши последние расходы:\n\n"
    
    for expense in expenses:
        date_str = expense['record_date'].strftime('%d.%m') if expense['record_date'] else ""
        amount_str = f"{expense['total_sum']:.2f}".rstrip('0').rstrip('.')
        expense_text += f"#{expense['id']} - {expense['category_name']} - {amount_str} руб."
        if date_str:
            expense_text += f" ({date_str})"
        
        if expense.get('comments'):
            expense_text += f"\n   📝 {expense['comments'][:30]}"
        
        expense_text += "\n\n"
    
    expense_text += "👇 Введите номер расхода для удаления:\n(например: 1)"
    
    await callback.message.answer(expense_text)
    await state.set_state(ExpenseStates.DELETE_EXPENSE)
    await callback.answer()

@router.message(ExpenseStates.DELETE_EXPENSE)
async def process_delete_expense(message: Message, state: FSMContext):
    """Обработка удаления расхода"""
    try:
        expense_id = int(message.text.strip())
        telegram_id = message.from_user.id
        
        success = await delete_expense(expense_id=expense_id, telegram_id=telegram_id)
        
        if success:
            await message.answer(f"✅ Расход #{expense_id} удален!")
        else:
            await message.answer(f"❌ Расход #{expense_id} не найден.")
            
    except ValueError:
        await message.answer("❌ Введите корректный номер (только цифры).")
    finally:
        await state.clear()
