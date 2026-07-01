import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Legal Book Bot\nSend a book title or author (e.g. Pride and Prejudice).")

async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if len(query) < 3:
        await update.message.reply_text("Query too short.")
        return

    await update.message.reply_text(f"🔍 Searching '{query}'...")

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(
            f"https://gutendex.com/books?search={query.replace(' ', '%20')}",
            headers=headers,
            timeout=20
        )
        
        logging.info(f"Status code: {resp.status_code}")
        
        if resp.status_code != 200:
            await update.message.reply_text(f"Service error ({resp.status_code}). Try again later.")
            return

        data = resp.json()
        found = False
        for book in data.get('results', [])[:5]:
            formats = book.get('formats', {})
            link = next((url for url in formats.values() if url), None)
            if link:
                author = ', '.join(a.get('name', 'Unknown') for a in book.get('authors', []))
                text = f"**{book.get('title')}**\n{author}\n[Download]({link})"
                await update.message.reply_text(text, parse_mode='Markdown')
                found = True
        if not found:
            await update.message.reply_text("No public domain results. Try classic books.")
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        await update.message.reply_text("Search failed due to network issue. Try again.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_book))
    
    print("✅ Bot started!")
    app.run_polling()
