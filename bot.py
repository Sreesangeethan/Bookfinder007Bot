import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Logging (helpful for debugging on Render)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Legal Book Bot!\n\n"
        "Send me a book title or author.\n"
        "I search public domain & open sources only.\n"
        "Respect copyright!"
    )

async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if len(query) < 3:
        await update.message.reply_text("Please type a longer search term.")
        return

    await update.message.reply_text(f"🔍 Searching for '{query}' in legal sources...")

    try:
        import requests
        resp = requests.get(
            f"https://gutendex.com/books?search={query.replace(' ', '%20')}", 
            timeout=15
        )
        data = resp.json()
        
        found = False
        for book in data.get('results', [])[:6]:
            formats = book.get('formats', {})
            link = (formats.get('application/epub+zip') or 
                    formats.get('text/plain; charset=utf-8') or 
                    formats.get('application/pdf') or 
                    next(iter(formats.values()), None))
            
            if link:
                author = ', '.join(a.get('name', 'Unknown') for a in book.get('authors', []))
                text = f"📖 **{book.get('title')}**\n👤 {author}\n🔗 [Download]({link})"
                await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
                found = True
        if not found:
            await update.message.reply_text("No results found. Try classic/public domain books.")
    except Exception as e:
        await update.message.reply_text("Search failed. Please try again later.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_book))
    
    print("Bot is running...")
    app.run_polling()
