# filepath: server.py
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from typing import Dict, Any
from flask import Flask, request

# --- Flask app for keeping the bot alive on Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/_health')
def health():
    return "OK"

# --- Environment Setup ---

# --- Logging Configuration ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Security ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "7577992673:AAFwhaTnguPIZNLRsjEvKOHeluHmYZdN7Mc")
if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# --- Constants ---
SUPPORTED_LANGUAGES = ['tj', 'ru', 'en']
DEFAULT_LANGUAGE = 'en'
ADMIN_USERNAME = "@admin_furughi_donish"
SUPPORT_EMAIL = "support@furughi-donish.tj"
WEBSITE_URL = "https://furughi-donish.tj"

# --- Database Simulation ---
# In a production environment, replace with a real database connection
user_data_db: Dict[int, Dict[str, Any]] = {}

# --- Multilingual Content ---
TEXTS = {
    'tj': {
        'start': "👋 Салом, {name}! Ба боти расмии <b>Фуруги Дониш</b> хуш омадед!\n\nМо як платформаи таълимӣ бо имконоти зиёд барои муаллимон ва донишҷӯён мебошем.",
        'help': "🆘 <b>Роҳнамои корбарӣ</b>\n\n/start - Оғози бот\n/help - Роҳнамо\n/about - Дар бораи лоиҳа\n/feedback - Фикру пешниҳодҳо\n/language - Иваз кардани забони интерфейс\n\nБарои маълумоти бештар тугмаҳои зерро истифода баред.",
        'about': "🎓 <b>Фуруги Дониш</b> — лоиҳаи таълимии инноватсионӣ барои мустаҳкам кардани фарованди таълим дар Тоҷикистон.\n\n<b>Мақсадҳо:</b>\n• Таъмин кардани воситаҳои муосир барои омӯзиш\n• Эҷоди фазои иҷтимоӣ барои мубодилаи илмӣ\n• Дастгирии ижодиёни илмӣ\n\n<b>Ҳадафҳо:</b>\n• 10,000 корбари фаъол то охири соли 2025\n• 5,000 манбаъи илмӣ дар китобхона\n• 100% дастгирии техникӣ",
        'services': "🔧 <b>Хидматҳои мо</b>:\n\n• 📚 <b>Китобхонаи рақамӣ</b> бо зиёда аз 1,000 китоб ва мақола\n• 💬 <b>Платформаи саволу ҷавоб</b> бо дастгирии AI\n• 🤖 <b>Ассистенти ақли сунъӣ</b> барои кӯмак дар вазифаҳо\n• 📂 <b>Системаи идоракунии курсҳо</b>\n• 🎥 <b>Видёо-дарсҳо</b> аз беҳтарин муаллимон\n• 📊 <b>Аналитикаи пешрафт</b> барои донишҷӯён",
        'teachers': "👨‍🏫 <b>Барои муаллимон</b>:\n\n• Тайёр кардани тестҳо, презентатсияҳо ва вазифаҳо\n• Назорати фаъолияти донишҷӯён бо графикҳои тафсилӣ\n• Тақсимоти автоматии омӯзишгоҳҳо\n• Эҷоди курсҳои шахсӣ\n• Платформаи мубодилаи таҷриба\n• Дастгирии техникӣ 24/7",
        'students': "🎓 <b>Барои донишҷӯён</b>:\n\n• Дастрасӣ ба ҳамаи манбаъҳо дар як ҷо\n• Ҷавобҳои фаврии ба саволҳо\n• Омӯзиши интерактивӣ бо AI\n• Назорати пешрафти шахсӣ\n• Имтиҳонҳои модели\n• Гурӯҳҳои таҳсилӣ",
        'contact': f"📬 <b>Тамос бо дастгоҳ</b>\n\n• Админ: {ADMIN_USERNAME}\n• Почтаи электронӣ: {SUPPORT_EMAIL}\n• Сомона: {WEBSITE_URL}\n• Работое время: 08:00-20:00 (Dushanbe time)\n\nБарои саволҳои зудҷавоб пайваст шавед ба админ.",
        'feedback': "✍️ Лутфан фикру пешниҳодҳои худро дар бораи хидматҳои мо нависед. Мо ҳамаи фикрҳоро бо эҳтиром меомӯзем ва барои такмили хидматҳо истифода мебарем.",
        'language': "🌐 Забони интерфейсро интихоб кунед:",
        'back': "⬅️ Бозгашт",
        'error': "❌ Хатои система. Лутфан баъдтар аз нав кӯшиш кунед ё бо дастгоҳ тамос гиред.",
        'feedback_received': "✅ Фикри шумо қабул шуд! Ташаккур барои кӯмаки шумо.",
        'unauthorized': "⛔ Дастрасии маҳдуд. Шумо иҷозати ин амалро надоред."
    },
    'ru': {
        'start': "👋 Здравствуйте, {name}! Добро пожаловать в официального бота <b>Furugi Donish</b>!\n\nМы образовательная платформа с широкими возможностями для учителей и студентов.",
        'help': "🆘 <b>Справка</b>\n\n/start - Начать работу\n/help - Помощь\n/about - О проекте\n/feedback - Оставить отзыв\n/language - Изменить язык интерфейса\n\nДля получения дополнительной информации используйте кнопки ниже.",
        'about': "🎓 <b>Furugi Donish</b> — инновационный образовательный проект для улучшения учебного процесса в Таджикистане.\n\n<b>Цели:</b>\n• Предоставление современных инструментов обучения\n• Создание научного сообщества\n• Поддержка творческих инициатив\n\n<b>Задачи:</b>\n• 10,000 активных пользователей к концу 2025\n• 5,000 образовательных ресурсов в библиотеке\n• 100% техническая поддержка",
        'services': "🔧 <b>Наши услуги</b>:\n\n• 📚 <b>Цифровая библиотека</b> с более чем 1,000 книг и статей\n• 💬 <b>Платформа вопросов и ответов</b> с поддержкой ИИ\n• 🤖 <b>ИИ-ассистент</b> для помощи с заданиями\n• 📂 <b>Система управления курсами</b>\n• 🎥 <b>Видеоуроки</b> от лучших преподавателей\n• 📊 <b>Аналитика успеваемости</b> для студентов",
        'teachers': "👨‍🏫 <b>Для учителей</b>:\n\n• Создание тестов, презентаций и заданий\n• Мониторинг активности студентов с детальной статистикой\n• Автоматическое распределение уроков\n• Создание персональных курсов\n• Платформа обмена опытом\n• Круглосуточная техническая поддержка",
        'students': "🎓 <b>Для студентов</b>:\n\n• Доступ ко всем ресурсам в одном месте\n• Мгновенные ответы на вопросы\n• Интерактивное обучение с ИИ\n• Персональный трекинг прогресса\n• Пробные тесты\n• Учебные группы",
        'contact': f"📬 <b>Контактная информация</b>\n\n• Админ: {ADMIN_USERNAME}\n• Эл. почта: {SUPPORT_EMAIL}\n• Сайт: {WEBSITE_URL}\n• Часы работы: 08:00-20:00 (Душанбе)\n\nДля срочных вопросов свяжитесь с админом.",
        'feedback': "✍️ Пожалуйста, напишите ваш отзыв о наших услугах. Мы ценим все мнения и используем их для улучшения сервиса.",
        'language': "🌐 Выберите язык интерфейса:",
        'back': "⬅️ Назад",
        'error': "❌ Системная ошибка. Пожалуйста, попробуйте позже или свяжитесь с поддержкой.",
        'feedback_received': "✅ Ваш отзыв получен! Спасибо за вашу помощь.",
        'unauthorized': "⛔ Доступ ограничен. У вас нет прав для этого действия."
    },
    'en': {
        'start': "👋 Hello, {name}! Welcome to the official <b>Furugi Donish</b> bot!\n\nWe are an educational platform with extensive features for teachers and students.",
        'help': "🆘 <b>Help Guide</b>\n\n/start - Start the bot\n/help - Show help\n/about - About the project\n/feedback - Provide feedback\n/language - Change interface language\n\nFor more information, use the buttons below.",
        'about': "🎓 <b>Furugi Donish</b> is an innovative educational project aimed at enhancing the learning process in Tajikistan.\n\n<b>Goals:</b>\n• Providing modern learning tools\n• Creating a scientific community\n• Supporting creative initiatives\n\n<b>Targets:</b>\n• 10,000 active users by end of 2025\n• 5,000 educational resources in library\n• 100% technical support coverage",
        'services': "🔧 <b>Our Services</b>:\n\n• 📚 <b>Digital library</b> with 1,000+ books and articles\n• 💬 <b>Q&A platform</b> with AI support\n• 🤖 <b>AI assistant</b> for homework help\n• 📂 <b>Course management system</b>\n• 🎥 <b>Video lessons</b> from top teachers\n• 📊 <b>Progress analytics</b> for students",
        'teachers': "👨‍🏫 <b>For Teachers</b>:\n\n• Create tests, presentations and assignments\n• Monitor student activity with detailed stats\n• Automatically distribute lessons\n• Create personal courses\n• Experience sharing platform\n• 24/7 technical support",
        'students': "🎓 <b>For Students</b>:\n\n• Access all resources in one place\n• Get instant answers to questions\n• Interactive learning with AI\n• Personal progress tracking\n• Practice tests\n• Study groups",
        'contact': f"📬 <b>Contact Information</b>\n\n• Admin: {ADMIN_USERNAME}\n• Email: {SUPPORT_EMAIL}\n• Website: {WEBSITE_URL}\n• Working hours: 08:00-20:00 (Dushanbe time)\n\nFor urgent questions, contact the admin.",
        'feedback': "✍️ Please write your feedback about our services. We value all opinions and use them to improve our service.",
        'language': "🌐 Choose interface language:",
        'back': "⬅️ Back",
        'error': "❌ System error. Please try again later or contact support.",
        'feedback_received': "✅ Your feedback has been received! Thank you for your help.",
        'unauthorized': "⛔ Access restricted. You don't have permission for this action."
    }
}

