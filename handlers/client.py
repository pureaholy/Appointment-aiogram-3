import os

import aiogram.exceptions
from aiogram import types, F, Router, Bot
import telegram.error
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

from keyboards.admin import admin_buttons
from keyboards.basic import cancel_buttons
from .basic import show_all_dates

from keyboards.client import price_buttons, get_admin_dates_ikb, service_buttons, start_buttons, client_cb
import utils.database as db


class NewOrder(StatesGroup):
    service = State()
    name = State()
    surname = State()
    date_client = State()
    phone = State()


class NewDate(StatesGroup):
    date_admin = State()


client_router = Router()


@client_router.message(F.text == "Доступные даты")
async def cmd_show_all_dates(message: types.Message):
    dates = await db.get_admin_date()
    sudo_id = int(os.getenv('SUDO_ID'))
    is_admin = await db.is_admin(message.from_user.id)
    if not dates:
        await message.answer('На данный момент нет доступных дат', reply_markup=cancel_buttons)
    await show_all_dates(message, dates)
    if message.from_user.id != sudo_id and not is_admin:
        if not dates:
            pass
        else:
            await message.answer('Уважаемый клиент, если ни одна из предложенных дат вам не подходит,'
                                 ' мы предлагаем связаться с мастером и договориться о более удобной для вас дате и времени.\n'
                                 f'<i> Спасибо за понимание! </i>',
                                 parse_mode='HTML', reply_markup=price_buttons)


@client_router.message(F.text == "Услуги")
async def cmd_services(message: types.Message):
    price = '50 рублей'
    service = 'Коллагенирование ресниц'
    text = f'Услуга: {service}\n Цена услуги: <b>{price}</b>'
    await message.answer(text, parse_mode='HTML')

    price1 = '15 рублей'
    service1 = 'Брови'
    text1 = f'Услуга: {service1}\n Цена услуги: <b>{price1}</b>'
    await message.answer(text1, parse_mode='HTML', reply_markup=price_buttons)


@client_router.message(F.text == "Записаться")
async def cmd_add_service(message: types.Message, state: FSMContext):
    await state.set_state(NewOrder.service)
    await message.answer('Выберите услугу:', reply_markup=service_buttons)


@client_router.message(NewOrder.service)
async def add_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await state.set_state(NewOrder.name)
    await message.answer('Напишите ваше имя:', reply_markup=cancel_buttons)


@client_router.message(NewOrder.name)
async def name_handler(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(NewOrder.surname)
    await message.answer('Напишите вашу фамилию:', reply_markup=cancel_buttons)


@client_router.message(NewOrder.surname)
async def surname_handler(message: types.Message, state: FSMContext):
    date_admin = await db.get_admin_date()
    await state.update_data(surname=message.text)
    await state.set_state(NewOrder.date_client)
    if date_admin is None or len(date_admin) == 0:
        await message.answer('На данный момент нет доступных дат')
        await state.clear()
    else:
        await message.answer('выберите дату:', reply_markup=get_admin_dates_ikb(date_admin))


@client_router.callback_query(NewOrder.date_client, client_cb.filter(F.action == "date_client"))
async def date_select_handler(query: CallbackQuery, callback_data: client_cb, state: FSMContext):
    date_client = callback_data.data_id
    await state.update_data(date_client=date_client)
    await query.answer()
    await state.set_state(NewOrder.phone)
    await query.message.answer('Введите ваш номер телефона', reply_markup=cancel_buttons)


@client_router.message(NewOrder.phone)
async def add_service(message: types.Message, state: FSMContext, bot: Bot):
    phone = message.text
    await state.update_data(phone=phone)
    if message.from_user.id != int(os.getenv('SUDO_ID')):
        await message.answer('Вы записаны, как только мастер будет свободен, он с вами свяжется!\n'
                             'Возникли вопросы?\n'
                             ' Напиши мне в pm', reply_markup=start_buttons)
    else:
        await message.answer('Вы на главном меню', reply_markup=admin_buttons)
    await db.add_item(state)
    await state.clear()

    try:
        await bot.send_message(chat_id=int(os.getenv('NOTICE_ID')), text='К вам новый клиент')
    except (telegram.error.BadRequest, aiogram.exceptions.TelegramNotFound) as e:
        print('При отправке сообщения произошла ошибка:', e)


