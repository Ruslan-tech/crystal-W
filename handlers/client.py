import os
from data.data import subservices
from aiogram import types, Bot, executor, Dispatcher
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.types import ContentType, InputFile

from keyboards.client_kb import welcome_mrkup, car_mrkup, create_btn_mrkup_services,\
    btn_back_to_services, create_tires_services_kb
from utils.dbmanage.dbcontrol import client_exists, add_client_to_db, \
    delete_client, get_price_wash, get_price_polish, \
    get_price_dry_cleaner, get_price_prot_cover, get_price_liquid_glass, \
    get_price_tires, get_user_bonus, add_bonus_user
import json
from loader import dp, bot
import io
import base64
from PIL import Image
import qrcode
from qrcode.image.pure import PyPNGImage
import cv2
import requests
import numpy


# фиксируем прилет qr-code
@dp.message_handler(content_types=ContentType.PHOTO)
async def send_photo_file_id(message: types.message):
    # Сохраняем картинку на серверах телеги и запихиваем ее в переменную ввиде байт кода
    photo_file_id = message.photo[-1].file_id
    print(photo_file_id)
    file_photo = await bot.get_file(photo_file_id)
    file_path = file_photo.file_path
    url_info = f"https://api.telegram.org/file/bot{os.getenv('API_TOKEN')}/"
    img = requests.get(url_info + file_path)
    img_b = Image.open(io.BytesIO(img.content))
    # из байт кода в массив
    open_cv_image = numpy.array(img_b)
    # декодируем qr-code
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(open_cv_image)
    print(data)

    if data == "":
        message_adm = "Ошибка QR-code. Попробуйте еще раз."
    if data.find("cry: ") == 0:
        message_adm = "QR-code. Успешно просканирован."
        #####работа с БД######
        to_BD_user = data[5:]
        print(int(to_BD_user))
        user_bonus = get_user_bonus(int(to_BD_user))
        if user_bonus < 6:
            add_bonus_user(int(to_BD_user), user_bonus + 1)
            await message.reply(text=f"Замечательно. Копим бонусы дальше")
        elif user_bonus == 6:
            add_bonus_user(int(to_BD_user), 0)
            await message.reply(text="У Вас скидка на сегодняшнюю мойку")
        ######################
    else:
        message_adm = "Неверный QR-code."

    await message.reply(text=message_adm)


@dp.message_handler(commands=['bonus'])
async def get_my_bonus(message: types.message):
    bonus = get_user_bonus(message.from_user.id)
    await bot.send_message(message.from_user.id, 
                           text=f"{message.from_user.first_name} ваш бонус {bonus}. \
                               \n Копите бонусы пользуясь услугами нашего \
                               \n автомоечного комплекса. \
                               \n Не забывайте сканировать ваш qr-code у администратора комплекса.\
                               \n Скидка предоставляется на каждую 6ю мойку.")


@dp.message_handler(commands=['start'])
async def start_welcome(message: types.message):
    if not client_exists(message.from_user.id):
        add_client_to_db(message.from_user.id, message.from_user.username)
    
    await bot.send_message(message.from_user.id, text=f"Привет {message.from_user.first_name}",
                           reply_markup=welcome_mrkup)


@dp.callback_query_handler(text="qr_code")
async def qr_code(message: types.message):
    # проверочный флаг лигитимности QR-code
    flag = "cry: "
    # создаем QR-code и сохраняем в фаил
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(flag + str(message.from_user.id))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    os.makedirs("qrcode", exist_ok=True)
    img.save(r"qrcode/" + base64.b64encode(message.from_user.first_name.encode('UTF-8')).decode("UTF-8") + ".png")
    photo = InputFile(
        r"qrcode/" + base64.b64encode(message.from_user.first_name.encode('UTF-8')).decode("UTF-8") + ".png")

    await bot.send_photo(message.from_user.id, photo=photo)


@dp.callback_query_handler(text="go_wash")
async def go_wash(callback: types.CallbackQuery):
    await callback.message.answer(text="🫵 Для записи на автомоечный комплекс позвоните по телефону 📞 +7(965)766-66-55")


@dp.callback_query_handler(text="car_mrkup")
async def go_cat(callback: types.CallbackQuery):
    await callback.message.answer(text="Выберите класс вашего авто:", reply_markup=car_mrkup)


