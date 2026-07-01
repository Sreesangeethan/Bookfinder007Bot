#update
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Legal Book Finder Bot\n\n"
        "Send a book title or author (English works best).\n"
        "Example: Pride and Prejudice"
    )

async def search_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if len(query) < 3:
        await update.message.reply_text("Please send a longer search term.")
        return

    await update.message.reply_text(f"🔍 Searching for '{query}'...")

    try:
        import requests
        # Added user-agent and longer timeout
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; BookBot/1.0)'}
        resp = requests.get(
            f"https://gutendex.com/books?search={query.replace(' ', '%20')}", 
            headers=headers,
            timeout=20
        )
        
        if resp.status_code != 200:
            await update.message.reply_text("External service temporarily unavailable.")
            return
            
        data = resp.json()
        
        found = False
        count = 0
        for book in data.get('results', []):
            if count >= 5: break
            formats = book.get('formats', {})
            link = (formats.get('application/epub+zip') or 
                    formats.get('text/plain; charset=utf-8') or 
                    formats.get('application/pdf') or 
                    next(iter(formats.values()), None))
            
            if link and 'gutenberg' in link.lower():
                author = ', '.join(a.get('name', 'Unknown') for a in book.get('authors', []))
                text = f"📖 **{book.get('title')}**\n👤 {author}\n🔗 [Download EPUB/PDF]({link})"
                await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)
                found = True
                count += 1
        if not found:
            await update.message.reply_text("No public domain results found.\nTry classic books like 'Sherlock Holmes' or 'Alice in Wonderland'.")
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Search failed due to network issue. Try again in a minute.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_book))
    
    print("✅ Bot started successfully!")
    app.run_polling()
