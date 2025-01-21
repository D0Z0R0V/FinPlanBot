from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Подарки"),
                                     KeyboardButton(text="Финансы")],
                                     [KeyboardButton(text="Отчет"),
                                     KeyboardButton(text="Посты"),
                                     KeyboardButton(text="Мини игра..." )]],
                           resize_keyboard=True,
                           input_field_placeholder="Выберите подходящий пункт меню...")