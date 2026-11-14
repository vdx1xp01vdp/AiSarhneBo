import os, logging, io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from groq import Groq
from gtts import gTTS

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
client = Groq(api_key=os.getenv("GROQ_KEY"))

OWNER = "مهند محمد مصباح عبد المقصود حسن"
SIGN = f"\n\n━━━━━━━━━━━━\n👑 صُنع بكل حب بواسطة:\n{OWNER}\n━━━━━━━━━━━━"

MODES = {
    "kid": "اشرح لطفل 10 سنين، بالمصري، أمثلة كرتون، ايموجي كتير",
    "school": "اشرح كمدرس ثانوي محترف، تعريف + مثال + ملخص + سؤال امتحان، بالمصري",
    "summary": "لخص في 5 نقط فقط، بالمصري",
    "exam": "اعمل امتحان 5 اسئلة اختياري + الاجابات في الاخر",
    "image": "اوصف صورة توضيحية للدرس ده بالتفصيل، كأنك بترسمها",
}

def kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧒 طفل", callback_data="kid"), InlineKeyboardButton("🎓 ثانوي", callback_data="school")],
        [InlineKeyboardButton("⚡ تلخيص", callback_data="summary"), InlineKeyboardButton("📝 امتحان", callback_data="exam")],
        [InlineKeyboardButton("🎨 تخيل صورة", callback_data="image"), InlineKeyboardButton("🔊 صوتي تشغيل/ايقاف", callback_data="voice")],
        [InlineKeyboardButton("🧠 ذاكرتي", callback_data="memory"), InlineKeyboardButton("👑 مين عملني؟", callback_data="owner")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "school"
    context.user_data["voice"] = False
    context.user_data["history"] = []
    await update.message.reply_text(
        "👑 أهلاً بيك في **أيسارنبو ULTRA** 👑\n\n"
        "أفخم بوت شرح في التاريخ.\n"
        "✅ بيفتكرك ✅ بيشرح صوتي ✅ بيعمل امتحان\n\n"
        f"💎 البوت ده من صنع:\n**{OWNER}**\n\n"
        "اختار الوضع وابعت أي سؤال 👇",
        reply_markup=kb(), parse_mode="Markdown"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👑 أيسارنبو ULTRA\n\nصُنع بكل حب بواسطة:\n{OWNER}\n\nفكرة وتصميم وتنفيذ: مهند ❤️")

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "voice":
        context.user_data["voice"] = not context.user_data.get("voice", False)
        s = "اشتغل 🔊" if context.user_data["voice"] else "وقف 🔇"
        await q.edit_message_text(f"الشرح الصوتي: {s}", reply_markup=kb())
        return
    if q.data == "memory":
        h = context.user_data.get("history", [])
        txt = "🧠 ذاكرتك:\n" + "\n".join(h[-5:]) if h else "لسه مفيش حاجة"
        await q.edit_message_text(txt, reply_markup=kb())
        return
    if q.data == "owner":
        await q.edit_message_text(f"👑 البوت ده من صنع:\n{OWNER}\n\nفخر الصناعة المصرية ❤️🇪🇬", reply_markup=kb())
        return
    context.user_data["mode"] = q.data
    await q.edit_message_text(f"تمام ✅ اخترت: {q.data}\n\nابعت سؤالك 👇", reply_markup=kb())

async def explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode", "school")
    text = update.message.text
    history = context.user_data.get("history", [])
    history.append(text)
    context.user_data["history"] = history[-10:]
    msg = await update.message.reply_text("بجهزلك شرح ULTRA... 👑⏳")
    try:
        res = client.chat.completions.create(model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content": f"انت أيسارنبو ULTRA، من صنع {OWNER}. {MODES[mode]}. بالمصري، ايموجي، تنسيق فخم."},
                      {"role":"user","content": text}], temperature=0.7, max_tokens=1500)
        ans = res.choices[0].message.content + SIGN
        await msg.edit_text(ans, reply_markup=kb())
        if context.user_data.get("voice"):
            tts = gTTS(text=res.choices[0].message.content[:1000], lang='ar')
            buf = io.BytesIO(); tts.write_to_fp(buf); buf.seek(0)
            await update.message.reply_voice(voice=buf)
    except:
        await msg.edit_text("حصل مشكلة، جرب تاني 🙏")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, explain))
    print("ULTRA Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
