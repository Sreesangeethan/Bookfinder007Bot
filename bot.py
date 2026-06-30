import os
import telebot
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")  # We'll set this on Render

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Legal Book Bot\nSend title or author.\nRespect copyright!")


@bot.message_handler(func=lambda m: True)
def search(message):
    query = message.text.strip()
    if len(query) < 3:
        return bot.reply_to(message, "Query too short.")

    bot.reply_to(message, f"🔍 Searching '{query}'...")

    try:
        resp = requests.get(f"https://gutendex.com/books?search={query.replace(' ', '%20')}", timeout=10)
        data = resp.json()

        sent = False
        for book in data.get('results', [])[:8]:
            formats = book.get('formats', {})
            link = (formats.get('application/epub+zip') or
                    formats.get('text/plain; charset=utf-8') or
                    list(formats.values())[0] if formats else None)

            if link:
                author = ', '.join(a.get('name', '') for a in book.get('authors', []))
                text = f"**{book.get('title')}**\n{author}\n[Download]({link})"
                bot.send_message(message.chat.id, text, parse_mode='Markdown')
                sent = True
        if not sent:
            bot.reply_to(message, "No results found in public domain sources.")
    except:
        bot.reply_to(message, "Search failed. Try again.")


print("Bot started successfully!")
bot.infinity_polling()