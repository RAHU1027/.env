import asyncio
import httpx
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Credentials jo tumne diye
TOKEN = "8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4"
API_KEY = "5b108bd2fdd31c0c34bc65f24a5216a0"
BASE_URL = "https://platfone.com/api/v1"
EMAIL_API = "https://www.1secmail.com/api/v1/"

# Button Menu
KEYBOARD = [['Get Email', 'Get Number']]
MARKUP = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Swagat hai! Neeche diye gaye buttons use karein:", reply_markup=MARKUP)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == 'Get Email':
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{EMAIL_API}?action=genRandomMailbox&count=1")
            email = resp.json()[0]
            await update.message.reply_text(f"📧 Aapki Email: `{email}`")

    elif text == 'Get Number':
        headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
        payload = {"country_id": "us", "service_id": "ig"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BASE_URL}/activation", json=payload, headers=headers)
            data = response.json()
            
            if "activation_id" not in data:
                await update.message.reply_text("Error: Number nahi mil raha, balance check karo.")
                return

            act_id = data.get("activation_id")
            phone = data.get("phone")
            await update.message.reply_text(f"✅ Number: `{phone}`\nID: `{act_id}`\nSMS ka wait kar raha hoon...")
            
            # Fast Polling (1 second interval)
            for i in range(60): 
                await asyncio.sleep(1) # 1 second interval for fast OTP
                res = await client.get(f"{BASE_URL}/activation/{act_id}", headers=headers)
                res_data = res.json()
                
                if res_data.get("sms_status") == "smsReceived":
                    await update.message.reply_text(f"🎉 OTP Code: `{res_data.get('sms_code')}`")
                    return
            await update.message.reply_text("❌ Timeout: SMS nahi aaya.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    app.run_polling()
