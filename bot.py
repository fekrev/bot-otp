import logging
import csv
import io
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Konfigurasi Log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# -------------------------------------------------------------
# KREDENSIAL & TARGET CHANNEL / GRUP
# -------------------------------------------------------------
BOT_TOKEN = "8861213863:AAFDs8QgfoNaVErEUANgq_xESOjw3vQ-Hmw"
TARGET_CHANNEL_ID = -1004448885063  # ID Channel/Grup Telegram kamu

THIRDWAVE_API_KEY = "YOUR_THIRDWAVE_API_KEY" # Tempel API Key Thirdwave kamu di sini
BASE_URL = "https://api.thirdwave.id" 
# -------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot OTP Thirdwave siap digunakan! Perintah: /numbers untuk cek nomor, /export untuk CSV."
    )

async def get_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {THIRDWAVE_API_KEY}"}
    try:
        response = requests.get(f"{BASE_URL}/api/numbers", headers=headers)
        if response.status_code == 200:
            data = response.json()
            msg = "Daftar Nomor:\n" + "\n".join([str(item) for item in data])
            
            # Kirim ke tempat perintah diketik (PC/Grup)
            await update.effective_chat.send_message(msg[:4000])
            
            # Kirim juga salinannya otomatis ke Channel/Grup Target
            try:
                await context.bot.send_message(chat_id=TARGET_CHANNEL_ID, text=f"📢 **[Laporan Nomor]**\n{msg[:4000]}")
            except Exception as channel_err:
                logging.error(f"Gagal kirim ke channel: {channel_err}")
        else:
            await update.effective_chat.send_message(f"Gagal mengambil data. Status: {response.status_code}")
    except Exception as e:
        await update.effective_chat.send_message(f"Terjadi kesalahan: {e}")

async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"Authorization": f"Bearer {THIRDWAVE_API_KEY}"}
    try:
        response = requests.get(f"{BASE_URL}/api/numbers", headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    writer.writerow(data[0].keys())
                    for item in data:
                        writer.writerow(item.values())
                else:
                    writer.writerow(["Number"])
                    for item in data:
                        writer.writerow([item])
            
            output.seek(0)
            file_bytes = output.getvalue().encode('utf-8')
            
            # Kirim file CSV ke tempat chat asal
            document = io.BytesIO(file_bytes)
            document.name = "export_numbers.csv"
            await update.effective_chat.send_document(document=document, filename="export_numbers.csv")
            
            # Kirim file CSV otomatis ke Channel/Grup Target
            try:
                channel_doc = io.BytesIO(file_bytes)
                channel_doc.name = "export_numbers.csv"
                await context.bot.send_document(
                    chat_id=TARGET_CHANNEL_ID, 
                    document=channel_doc, 
                    filename="export_numbers.csv",
                    caption="📢 **[Export Data CSV Baru]**"
                )
            except Exception as channel_err:
                logging.error(f"Gagal kirim CSV ke channel: {channel_err}")
                
        else:
            await update.effective_chat.send_message(f"Gagal export data. Status: {response.status_code}")
    except Exception as e:
        await update.effective_chat.send_message(f"Terjadi kesalahan saat export: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("numbers", get_numbers))
    app.add_handler(CommandHandler("export", export_csv))
    
    app.run_polling()
                
