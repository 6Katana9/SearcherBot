from telethon.sync import TelegramClient, events
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from decouple import config
from datetime import datetime, timedelta
from telethon.tl.custom import Button

# Замените на свои значения
API_ID = config('API_ID')
API_HASH = config('API_HASH')
BOT_ID = config('BOT_ID')

# Введите номер телефона и код подтверждения для аутентификации
PHONE_NUMBER = config('PHONE_NUMBER')
SESSION_NAME = config('SESSION_NAME')



bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=config('TOKEN'))

# Создайте клиент Telegram
client = TelegramClient(config('SESSION_NAME'), API_ID, API_HASH)


#Функция для подписки на группы/каналы 
@bot.on(events.NewMessage(pattern='/subscribe'))
async def subscribes_group(event):
    try:
        GROUP = event.text.split(' ', 1)[1] #Отделяю запрос с командой: /subscribe https://t.me/link/ -> https://t.me/link/
        
        with open('groups_id.txt') as f1:
            gr_list = [line.strip() for line in f1.readlines()]
        
        if GROUP in gr_list:
            await event.respond('Эта группа уже есть в подписках')
        else:
            with open('groups_id.txt', 'a') as f:
                f.write(f'{GROUP}\n')
            await event.respond('Группа/канал добавлена в базу данных')
    except:
        await event.respond("Введите так:\n/subscribe https://t.me/link/")


#Функция для запуска кнопок с удалением групп/каналов
@bot.on(events.NewMessage(pattern='/delete_channel'))
async def delete_channel(event):
    try:
        with open('groups_id.txt') as f1:
            channels = [line.strip() for line in f1.readlines()]
        if channels:
            channel_list = channels
            buttons = [Button.inline(f'{channel[13:]}', data=f'delete_channel {channel}') for channel in channel_list]
            # markup = Button.text(buttons)
            await event.respond("Выберите канал для удаления:", buttons=buttons)
        else:
            await event.respond("Список каналов для управления пуст.")

    except Exception as e:
        await event.respond(f"Произошла ошибка: {str(e)}, пожайлуста обратитесь к katan'е - @katana_tlbkv")

# Функция для обработки кнопок удаления группы/канала
@bot.on(events.CallbackQuery(pattern=r'delete_channel (.+)'))
async def button_delete_channel(event):
    try:
        with open('groups_id.txt') as f1:
            channels = [line.strip() for line in f1.readlines()]
        if channels:
            channel_to_delete = event.data_match.group(1)
            channel_to_delete = channel_to_delete.decode("utf-8") 
            if channel_to_delete in channels:
                channels.remove(channel_to_delete)
                with open('groups_id.txt', 'w') as f2:
                    f2.writelines(channels)
                await event.respond(f"Канал {channel_to_delete} удален.")
            else:
                await event.respond("Выбранный канал не найден.")
        else:
            await event.respond("Список каналов для управления пуст.")
    
    except Exception as e:
        await event.respond(f"Произошла ошибка: {str(e)}, пожайлуста обратитесь к katan'е - @katana_tlbkv")



#Функция для поиска инфы по запросу 
@bot.on(events.NewMessage(pattern='/search'))
async def search_messages(event):
    await client.start()
    dialogs = []

    try:
        with open('groups_id.txt') as f:
            groups_list =  [line.strip() for line in f.readlines()]

        if len(event.text.split()) == 1:
            await event.respond("Введите так:\n/search какое-то слово")
            return 0
        
        SEARCH_QUERY = event.text.split(' ', 1)[1] # Отделяю запрос с командой: /search katana -> katana
        
        for i in groups_list:
            dialogs.append(await client.get_entity(i)) #Получаем список всех диалогов пользователя
        
        results = []
        now = datetime.now() # нынещняя дата
        three_days_ago = now - timedelta(days=3) # вычисляю время на три дня
        for dialog in dialogs:

            # Ищем сообщения по запросу в группах и каналах
            result = await client(SearchRequest(
                peer=dialog,
                q=SEARCH_QUERY,
                filter=InputMessagesFilterEmpty(),
                min_date=three_days_ago, # получаю только инфо за последние 3 дня
                max_date=now,
                offset_id=0,
                add_offset=0,
                limit=70,
                max_id=0,
                min_id=0,
                from_id=None,
                hash=0
            ))
            results.extend(result.messages) # расширяю лист найденными сообщениями
                
        if results:
            for message in results:
                chat_id = message.peer_id
                chat = await client.get_entity(chat_id)
                chat_name = chat.title if chat.title else "Группа без названия" # получаю названия групп и каналов
                full_link = chat.username if chat.username else 'Ссылки нет'
                await event.respond(f"Сообщение из группы '{chat_name}'\n{message.message}\n Ссылка: https://t.me/{full_link}/")

        else:
           await event.respond("По вашему запросу ничего не найдено.")
    
    except Exception as e:
        await event.respond(f"Произошла ошибка: {str(e)}, пожайлуста обратитесь к katan'е - @katana_tlbkv")
    
def main():
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
