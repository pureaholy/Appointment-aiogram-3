import os
from aiogram import types, Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

import utils.database as db
from keyboards.admin import get_edit_ikb, admin_buttons, start_admin_buttons, user_cb
from keyboards.basic import cancel_buttons
from keyboards.client import start_buttons

admin_router = Router()


class NewDate(StatesGroup):
    date_admin = State()


@admin_router.callback_query(user_cb.filter(F.action == "del_date"))
async def cb_delete_date(query: CallbackQuery, callback_data: user_cb):
    date_to_delete = callback_data.data_id
    if ' ' in date_to_delete:
        date_parts = date_to_delete.split()
        time_part = date_parts[1]
        formatted_time = time_part.replace('.', ':')
        date_parts[1] = formatted_time
        formatted_date_for_db = ' '.join(date_parts)
    else:
        formatted_date_for_db = date_to_delete
    await db.delete_date(formatted_date_for_db)
    await query.answer()
    await query.message.edit_text(f"Дата была удалена.", reply_markup=admin_buttons)


@admin_router.callback_query(user_cb.filter(F.action == "del_zapis"))
async def cb_delete_user(query: CallbackQuery, callback_data: user_cb):
    if query.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(query.from_user.id):
        date_to_delete = callback_data.data_id
        await db.delete_user(date_to_delete)
        await query.answer()
        await query.message.reply('Запись была удалена', reply_markup=admin_buttons)


@admin_router.message(F.text == "Админ-панель")
async def cmd_admin(message: types.Message):
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        await message.answer('Админ-панель открыта', reply_markup=admin_buttons)
    else:
        await message.answer('Нет доступа.')




@admin_router.message(F.text == "Добавить дату/время")
async def add_date(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        await message.answer('Напишите дату и время\nМожно также через строчку '
                             'Например:\n01.01.2023\n02.02.2023\nи т.д...', reply_markup=cancel_buttons)
        await state.set_state(NewDate.date_admin)


@admin_router.message(NewDate.date_admin)
async def cmd_add_date(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer("Действие отменено. Возвращаюсь в меню", reply_markup=admin_buttons)
        await state.clear()
    else:
        await state.update_data(date_admin=message.text)
        await message.answer('Дата и время были успешно записаны\nВведите ещё: (Для отмены нажмите соответствующую '
                             'кнопку)', reply_markup=cancel_buttons)
        await db.write_date(state)
        await state.set_state(NewDate.date_admin)


async def show_all_clients(message: types.Message, clients: list):
    for client in clients:
        client_info = f"ID заказа: {client[0]}\n" \
                      f"Тип услуги: {client[1]}\n" \
                      f"Имя: {client[2]} {client[3]}\n" \
                      f"Дата: {client[4]}\n" \
                      f"Номер: {client[5]}"
        await message.answer(client_info, reply_markup=get_edit_ikb(client[0]))


@admin_router.message(F.text == "Все записи")
async def cmd_get_all_clients(message: types.Message):
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        clients = await db.get_all_clients()
        if not clients:
            await message.answer('На данный момент нету записей')

        await show_all_clients(message, clients)


@admin_router.message(F.text == "Вернуться")
async def cmd_get_all_clients(message: types.Message):
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        await message.answer("Вы вернулись в главное меню", reply_markup=start_admin_buttons)
    else:
        await message.answer('Вы вернулись в главное меню', reply_markup=start_buttons)


@admin_router.message(Command("aadmin"))
async def cmd_add_admin(message: types.Message, command: CommandObject, bot: Bot):
    args = command.args
    user_id = int(args)
    chat_info = await bot.get_chat(user_id)
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        result = await db.add_admin(user_id)
        if result:
            await message.reply(f"Пользователь {chat_info.first_name}  добавлен в админы")
        else:
            await message.reply(f'{chat_info.first_name} уже админ!')
    if args is None:
        await message.reply("Пожалуйста, укажите корректный user_id администратора.")
        return
    if int(args) == int(os.getenv('SUDO_ID')):
        await message.answer('Данный пользователь уже является админом (Главный админ)')


@admin_router.message(Command("dadmin"))
async def cmd_remove_admin(message: types.Message, command: CommandObject, bot: Bot):
    args = command.args
    user_id = int(args)
    chat_info = await bot.get_chat(user_id)
    if message.from_user.id == int(os.getenv('SUDO_ID')) or await db.is_admin(message.from_user.id):
        result = await db.remove_admin(user_id)
        if result:
            await message.reply(
                f"Пользователь {chat_info.first_name} удален из списка администраторов.")
        else:
            await message.reply(f"{chat_info.first_name} не является админом!"
                                )
    if args is None:
        await message.reply("Пожалуйста, укажите корректный user_id администратора для удаления.")
        return
    if args == int(os.getenv('SUDO_ID')):
        await message.answer(f'{chat_info.first_name} является Главным админом')
