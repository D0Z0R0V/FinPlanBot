from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

wish = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Добавить подарок", callback_data="gift"),
                                              InlineKeyboardButton(text="Просмотреть\n список", callback_data="view_list")],
                                              [InlineKeyboardButton(text="Удалить подарок по номеру", 
                                                                    callback_data="delete_gift")]])

post = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Для публикации", callback_data="public"),
                                              InlineKeyboardButton(text="Опубликованные", callback_data="published")]])

wastes = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Жилье", callback_data="housing"),
                                               InlineKeyboardButton(text="Продукты", callback_data="products"),
                                               InlineKeyboardButton(text="Машина", callback_data="car")],
                                               [InlineKeyboardButton(text="Уходовое", callback_data="nursing"),
                                                InlineKeyboardButton(text="Хобби", callback_data="hobby"),
                                                InlineKeyboardButton(text="Досуг", callback_data="leisure")]])

