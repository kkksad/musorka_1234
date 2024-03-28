import sqlite3
import random
import qrcode
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

TOKEN="6298575138:AAEARIdXHM95NJyWH21RPM17vOECF5LIwkU"

bot = Bot(token=TOKEN)
dp=Dispatcher()

connection = sqlite3.connect("auth_tabel.db")
cursor = connection.cursor()
cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_table (
            temp_tg_id INT UNIQUE,
            email text UNIQUE,
            password TEXT,
            id TEXT UNIQUE,
            bonus INT
        )
    ''')
def add_user(temp_tg_id:int, email:str, password:str):

    chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '|', '[', ']', '{', '}', ';', ':', ',', '.', '<', '>', '/', '?']
    inside_id = ''.join(random.choice(chars) for _ in range(8))
    cursor.execute(f'INSERT INTO user_table (temp_tg_id, email, password, id, bonus) VALUES (?, ?, ?, ?, ?)', (temp_tg_id,email,password,inside_id,0))
    connection.commit()
    return inside_id
def qr_gen(id:str):

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # Добавляем данные в QR-код
    qr.add_data(id)
    qr.make(fit=True)

    # Создаем изображение QR-кода
    img = qr.make_image(fill_color="black", back_color="white")
    

    return img   

# qr_gen(add_user(6298575138,'9919@mail.ru', 'pass')).save(f'{str(random.randint(1,999999))}.png')
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("сап пидор")
@dp.message(Command('account_info'))
async def with_puree(message: types.Message):
    cursor.execute('select bonus from user_table where temp_tg_id = ?',(str(message.from_user.id),))
    await message.answer(text=f'у вас {str(list(cursor.fetchall()[0])[0])} бонусов')
@dp.message(Command("registr"))
async def registr(message:Message):
   if len(message.text.split())==3:
      try:
        qr_gen(add_user(message.from_user.id, str(message.text.split()[1]), str(message.text.split()[2]))).save(f'{str(message.from_user.id)}.png')
        qr=types.FSInputFile(f'{str(message.from_user.id)}.png')
        await message.answer_photo(caption="ваш qr code", photo=qr)
      except sqlite3.IntegrityError:
        await message.answer("alreadi registr")
   else:
      await message.answer("eblan?")
    

async def main() -> None:
  # Initialize Bot instance with a default parse mode which will be passed to all API calls

  # And the run events dispatching
  await dp.start_polling(bot)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO, stream=sys.stdout)
  asyncio.run(main())

    