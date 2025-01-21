from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db_utils import get_gift_list, add_gift, delete_gift
from dotenv import load_dotenv


load_dotenv()
router = Router()


class GiftStates(StatesGroup):
    ADD_GIFT = State()
    DELETE_GIFT = State()


@router.callback_query(F.data == "view_list")
async def list_gift(callback: CallbackQuery):
    gifts = await get_gift_list(callback.from_user.id)
    if not gifts:
        await callback.message.answer("Список подарков пуст. Добавьте что-то!")
    else:
        response = "\n".join(
            [f"{gift['id']}. {gift['gift_name']} - {gift['comment']}. Подарок от {gift['names']}" for gift in gifts]
        )
        await callback.message.answer(f"Список подарков:\n\n{response}")
    await callback.answer()

@router.callback_query(F.data == "gift")
async def add_gift_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите название подарка и комментарий через символ '\\'.\nПример: Подарок1\\Это мой комментарий"
    )
    await state.set_state(GiftStates.ADD_GIFT)
    await callback.answer()

@router.message(GiftStates.ADD_GIFT)
async def process_add_gift(message: Message, state: FSMContext):
    if "\\" not in message.text:
        await message.answer(
            "Неверный формат. Убедитесь, что вы разделили название и комментарий символом '\\'."
        )
        return


    full_name = f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.last_name else message.from_user.first_name
    gift_name, comment = map(str.strip, message.text.split("\\", 1))
    await add_gift(user_id=message.from_user.id, gift_name=gift_name, comment=comment, names=full_name)
    await message.answer(f"Подарок '{gift_name}' добавлен! От {full_name}")
    await state.clear()

@router.callback_query(F.data == "delete_gift")
async def delete_gift_prompt(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите номер подарка, который хотите удалить:")
    await state.set_state(GiftStates.DELETE_GIFT)
    await callback.answer()

@router.message(GiftStates.DELETE_GIFT)
async def process_delete_gift(message: Message, state: FSMContext):
    try:
        gift_id = int(message.text)
        success = await delete_gift(gift_id=gift_id, user_id=message.from_user.id)
        if success:
            await message.answer(f"Подарок с номером {gift_id} успешно удален!")
        else:
            await message.answer("Подарок с таким номером не найден.")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный номер.")
    finally:
        await state.clear()