cars_types = {"sedan": "седан", "cross": "кроссовер", "vned": "внедорожник", "microbus": "микроавтобус"}

cars_service_types = {"moika_sedan": {1: "седан"}, "moika_cross": {2: "кроссовер"}, "moika_vned": {3: "внедорожник"},
                      "moika_microbus": {4: "микроавтобус"}}

cars_service_polish_types = {"polish_sedan": {1: "седан"}, "polish_cross": {2: "кроссовер"},
                             "polish_vned": {3: "внедорожник"}, "polish_microbus": {4: "микроавтобус"}}

cars_service_dry_cleaner_types = {"dry_cleaner_sedan": {1: "седан"}, "dry_cleaner_cross": {2: "кроссовер"},
                                  "dry_cleaner_vned": {3: "внедорожник"},
                                  "dry_cleaner_microbus": {4: "микроавтобус"}}

cars_service_prot_cover_types = {"prot_cover_sedan": {1: "седан"}, "prot_cover_cross": {2: "кроссовер"},
                                 "prot_cover_vned": {3: "внедорожник"},
                                 "prot_cover_microbus": {4: "микроавтобус"}}

car_service_tiers_types = {"tiers_sedan": {1: "седан"}, "tiers_cross": {2: "кроссовер"},
                           "tiers_vned": {3: "внедорожник"},
                           "tiers_microbus": {4: "микроавтобус"}}


