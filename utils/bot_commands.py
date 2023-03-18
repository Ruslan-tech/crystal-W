from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Просмотреть услуги или Записаться на мойку"),
            types.BotCommand("help", "Полезная информация"),
            types.BotCommand("location", "Место нахождения"),
            types.BotCommand("quit", "Выход")
        ]
    )