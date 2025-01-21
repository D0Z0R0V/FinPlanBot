from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

wish = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Добавить подарок", callback_data="gift"),
                                              InlineKeyboardButton(text="Просмотреть список", callback_data="view_list")],
                                              [InlineKeyboardButton(text="Удалить подарок по номеру", 
                                                                    callback_data="delete_gift")]])

post = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Для публикации", callback_data="public"),
                                              InlineKeyboardButton(text="Опубликованные", callback_data="published")]])