# --- Utility Functions ---
def get_user_language(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    """Get user's preferred language from context or database."""
    if context.user_data.get('lang'):
        return context.user_data['lang']
    if user_id in user_data_db and 'lang' in user_data_db[user_id]:
        return user_data_db[user_id]['lang']
    return DEFAULT_LANGUAGE

def save_user_language(user_id: int, language: str):
    """Save user's language preference to database."""
    if user_id not in user_data_db:
        user_data_db[user_id] = {}
    user_data_db[user_id]['lang'] = language

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and main menu."""
    try:
        user = update.effective_user
        lang = get_user_language(context, user.id)
        
        # Log user start
        logger.info(f"User {user.id} ({user.full_name}) started the bot")

        text = TEXTS[lang]['start'].format(name=user.first_name)

        keyboard = [
            [
                InlineKeyboardButton("🇹🇯 TJ", callback_data='lang_tj'),
                InlineKeyboardButton("🇷🇺 RU", callback_data='lang_ru'),
                InlineKeyboardButton("🇬🇧 EN", callback_data='lang_en')
            ],
            [
                InlineKeyboardButton("ℹ️ " + TEXTS[lang]['about'].split('\n')[0][4:17], callback_data='about'),
                InlineKeyboardButton("📚 " + TEXTS[lang]['services'].split('\n')[0][4:17], callback_data='services')
            ],
            [
                InlineKeyboardButton("👨‍🏫 " + TEXTS[lang]['teachers'].split('\n')[0][4:17], callback_data='teachers'),
                InlineKeyboardButton("🎓 " + TEXTS[lang]['students'].split('\n')[0][4:17], callback_data='students')
            ],
            [
                InlineKeyboardButton("📬 " + TEXTS[lang]['contact'].split('\n')[0][4:17], callback_data='contact'),
                InlineKeyboardButton("✍️ Feedback", callback_data='feedback')
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await handle_error(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help information."""
    try:
        user = update.effective_user
        lang = get_user_language(context, user.id)
        
        keyboard = [[InlineKeyboardButton(TEXTS[lang]['back'], callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(TEXTS[lang]['help'], reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in help handler: {e}")
        await handle_error(update, context)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send information about the project."""
    try:
        user = update.effective_user
        lang = get_user_language(context, user.id)
        
        keyboard = [[InlineKeyboardButton(TEXTS[lang]['back'], callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(TEXTS[lang]['about'], reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in about handler: {e}")
        await handle_error(update, context)

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle feedback command."""
    try:
        user = update.effective_user
        lang = get_user_language(context, user.id)
        
        context.user_data['awaiting_feedback'] = True
        keyboard = [[InlineKeyboardButton(TEXTS[lang]['back'], callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(TEXTS[lang]['feedback'], reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in feedback handler: {e}")
        await handle_error(update, context)

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection command."""
    try:
        user = update.effective_user
        lang = get_user_language(context, user.id)
        
        keyboard = [
            [
                InlineKeyboardButton("🇹🇯 Тоҷикӣ", callback_data='lang_tj'),
                InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
                InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')
            ],
            [InlineKeyboardButton(TEXTS[lang]['back'], callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(TEXTS[lang]['language'], reply_markup=reply_markup, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in language handler: {e}")
        await handle_error(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    try:
        user = update.effective_user
        lang = get_user_language(context, user.id)
        
        if context.user_data.get('awaiting_feedback'):
            # Process feedback
            feedback = update.message.text
            logger.info(f"Feedback from user {user.id}: {feedback}")
            
            # Here you would typically save feedback to database or send to admin
            # For now, we'll just log it and confirm receipt
            
            context.user_data['awaiting_feedback'] = False
            await update.message.reply_text(TEXTS[lang]['feedback_received'], parse_mode='HTML')
            
            # Return to main menu
            await start(update, context)
        else:
            # Handle other messages
            await update.message.reply_text(
                TEXTS[lang]['help'],
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        await handle_error(update, context)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    try:
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        lang = get_user_language(context, user.id)
        
        if query.data.startswith('lang_'):
            # Language selection
            new_lang = query.data.split('_')[1]
            context.user_data['lang'] = new_lang
            save_user_language(user.id, new_lang)
            logger.info(f"User {user.id} changed language to {new_lang}")
            await start(update, context)
            
        elif query.data in ['about', 'services', 'teachers', 'students', 'contact', 'feedback']:
            # Content sections
            text = TEXTS[lang][query.data]
            keyboard = [[InlineKeyboardButton(TEXTS[lang]['back'], callback_data='back')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
            
        elif query.data == 'back':
            # Back to main menu
            await start(update, context)
            
    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        await handle_error(update, context)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors gracefully."""
    try:
        user = update.effective_user
        lang = get_user_language(context, user.id if user else None)
        
        error_message = TEXTS[lang]['error']
        
        if update.message:
            await update.message.reply_text(error_message, parse_mode='HTML')
        elif update.callback_query:
            await update.callback_query.edit_message_text(error_message, parse_mode='HTML')
            
        logger.error(f"Error handled for user {user.id if user else 'unknown'}")
    except Exception as e:
        logger.critical(f"Critical error in error handler: {e}")

# --- Main Function ---
def main():
    """Start the bot."""
    try:
        # Create the Application
        application = Application.builder().token(TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("feedback", feedback_command))
        application.add_handler(CommandHandler("language", language_command))
        
        # Add button handler
        application.add_handler(CallbackQueryHandler(button_click))
        
        # Add message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        application.add_error_handler(handle_error)

        # Start the Bot using webhook if URL is configured, otherwise use polling
        logger.info("Starting bot...")
        
        if WEBHOOK_URL:
            # Set webhook
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
            )
            logger.info(f"Bot started with webhook on port {PORT}")
        else:
            # Start polling
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("Bot started with polling")
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    # Run Flask app in development
    if os.environ.get("ENVIRONMENT") == "development":
        main()
    else:
        # For production on Render, run the bot in a separate thread
        import threading
        bot_thread = threading.Thread(target=main)
        bot_thread.start()
        
        # Start Flask app
        app.run(host="0.0.0.0", port=PORT)
