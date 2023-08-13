import aiosqlite
from aiogram.fsm.context import FSMContext


async def db_start():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()

        await cur.execute("CREATE TABLE IF NOT EXISTS accounts ("
                          "user_id INTEGER PRIMARY KEY,"
                          "service TEXT, "
                          "name TEXT, "
                          "surname TEXT,"
                          "date_client TEXT, "
                          "phone INTEGER) ")

        await cur.execute("CREATE TABLE IF NOT EXISTS dates ("
                          "user_id INTEGER PRIMARY KEY,"
                          "date_admin TEXT) ")
        await cur.execute('''
                    CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        UNIQUE(user_id)
                    )
                ''')

        await db.commit()


async def get_all_clients():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("SELECT * FROM accounts")
        clients = await cur.fetchall()
        return clients


async def get_all_dates():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("SELECT * FROM dates")
        dates = await cur.fetchall()
        return dates


async def write_date(state: FSMContext):
    async with aiosqlite.connect('utils/tg.db') as db:
        async with db.cursor() as cursor:
            data = await state.get_data()
            datastr = data['date_admin']
            data_list = datastr.split('\n')
            for value in data_list:
                cleaned_value = value.strip()
                if cleaned_value:
                    await cursor.execute("SELECT date_admin FROM dates WHERE date_admin = ?", (cleaned_value,))
                    existing_row = await cursor.fetchone()
                    if existing_row is None:
                        await cursor.execute("INSERT INTO dates (date_admin) VALUES (?)", (cleaned_value,))
                        await db.commit()


async def add_item(state: FSMContext):
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        data = await state.get_data()
        await cur.execute(
            "INSERT INTO accounts (service, name, surname, date_client, phone) VALUES (?, ?, ?, ?, ?)",
            (data['service'], data['name'], data['surname'], data['date_client'], data['phone']))
        await db.commit()


async def delete_user(user_id: int) -> None:
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
        await db.commit()


async def delete_date(user_id: int) -> None:
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("DELETE FROM dates WHERE date_admin = ?", (user_id,))
        await db.commit()


async def get_admin_date():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("SELECT date_admin FROM dates")
        data = await cur.fetchall()
        return data


async def is_admin(user_id):
    async with aiosqlite.connect('utils/tg.db') as db:
        async with db.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)) as cursor:
            admin_data = await cursor.fetchone()

    return admin_data is not None


async def add_admin(user_id):
    if await is_admin(user_id):
        return False

    async with aiosqlite.connect('utils/tg.db') as db:
        await db.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
        await db.commit()

    return True


async def remove_admin(user_id):
    if not await is_admin(user_id):
        return False

    async with aiosqlite.connect('utils/tg.db') as db:
        await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        await db.commit()

    return True
