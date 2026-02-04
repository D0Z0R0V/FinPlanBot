from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Подарки"),
                                     KeyboardButton(text="Финансы")],
                                     [KeyboardButton(text="Отчет"),
                                     KeyboardButton(text="Дополнительно")]],
                           resize_keyboard=True,
                           input_field_placeholder="Выберите подходящий пункт меню...")

money = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Доход")],
                                      [KeyboardButton(text="Расходы")],
                                      [KeyboardButton(text="Назад")]],
                            resize_keyboard=True)

dop = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Посты")],
                                      [KeyboardButton(text="Мини игра...")],
                                      [KeyboardButton(text="Назад")]],
                            resize_keyboard=True)