@dp.callback_query_handler()
async def get_services_wash_car(callback: types.CallbackQuery):
    if callback.data in cars_types.keys():

        await callback.message.answer(text=f"Выберите услугу для 👉{cars_types.get(callback.data)}а",
                                      reply_markup=create_btn_mrkup_services(callback.data))
        # await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

    elif callback.data in cars_service_types.keys():

        coast_mojka = get_price_wash([k for k in cars_service_types.get(callback.data).keys()][0])
        call_spl = callback.data.split("_")[1]
        await callback.message.answer(
            text=f"<u>Цены 💰 на услугу <b>МОЙКА {[v for v in cars_service_types.get(callback.data).values()][0]}а</b></u> \n\
            \n🚰 Технологическая мойка - <u><b>{coast_mojka[0]} рублей</b></u>\
            \n🚰 Технологическая мойка + шампунь - <u><b>{coast_mojka[1]} рублей</b></u>\
            \n💧 Мойка кузова (шампунь + сушка) - <u><b>{coast_mojka[2]} рублей</b></u>\
            \n💧 Мойка СТАНДАРТ (+ мытье ковров) - <u><b>{coast_mojka[3]} рублей</b></u>\
            \n💧 Мойка «LUX Express» - <u><b>{coast_mojka[4]} рублей </b></u>\
            \n💧 Мойка «LUX Classic» - <u><b>{coast_mojka[5]} рублей </b></u>\
            \n💧 Мойка «Premium» - <u><b>{coast_mojka[6]} рублей </b></u>\
            \n💧 Мойка «Premium Extra» - <u><b>{coast_mojka[7]} рублей </b></u>\
            \n🧹 Уборка салона - <u><b>{coast_mojka[8]} рублей </b></u>\
            \n🧹 Удаление насекомых - <u><b>{coast_mojka[9]} рублей </b></u>\
            \n🧹 Уборка шерсти - <u><b>{coast_mojka[10]} рублей </b></u>\
            \n🧹 Уборка салона пылесосом - <u><b>{coast_mojka[11]} рублей </b></u>\
            \n🧹 Очистка стекол в салоне - <u><b>{coast_mojka[12]} рублей </b></u>\
            \n🧹 Очистка пластика в салоне - <u><b>{coast_mojka[13]} рублей </b></u>\
            \n🧹 Уборка багажника - <u><b>{coast_mojka[14]} рублей </b></u>\
            \n🧹 Обезжиривание кузова «ANTI OIL» - <u><b>{coast_mojka[15]} рублей </b></u>\
            \n🧹 Удаление битумных пятен - <u><b>{coast_mojka[16]} рублей </b></u>\
            \n💧 Кондиционер кожи Luxe - <u><b>{coast_mojka[17]} рублей </b></u>\
            \n💧 Кондиционер кожи Premium - <u><b>{coast_mojka[18]} рублей </b></u>\
            \n💧 Силиконовая смазка + смазка замков - <u><b>{coast_mojka[19]} рублей </b></u>\
            \n🧹 Очистка колесных дисков (1 колесо) - <u><b>{coast_mojka[20]} рублей </b></u>\
            \n🧹 Чернение резины - <u><b>{coast_mojka[21]} рублей </b></u>\
            \n💧 Стирка текстильных ковров (1 шт.) - <u><b>{coast_mojka[22]} рублей </b></u>\
            \n💧 Мойка моторного отсека - <u><b>{coast_mojka[23]} рублей </b></u>\
            \n💧 Мойка резиновых ковров - <u><b>{coast_mojka[24]} рублей </b></u>\
            \n💧 Мойка колес (4 шт.) - <u><b>{coast_mojka[25]} рублей</b></u>",
            reply_markup=btn_back_to_services(call_spl), parse_mode="HTML")
        # create_btn(get_price_wash([k for k in cars_service_types.get(callback.data).keys()][0]))


    elif callback.data in cars_service_polish_types.keys():

        coast_polish = get_price_polish([k for k in cars_service_polish_types.get(callback.data).keys()][0])
        call_spl = callback.data.split("_")[1]
        await callback.message.answer(
            text=f"<u>Цены 💰 на услугу <b>ПОЛИРОВКА {[v for v in cars_service_polish_types.get(callback.data).values()][0]}а</b> </u>\n \
            \n✨ Полировка фар (1 фара) - <u><b>{coast_polish[0]} рублей</b></u>\
            \n✨ Легкая полировка кузова (глянцевая) - <u><b>{coast_polish[1]} рублей</b></u>\
            \n✨ Глубокая абразивная полировка кузова ЗМ - <u><b>{coast_polish[2]} рублей</b></u>\
            \n✨ Полировка 1 элемента - <u><b>{coast_polish[3]} рублей</b></u>\
            \n💦 Анти-дождь GLACO SOFT 99, (лоб. ст. + перед. ст.) - <u><b>{coast_polish[4]} рублей</b></u>\
            \n💦 Анти-дождь GLACO SOFT 99, (все стекла) - <u><b>{coast_polish[5]} рублей</b></u>\
            \n💦 Анти-дождь Aquapel, (полусфера) - <u><b>{coast_polish[6]} рублей</b></u>",
            reply_markup=btn_back_to_services(call_spl), parse_mode="HTML")

    elif callback.data in cars_service_dry_cleaner_types.keys():

        coast_dry_cleaner = get_price_dry_cleaner(
            [k for k in cars_service_dry_cleaner_types.get(callback.data).keys()][0])
        call_spl = callback.data.split("_")[2]
        await callback.message.answer(
            text=f"<u>Цены 💰 на услугу <b>ХИМЧИСТКА {[v for v in cars_service_dry_cleaner_types.get(callback.data).values()][0]}а</b> </u>\n \
            \n😶‍🌫️ Полная химчистка салона (+ потолок и багажник) - <u><b>{coast_dry_cleaner[0]} рублей</b></u>\
            \n🧪 Химчистка пола (1 место) - <u><b>{coast_dry_cleaner[0]} рублей</b></u>\
            \n🧪 Химчистка потолока - <u><b>{coast_dry_cleaner[1]} рублей</b></u>\
            \n🧪 Химчистка сидений (1 место) - <u><b>{coast_dry_cleaner[2]} рублей</b></u>\
            \n🧪 Химчистка дверей (1 место) - <u><b>{coast_dry_cleaner[3]} рублей</b></u>\
            \n🧪 Химчистка багажника - <u><b>{coast_dry_cleaner[4]} рублей</b></u>\
            \n🧪 Удаление трудновыводимых пятен - <u><b>{coast_dry_cleaner[5]} рублей</b></u>",
            reply_markup=btn_back_to_services(call_spl), parse_mode="HTML")

    elif callback.data in cars_service_prot_cover_types.keys():

        coast_prot_cover = get_price_prot_cover([k for k in cars_service_prot_cover_types.get(callback.data).keys()][0])
        call_spl = callback.data.split("_")[2]
        await callback.message.answer(
            text=f"<u>Цены 💰 на услугу <b>ЗАЩИТНЫЕ ПОКРЫТИЯ {[v for v in cars_service_prot_cover_types.get(callback.data).values()][0]}а</b> </u>\n \
            \n🛡🧊 Обработка кузова холодным воском - <u><b>{coast_prot_cover[0]} рублей</b></u>\
            \n🛡 Полимерное покрытие Sonax - <u><b>{coast_prot_cover[1]} рублей</b></u>\
            \n🛡 Кварцевое покрытие - <u><b>{coast_prot_cover[2]} рублей</b></u>\
            \n🛡 Покрытие ТЕФЛОН Authentic Premium(SOFT99) - <u><b>{coast_prot_cover[3]} рублей</b></u>\
            \n🛡 Покрытие жидким стекл. Body Glass Guard (Willson) - <u><b>{coast_prot_cover[4]} рублей</b></u>\
            \n🛡 Покрытие жидким стекл. H-7 Glass Coating (SOFT99) - <u><b>{coast_prot_cover[5]} рублей</b></u>\
            \n🛡 Покрытие керамикой 1 слой - <u><b>{coast_prot_cover[6]} рублей</b></u>",
            reply_markup=btn_back_to_services(call_spl), parse_mode="HTML")

    elif callback.data == "liq_glass":
        await callback.message.answer(text=f"<u><b>ЖИДКОЕ СТЕКЛО</b></u> \n \
            \n💰 Покрытие кузова жидким стеклом <u>H-7 Glass Coating (SOFT99, Япония)</u> – цена от <u><b>{get_price_liquid_glass(3)} рублей.</b></u>\
            \n💧 H7 жидкое стекло для автомобиля обеспечивает надежную защиту кузова от различных воздействий внешней среды: \n\
                \n✅ осадков (дождя, снега, града)\n\
                \n✅ грязи\n\
                \n✅ морской воды\n\
                \n✅ экстремальных перемен температуры\n\
                \n✅ абразивного воздействия", parse_mode="HTML")
    elif callback.data == "presale":
        await callback.message.answer(text=f"<u><b>ПРЕДПРОДАЖНАЯ ПОДГОТОВКА</b></u> \n\
            \n📍  Специалисты нашей компании проведут предпродажную \
            \nподготовку Вашего автомобиля <u>на высочайшем уровне</u> \
            \nуже сегодня так, что завтра у Вас не будет отбоя от покупателей! \n\
            \n📍  Если вы решили продать свой автомобиль, ему необходимо \
            \nпридать товарный вид – <u>провести предпродажную подготовку.</u> \n\
            \n📍  Такая подготовка включает в себя целый комплекс действий, \
            \nкоторые при незначительных денежных 💰 затратах могут \
            \nповысить ☝️ рыночную стоимость вашей машины 🚗.\n \
            \n📍  Предпродажная подготовка – цена от <u><b>10 000 рублей</b></u>", parse_mode="HTML")
    elif callback.data in car_service_tiers_types.keys():
        coast_tires = get_price_tires([k for k in car_service_tiers_types.get(callback.data).keys()][0])
        call_spl = callback.data.split("_")[1]
        print(coast_tires)
        print(call_spl)
        await callback.message.answer(text="Выберите услугу: ", reply_markup=create_tires_services_kb())
        # await callback.message.answer(text=f"<u><b>ПОЛНЫЙ ШИНОМОНТАЖ 4-Х КОЛЁС</b></u> \n \
        # (ВКЛЮЧАЕТ СНЯТИЕ, УСТАНОВКУ И БАЛАНСИРОВКУ)", parse_mode="HTML")
        # for el in coast_tires:
        #     await callback.message.answer(text=f"<u><b>{el} рублей</b></u>", parse_mode="HTML")
        # await callback.message.answer(text="", parse_mode="HTML")
           


@dp.message_handler(commands=['quit'])
async def delete_client(message: types.message):
    delete_client(message.from_user.id)
    await bot.send_message(message.from_user.id, text=" 😥Жаль, что вы нас покидаете. Мы ждем Вас снова. 👋")


@dp.message_handler(commands=['location'])
async def info(message: types.message):
    await bot.send_message(message.from_user.id,
                           text="🗺 Коломяжский пр., д. 19 (территория АЗС «ЛИНОС»)\n🗺 Выборгская наб., д. 57, лит. А (территория АЗС «ЛИНОС»).")
