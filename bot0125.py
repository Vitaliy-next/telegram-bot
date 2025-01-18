import os
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения

# Инициализация Flask-приложения
app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Список ID подписчиков
subscribers = []

# Пароль для доступа к админ-меню
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
email = os.getenv('EMAIL')
password = os.getenv('EMAIL_PASSWORD')  # Пароль приложения от Google
recipient = email  # Email для получения заказа
TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
recipient = email  # Email для получения заказа


# Функции для работы с файлом JSON
def load_subscribers():
    """Загружает список подписчиков из файла."""
    global subscribers
    try:
        with open("subscribers.json", "r") as file:
            subscribers = json.load(file)
            logger.info("Список подписчиков загружен.")
    except FileNotFoundError:
        subscribers = []
        logger.info("Файл subscribers.json не найден. Создаётся пустой список подписчиков.")
    except Exception as e:
        logger.error(f"Ошибка загрузки подписчиков: {e}")
        subscribers = []


def save_subscribers():
    """Сохраняет список подписчиков в файл."""
    try:
        with open("subscribers.json", "w") as file:
            json.dump(subscribers, file)
            logger.info("Список подписчиков сохранён.")
    except Exception as e:
        logger.error(f"Ошибка сохранения подписчиков: {e}")


# Функция для отправки уведомлений
async def send_notifications(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Отправляет сообщение всем подписчикам."""
    logger.info(f"Список подписчиков: {subscribers}")
    for user_id in subscribers:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            logger.info(f"Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            logger.warning(f"Не удалось отправить сообщение пользователю {user_id}: {e}")


# Функция для отправки писем (фиктивная)
def send_email(subject: str, body: str):
    # def send_email(email, subject, body):
    logger.info(f"Email отправлен на {email} с темой '{subject}' и текстом:\n{body}")
    try:
        # Создание сообщения
        message = MIMEMultipart()
        message["From"] = email  # Используем локальную переменную email вместо EMAIL

        message["To"] = recipient  # Используем локальную переменную recipient
        message["Subject"] = subject

        # Добавляем текст письма
        message.attach(MIMEText(body, "html"))

        # Настраиваем SMTP-сервер и отправляем письмо ВСЕ В ДЕЛО нужно смотреть с какой буквы маленькая, большая, это важно
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email, password)
            server.sendmail(email, recipient, message.as_string())
        print("Email успешно отправлен.")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


# Функция стартового меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавляет пользователя в список подписчиков и отображает главное меню."""
    user_id = update.effective_user.id
    if user_id not in subscribers:
        subscribers.append(user_id)
        save_subscribers()

    keyboard = [
        [InlineKeyboardButton("Загальна інформація", callback_data="info")],
        [InlineKeyboardButton("Звітність для ФОП", callback_data="reports")],
        [InlineKeyboardButton("Розрахунок податків", callback_data="taxes")],
        [InlineKeyboardButton("Як вести облік?", callback_data="accounting")],
        [InlineKeyboardButton("🌟Короткий опрос і Ваші питання ", callback_data="unswer_question")],
        [InlineKeyboardButton("Допомога", callback_data="help")],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text("Виберіть розділ:", reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text("Виберіть розділ:", reply_markup=reply_markup)


# Функция админ-меню
# Функция помощи
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Що таке ФОП?", callback_data="help_what_is_fop")],
        [InlineKeyboardButton("📚 Як змінити систему оподаткування?", callback_data="help_change_system")],
        [InlineKeyboardButton("📚 Як подати звітність для ФОП?", callback_data="help_filing_reports")],
        [InlineKeyboardButton("📚 Як розрахувати податки?", callback_data="help_calculate_taxes")],
        [InlineKeyboardButton("📚 Як вести облік?", callback_data="help_accounting")],
        [InlineKeyboardButton("🔍 Знайти відповідь", callback_data="help_search")],
        [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
    ]
    await update.callback_query.edit_message_text(
        "Обиріть питання або скористайтеся пошуком:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# Обработка нажатия кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    # Загальна інформація
    if data == "info":
        keyboard = [
            [InlineKeyboardButton("Що таке ФОП?", callback_data="info_what")],
            [InlineKeyboardButton("Групи та системи оподаткування", callback_data="info_groups")],
            [InlineKeyboardButton("Як змінити систему?", callback_data="info_change")],
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text("Загальна інформація:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "info_what":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "ФОП – це фізична особа-підприємець, яка веде бізнес без створення юридичної особи.",
            reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "info_groups":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "1 група – малий бізнес. 2 група – послуги для населення/ФОП. 3 група – ширші можливості, включаючи роботу з НДС.",
            reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "info_change":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Щоб змінити систему оподаткування, подайте заяву до податкової до кінця кварталу.",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "reports":
        keyboard = [
            [InlineKeyboardButton("1 група", callback_data="reports_group1")],
            [InlineKeyboardButton("2 група", callback_data="reports_group2")],
            [InlineKeyboardButton("3 група", callback_data="reports_group3")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
        ]
        await query.edit_message_text("Оберіть групу для звітності:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "reports_group1":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Звітність для 1 групи ФОП:\n"
            "- Подання декларації раз на рік (до 1 березня).\n"
            "- Сплата ЄСВ до 20 січня наступного року.\n"
            "- Подача книги обліку доходів за бажанням.", reply_markup=InlineKeyboardMarkup(keyboard))


    elif data == "reports_group2":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Звітність для 2 групи ФОП:\n"
            "- Подання декларації раз на рік (до 1 березня).\n"
            "- Сплата ЄСВ до 20 січня наступного року.\n"
            "- Подача книги обліку доходів за бажанням.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "reports_group3":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Звітність для 3 групи ФОП:\n"
            "- Декларація подається щоквартально.\n"
            "- При реєстрації платником ПДВ звітність подається щомісяця.\n"
            "- Сплата ЄСВ до 20 числа місяця, наступного за кварталом.", reply_markup=InlineKeyboardMarkup(keyboard))

        # Розрахунок податків
    if data == "taxes":
        keyboard = [
            [InlineKeyboardButton("1 група", callback_data="taxes_group1")],
            [InlineKeyboardButton("2 група", callback_data="taxes_group2")],
            [InlineKeyboardButton("3 група", callback_data="taxes_group3")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")],
        ]
        await query.edit_message_text("Оберіть групу для розрахунку податків:",
                                      reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "taxes_group1":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Розрахунок податків для 1 групи ФОП:\n"
            "- Єдиний податок: до 10% від прожиткового мінімуму станом на 1 січня поточного року.\n"
            "- ЄСВ (єдиний соціальний внесок): 22% від мінімальної заробітної плати станом на 1 січня.",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "taxes_group2":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Розрахунок податків для 2 групи ФОП:\n"
            "- Єдиний податок: до 20% від мінімальної заробітної плати станом на 1 січня поточного року.\n"
            "- ЄСВ (єдиний соціальний внесок): 22% від мінімальної заробітної плати станом на 1 січня.",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "taxes_group3":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Розрахунок податків для 3 групи ФОП:\n"
            "- Єдиний податок (без НДС): 5% від доходу.\n"
            "- Єдиний податок (з НДС): 3% від доходу + ПДВ (20%).\n"
            "- ЄСВ (єдиний соціальний внесок): 22% від мінімальної заробітної плати станом на 1 січня.",
            reply_markup=InlineKeyboardMarkup(keyboard))

        # Як вести облік?
    if data == "accounting":
        keyboard = [
            [InlineKeyboardButton("Книга обліку доходів", callback_data="accounting_book")],
            [InlineKeyboardButton("Автоматизація обліку", callback_data="accounting_automation")],
            [InlineKeyboardButton("Зберігання документів", callback_data="accounting_documents")],
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text("Оберіть аспект обліку:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "accounting_book":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Книга обліку доходів:\n"
            "- Для 1 і 2 груп обов'язковою є книга обліку доходів.\n"
            "- Записи ведуться щодня, фіксуються суми отриманих доходів.\n"
            "- Книгу можна вести як у паперовій, так і в електронній формі.",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "accounting_automation":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Автоматизація обліку:\n"
            "- Для обліку доходів та витрат використовуйте програми: Приват24, Liga:REPORT, МЕДОК.\n"
            "- Програми допомагають автоматизувати розрахунки податків, створення звітів.",
            reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "accounting_documents":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            "Зберігання документів:\n"
            "- Зберігайте копії всіх договорів, квитанцій, актів виконаних робіт.\n"
            "- Рекомендується використовувати хмарні сервіси для резервного копіювання документів.",
            reply_markup=InlineKeyboardMarkup(keyboard))

    if data == "main_menu":
        await start(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data == "help_search":
        await query.edit_message_text(
            "Введіть своє питання у чат, і бот спробує знайти відповідь.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")]])
        )
        context.user_data["awaiting_question"] = True

        # Обработка пользовательского вопроса
    if data == "help_what_is_fop":
        await query.edit_message_text(
            "ФОП – це фізична особа-підприємець, яка веде бізнес без створення юридичної особи.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")]])
        )
    elif data == "help_change_system":
        await query.edit_message_text(
            "Щоб змінити систему оподаткування, подайте заяву до податкової до кінця кварталу.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")]])
        )
    elif data == "help_filing_reports":
        await query.edit_message_text(
            "Звітність для ФОП подається в залежності від групи. Оберіть 'Звітність для ФОП' для деталей.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")]])
        )
    elif data == "help_calculate_taxes":
        await query.edit_message_text(
            "Податки розраховуються залежно від групи та системи. Перейдіть до 'Розрахунок податків' для деталей.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")]])
        )
    elif data == "help_accounting":
        await query.edit_message_text(
            "Для ведення обліку використовуйте книгу обліку доходів або спеціалізовані програми.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")]])
        )
    if data == "unswer_question":
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        context.user_data["answer_question"] = "group_question"
        await query.edit_message_text("Яка у Вас група підприємницької діяльності? ",
                                      reply_markup=InlineKeyboardMarkup(keyboard))


