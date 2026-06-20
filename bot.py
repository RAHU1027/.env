import os
import asyncio
import httpx
from aiohttp import web
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Credentials (Jo aapne diye)
TOKEN = "8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4"
API_KEY = "5b108bd2fdd31c0c34bc65f24a5216a0"
BASE_URL = "https://platfone.com/api/v1"
EMAIL_API = "https://www.1secmail.com/api/v1/"

# --- Web Server (Uptime Fix) ---
async def handle(request):
    return web.Response(text="Bot is running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

# --- Bot Commands ---
async def setup_menu(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Bot shuru karein"),
        BotCommand("generate", "Naya Number lein"),
        BotCommand("email", "Nayi Email lein")
    ])

async def start(update, context):
    user = update.effective_user
    welcome = f"Namaste {user.first_name}! Main aapka Premium Bot hoon.\n/generate - Number ke liye\n/email - Email ke liye"
    await update.message.reply_text(welcome)

async def email(update, context):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{EMAIL_API}?action=genRandomMailbox&count=1")
        email = resp.json()[0]
        await update.message.reply_text(f"📧 Aapki Email: `{email}`")

async def generate(update, context):
    await update.message.reply_text("⏳ Number generate ho raha hai...")
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"country_id": "us", "service_id": "ig"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/activation", json=payload, headers=headers)
        data = response.json()
        
        if "activation_id" not in data:
            await update.message.reply_text("❌ Error: Number nahi mila. Platfone balance check karein.")
            return

        act_id, phone = data.get("activation_id"), data.get("phone")
        await update.message.reply_text(f"✅ Number: `{phone}`\nID: `{act_id}`\nSMS ka wait...")
        
        for i in range(60): 
            await asyncio.sleep(2)
            res = await client.get(f"{BASE_URL}/activation/{act_id}", headers=headers)
            if res.json().get("sms_status") == "smsReceived":
                await update.message.reply_text(f"🎉 OTP Code: `{res.json().get('sms_code')}`")
                return
        await update.message.reply_text("❌ Timeout: SMS nahi aaya.")

async def main():
    # 1. Web Server start karo (Render ke liye)
    await start_web_server()
    
    # 2. Bot start karo
    app = ApplicationBuilder().token(TOKEN).post_init(setup_menu).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("email", email))
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
