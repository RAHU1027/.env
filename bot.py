import os
import asyncio
import httpx
from aiohttp import web
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler

# Credentials
TOKEN = "8744594607:AAGXRJnxQ_ylxbQO40sAQYigA5n1refYgY4"
API_KEY = "5b108bd2fdd31c0c34bc65f24a5216a0"
BASE_URL = "https://platfone.com/api/v1"
EMAIL_API = "https://www.1secmail.com/api/v1/"

# 1. Web Server (Render ke liye)
async def handle(request):
    return web.Response(text="Bot is running!")

async def run_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()

# 2. Email aur Number Logic
async def start(update, context):
    await update.message.reply_text("Swagat hai! /generate (Number) aur /email (Email) use karein.")

async def get_email(update, context):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{EMAIL_API}?action=genRandomMailbox&count=1")
        email = resp.json()[0]
        await update.message.reply_text(f"📧 Random Email: `{email}`")

async def get_number(update, context):
    await update.message.reply_text("⏳ Number generate ho raha hai...")
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"country_id": "us", "service_id": "ig"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/activation", json=payload, headers=headers)
        data = response.json()
        
        if "activation_id" not in data:
            await update.message.reply_text("❌ Error: Number nahi mila. Balance check karo.")
            return

        act_id, phone = data.get("activation_id"), data.get("phone")
        await update.message.reply_text(f"✅ Number: `{phone}`\nID: `{act_id}`\nWait for OTP...")
        
        for i in range(60): 
            await asyncio.sleep(2)
            res = await client.get(f"{BASE_URL}/activation/{act_id}", headers=headers)
            if res.json().get("sms_status") == "smsReceived":
                await update.message.reply_text(f"🎉 OTP Code: `{res.json().get('sms_code')}`")
                return
        await update.message.reply_text("❌ Timeout: SMS nahi aaya.")

# 3. Main Running
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", get_number))
    app.add_handler(CommandHandler("email", get_email))
    await app.run_polling()

async def main():
    await asyncio.gather(run_server(), run_bot())

if __name__ == '__main__':
    asyncio.run(main())
