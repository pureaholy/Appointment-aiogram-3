from aiogram import types

kblist = [
    [types.KeyboardButton(text="Отмена")]
]
cancel_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kblist,
                                           input_field_placeholder="Выберите действие")
