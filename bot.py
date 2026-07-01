import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Legal Book Bot\nSend a book title or author.")

async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if len(query) < 3:
        await update.message.reply_text("Query too short.")
        return

    await update.message.reply_text(f"🔍 Searching '{query}'...")

    try:
        import requests
        headers = {'User-Agent': 'BookBot/1.0'}
        resp = requests.get(f"https://gutendex.com/books?search={query.replace(' ', '%20')}", headers=headers, timeout=15)
        data = resp.json()

        found = False
        for book in data.get('results', [])[:5]:
            formats = book.get('formats', {})
            link = next((url for url in formats.values() if url), None)
            if link:
                author = ', '.join(a.get('name', '') for a in book.get('authors', []))
                text = f"**{book.get('title')}**\n{author}\n[Download]({link})"
                await update.message.reply_text(text, parse_mode='Markdown')
                found = True
        if not found:
            await update.message.reply_text("No results found.")
    except:
        await update.message.reply_text("Search failed. Try again.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_book))
    
    print("✅ Bot started successfully!")
    
    # Use webhook for Render
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://bookfinder007bot.onrender.com/{BOT_TOKEN}"
    )
