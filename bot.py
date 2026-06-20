import asyncio
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Credentials
TOKEN = "8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4"
API_KEY = "5b108bd2fdd31c0c34bc65f24a5216a0"
BASE_URL = "https://platfone.com/api/v1"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot active hai! Number mangne ke liye /getnumber likhein.")

async def get_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    # Instagram service ke liye service_id check kar lena, maine yahan generic rakha hai
    payload = {"country_id": "us", "service_id": "instagram"}
    
    async with httpx.AsyncClient() as client:
        # Step 1: Number Request
        response = await client.post(f"{BASE_URL}/activation", json=payload, headers=headers)
        data = response.json()
        
        if "activation_id" not in data:
            await update.message.reply_text("Error: Number nahi mil saka. Shayad balance khatam hai.")
            return

        act_id = data.get("activation_id")
        phone = data.get("phone")
        
        await update.message.reply_text(f"✅ Number mil gaya: `{phone}`\nID: `{act_id}`\n\nSMS ka intezaar kar raha hoon...")
        
        # Step 2: SMS Polling
        for i in range(20): 
            await asyncio.sleep(10) # 10 second ka wait
            res = await client.get(f"{BASE_URL}/activation/{act_id}", headers=headers)
            res_data = res.json()
            
            if res_data.get("sms_status") == "smsReceived":
                await update.message.reply_text(f"🎉 Code mil gaya: `{res_data.get('sms_code')}`")
                return
                
        await update.message.reply_text("❌ Timeout: SMS nahi aaya.")

if __name__ == '__main__':
    # Bot start
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getnumber", get_number))
    app.run_polling()
