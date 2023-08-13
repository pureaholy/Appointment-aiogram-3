from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class user_cb(CallbackData, prefix="my"):
    data_id: str
    action: str


kblist = [
    [types.KeyboardButton(text="Услуги"), types.KeyboardButton(text="Доступные даты"),
     types.KeyboardButton(text="Помощь")],
    [types.KeyboardButton(text="Админ-панель")]
]
start_admin_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kblist,
                                                input_field_placeholder="Выберите действие")

kblist = [
    [types.KeyboardButton(text="Добавить дату/время")],
    [types.KeyboardButton(text="Доступные даты"), types.KeyboardButton(text="Все записи")],
    [types.KeyboardButton(text="Вернуться")]
]
admin_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=kblist,
                                          input_field_placeholder="Выберите действие")


def get_edit_ikb(user_id: int) -> types.InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.add(types.InlineKeyboardButton(
        text='Удалить запись',
        callback_data=user_cb(data_id=f"{user_id}", action="del_zapis").pack()))
    return ikb.as_markup()


def get_dates_ikb(user_id: int) -> types.InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.row(types.InlineKeyboardButton(text="Удалить дату",
                                       callback_data=user_cb(data_id=f"{user_id}", action="del_date").pack()))
    return ikb.as_markup()
