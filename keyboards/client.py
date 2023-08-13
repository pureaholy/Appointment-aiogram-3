from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.admin import user_cb


class client_cb(CallbackData, prefix="my"):
    data_id: str
    action: str


kblist = [
    [types.KeyboardButton(text="Услуги"), types.KeyboardButton(text="Доступные даты"),
     types.KeyboardButton(text="Помощь")],
    [types.KeyboardButton(text="Обо мне")]
]

start_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kblist,
                                          input_field_placeholder="Выберите действие")
kblist = [
    [types.KeyboardButton(text="Коллагенирование ресниц"), types.KeyboardButton(text="Брови")],
    [types.KeyboardButton(text="Коллагенирование ресниц и брови")], [types.KeyboardButton(text="Отмена")]
]

service_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kblist,
                                            input_field_placeholder="Выберите действие")
kblist = [
    [types.KeyboardButton(text="Записаться")],
    [types.KeyboardButton(text="Вернуться")]
]
price_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kblist,
                                          input_field_placeholder="Выберите действие")


def get_admin_dates_ikb(data):
    dates_ik = InlineKeyboardBuilder()
    for i in map(lambda x: str(x[0]), data):
        formatted_i = i.replace(':', '.')  # Замена символа ":" на "."
        dates_ik.row(types.InlineKeyboardButton(text=formatted_i,
                                                callback_data=client_cb(data_id=formatted_i, action="date_client").pack()))
    return dates_ik.as_markup()