# Обработка текстовых сообщений
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    # Обработка пользовательских вопросов в цепочке
    if context.user_data.get("answer_question"):
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        if context.user_data["answer_question"] == "group_question":
            context.user_data["group"] = user_message
            context.user_data["answer_question"] = "tax_system_question"
            await update.message.reply_text("Яку маєте систему оподаткування?",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
        elif context.user_data["answer_question"] == "tax_system_question":
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]
            context.user_data["tax_system"] = user_message
            context.user_data["answer_question"] = "contact_question"
            await update.message.reply_text(
                "Введіть Ваші конт. данні: ім’я, тел., електр. адреса., та Ваше питання, яке маєте до нас, чи  на яке не знайшли відповідь",
                reply_markup=InlineKeyboardMarkup(keyboard))
        elif context.user_data["answer_question"] == "contact_question":
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]

            context.user_data["contact_info"] = user_message
            context.user_data["answer_question"] = None
            await update.message.reply_text(
                "Дякую за відповіді!Перевірте ще раз контактні данні. Ми обов'язково опрацюємо Ваші данні і ваше запитання! Ось ваші дані і запитання:\n"
                f"Група: {context.user_data['group']}\n"
                f"Система оподаткування: {context.user_data['tax_system']}\n"
                f"Контактні данні та запитання: {context.user_data['contact_info']}"
                , reply_markup=InlineKeyboardMarkup(keyboard))
        # return

        # Форматируем данные для отображения
        confirmation_messag = (
            "Дякую за відповіді!Перевірте ще раз контактні данні. Ми обов'язково опрацюємо Ваші данні і з Вами зв'яжимось! Ось ваші дані:\n"
            f"Група: {context.user_data['group']}\n"
            f"Система оподаткування: {context.user_data['tax_system']}\n"
            f"Контактні данні: {context.user_data['contact_info']}"
        )
        # Отправляем данные на email
        email_subject = "Нові контактні дані від клієнта"
        send_email(email_subject, confirmation_messag)

        # Обработка пользовательского вопроса
    if context.user_data.get("awaiting_question"):
        question = user_message.lower()
        if "фоп" in question:
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]
            await update.message.reply_text(
                "ФОП – це фізична особа-підприємець, яка веде бізнес без створення юридичної особи.Жду з нетерпінням наступного питання!!!",
                reply_markup=InlineKeyboardMarkup(keyboard))
        elif "система" in question:
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]
            await update.message.reply_text(
                "Щоб змінити систему оподаткування, подайте заяву до податкової до кінця кварталу.Жду з нетерпінням наступного питання!!!",
                reply_markup=InlineKeyboardMarkup(keyboard))
        elif "звітність" in question:
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]
            await update.message.reply_text(
                "Звітність для ФОП подається в залежності від групи. Оберіть 'Звітність для ФОП' для деталей.Жду з нетерпінням наступного питання!!!",
                reply_markup=InlineKeyboardMarkup(keyboard))
        elif "податки" in question:
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]
            await update.message.reply_text(
                "Податки розраховуються залежно від групи та системи. Перейдіть до 'Розрахунок податків' для деталей.Жду з нетерпінням наступного питання!!!",
                reply_markup=InlineKeyboardMarkup(keyboard))
        elif "облік" in question:
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]
            await update.message.reply_text(
                "Для ведення обліку використовуйте книгу обліку доходів або спеціалізовані програми.Жду з нетерпінням наступного питання!!!",
                reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            keyboard = [
                [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
            ]

            await update.message.reply_text(
                "Якщо ви не маєте до нас питань, чи вже відправили його на розгляд, то ігноруйте це повідомлення! а якщо не знайшли відповідь на ваше питання і не відправляли його , то Можете перейти до головного меню , далі у меню (Короткий опрос і Ваші питання), Заповніть контактні дані, і напишить Ваше питання, ми обов'язково його опрацюємо і дамо відповідь",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            context.user_data["awaiting_email"] = True
            context.user_data["awaiting_question"] = False
        return
    # Обработка ввода email
    if context.user_data.get("awaiting_email"):
        keyboard = [
            [InlineKeyboardButton("⬅️ До головного меню", callback_data="main_menu")],
        ]
        email_address = user_message
        context.user_data["email_address"] = email_address

        # Форматируем данные для отображения

        email_subject = "Контактні дані від клієнта"
        message = (
            "На жаль, я не знайшов відповідь на ваше питання. Ваше питання ми опрацюємо і відправимо відповідь.\n\n"
            f"Ось ваше питання:\n"
            f"Питання: {context.user_data.get('last_question', 'Невідоме')}\n"
            f"Електронна адреса: {email_address}\n"
        )

        await update.message.reply_text("Перейдіть у головне меню та задайте Ваше питання. Дякую!",
                                        reply_markup=InlineKeyboardMarkup(keyboard))
        context.user_data["awaiting_email"] = False
        context.user_data["awaiting_question"] = True

        return


# Инициализация приложения Telegram Bot
application = Application.builder().token(TOKEN).build()

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

# Маршрут для обработки вебхуков
@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработка входящих обновлений от Telegram."""
    data = request.json
    update = Update.de_json(data, application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# Маршрут для установки вебхука
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Устанавливает вебхук для бота."""
    response = application.bot.set_webhook(WEBHOOK_URL)
    if response:
        return f"Webhook установлен: {WEBHOOK_URL}", 200
    return "Не удалось установить webhook", 400

# Маршрут для проверки работоспособности
@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности приложения."""
    return "OK", 200

# Основной запуск приложения
if __name__ == "__main__":
    load_subscribers()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



