import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token'ını environment variables'tan al
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    # Hoş geldin mesajı
    await update.message.reply_text(f"Merhaba {user_name}! Ben saat botuyum 🕐")
    
    # Ses dosyası gönder (eğer hazırsa)
    try:
        await update.message.reply_voice(
            voice=open('assets/hosgeldin.ogg', 'rb'),
            caption="Hoş geldiniz! Size özel mesajlar göndereceğim."
        )
    except Exception as e:
        logger.error(f"Ses dosyası gönderilemedi: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    user_id = update.effective_user.id
    
    logger.info(f"Kullanıcı {user_id} mesajı: {user_message}")
    
    # Basit analiz
    if any(word in user_message for word in ['uyku', 'uyuyam', 'gece']):
        await update.message.reply_voice(
            voice=open('assets/uyku.ogg', 'rb'),
            caption="Uyku problemi mi yaşıyorsun? 🛌"
        )
    elif any(word in user_message for word in ['merhaba', 'selam', 'hey']):
        await update.message.reply_voice(
            voice=open('assets/selam.ogg', 'rb'),
            caption="Sana da merhaba! 👋"
        )

async def send_scheduled_message(context: ContextTypes.DEFAULT_TYPE):
    """Zamanlanmış mesajları gönder"""
    job_data = context.job.data
    user_id = job_data['user_id']
    
    try:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        
        if current_time == "02:30":
            await context.bot.send_voice(
                chat_id=user_id,
                voice=open('assets/gece_mesaji.ogg', 'rb'),
                caption="Saat 02:30! Hala uyanık mısın? 🌙"
            )
            
    except Exception as e:
        logger.error(f"Zamanlanmış mesaj gönderilemedi: {e}")

async def setup_scheduler(application):
    """Scheduler'ı kur"""
    scheduler = AsyncIOScheduler()
    
    # Her gün 02:30'da çalışacak job
    scheduler.add_job(
        send_scheduled_message_to_all,
        CronTrigger(hour=2, minute=30),
        args=[application]
    )
    
    scheduler.start()
    return scheduler

async def send_scheduled_message_to_all(application):
    """Tüm kullanıcılara mesaj gönder"""
    # Burada veritabanından kullanıcıları çekmen gerekir
    # Şimdilik örnek olarak:
    users = [123456789]  # Gerçek kullanıcı ID'leri
    
    for user_id in users:
        try:
            await application.bot.send_voice(
                chat_id=user_id,
                voice=open('assets/gece_mesaji.ogg', 'rb'),
                caption="Saat 02:30! Neden hala uyanıksın? 💫"
            )
        except Exception as e:
            logger.error(f"Kullanıcı {user_id} için mesaj gönderilemedi: {e}")

def main():
    # Bot uygulamasını oluştur
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Scheduler'ı kur
    application.job_queue.scheduler = application.job_queue.scheduler or AsyncIOScheduler()
    application.job_queue.scheduler.add_job(
        send_scheduled_message_to_all,
        CronTrigger(hour=2, minute=30),
        args=[application]
    )
    application.job_queue.scheduler.start()
    
    # Botu başlat
    application.run_polling()
    logger.info("Bot başlatıldı!")

if __name__ == '__main__':
    main()
