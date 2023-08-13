from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import utils.database as db
import os

from aiogram import types, Router, F
from keyboards.admin import start_admin_buttons, admin_buttons, user_cb
from keyboards.basic import cancel_buttons
from keyboards.client import start_buttons, price_buttons

basic_router = Router()


async def show_all_dates(message: types.Message, dates: list):
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        builder = InlineKeyboardBuilder()
        for date_tuple in dates:
            date = date_tuple[0]
            builder.row(
                types.InlineKeyboardButton(
                    text=f"{date.replace(':', '.')} ❌",  # Замена символа ":" на "."
                    callback_data=user_cb(data_id=date.replace(':', '.'), action="del_date").pack()
                ))
        if not dates:
            pass
        else:
            await message.answer('🔽', reply_markup=cancel_buttons)
            await message.answer("Доступные даты:", reply_markup=builder.as_markup())

    elif message.from_user.id != int(os.getenv('SUDO_ID')):
        if not dates:
            pass
        else:
            date_str = '\n'.join(date_tuple[0] for date_tuple in dates)
            await message.answer(f'Доступные даты: \n{date_str}', reply_markup=price_buttons)


@basic_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await db.db_start()
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        await message.answer('Привет Босс!',
                             reply_markup=start_admin_buttons)
    else:
        await message.answer(f'{message.from_user.first_name}, привет!',
                             reply_markup=start_buttons.as_markup())


@basic_router.message(F.text == "Главное меню")
async def cmd_panel(message: types.Message):
    if message.from_user.id != int(os.getenv('SUDO_ID')):
        await message.answer('Вы вернулись в главное меню', reply_markup=start_buttons)

    elif message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        await message.answer('Вы вернулись в главное меню', reply_markup=admin_buttons)


@basic_router.message(F.text == "Помощь")
async def cmd_help(message: types.Message):
    await message.answer('Возникли проблемы в работе бота?\n'
                         'Напиши мне в pm')


@basic_router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer('Возникли проблемы в работе бота?\n'
                         'Напиши мне в pm')


@basic_router.message(F.text == "Обо мне")
async def cmd_help(message: types.Message):
    await message.answer('А что тут должно быть?\n'
                         'Напиши мне в pm')


@basic_router.message(F.text == "Отмена")
async def cmd_panel(message: types.Message, state: FSMContext):
    if message.from_user.id != int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        await state.clear()
        await message.answer('Вы вернулись обратно', reply_markup=start_buttons)

    elif message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        await state.clear()
        await message.answer('Вы вернулись обратно', reply_markup=admin_buttons)
