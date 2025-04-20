import os
import csv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from config import TELEGRAM_BOT_TOKEN
from utils import search_job_by_name, upload_file_to_job
from jobnimbus import generate_job_buttons

TOPIC_LOG_PATH = r"C:\Users\raean\Downloads\summary_bot\summary_bot\topic_log.csv"
pending_photos = {}  # key: chat_id or message_id, value: dict with file_url and file_name

def get_job_name_by_topic_id(thread_id):
    try:
        with open(TOPIC_LOG_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['topic_id']) == thread_id:
                    return row['job_name']
    except Exception as e:
        print(f"Error reading topic log: {e}")
    return None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.photo:
        return

    photo = message.photo[-1]
    file = await photo.get_file()

    print(f"🧪 file.file_path: {file.file_path}")

    file_url = (
        file.file_path if file.file_path.startswith("http")
        else f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file.file_path}"
    )
    file_name = f"{file.file_id}.jpg"
    caption = message.caption
    job_name = None

    # ✅ TOPIC FLOW (silent)
    if message.is_topic_message and message.message_thread_id:
        job_name = get_job_name_by_topic_id(message.message_thread_id)
        if job_name:
            jobs = search_job_by_name(job_name, exact=True)
            if jobs:
                job = jobs[0]
                result = upload_file_to_job(job['jnid'], file_url, file_name)
                print(f"📤 Uploaded to {job_name}: {result}")
        return

    # ✅ GROUP FLOW
    chat_id = message.chat.id

    if caption:
        job_name = caption.strip()
        jobs = search_job_by_name(job_name)
        if len(jobs) == 0:
            await message.reply_text(f"❌ No matching jobs found for: {job_name}")
        elif len(jobs) == 1:
            job = jobs[0]
            try:
                result = upload_file_to_job(job['jnid'], file_url, file_name)
                if result:
                    await message.reply_text(f"✅ Uploaded to **{job['name']}**", parse_mode="Markdown")
                else:
                    await message.reply_text(f"❌ Upload failed for **{job['name']}**. No result returned.")
            except Exception as e:
                print(f"❌ Upload error for job '{job['name']}': {e}")
                await message.reply_text(f"❌ Upload error for **{job['name']}**. Check console.")
        else:
            pending_photos[message.message_id] = {'file_url': file_url, 'file_name': file_name}
            await message.reply_text(
                "⚠️ Multiple jobs found — which one does this belong to?",
                reply_markup=generate_job_buttons(jobs)
            )
    else:
        pending_photos[chat_id] = {'file_url': file_url, 'file_name': file_name}
        await message.reply_text("📸 Photo received — which job does this go to?")

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat.id

    if chat_id not in pending_photos:
        return

    job_name = message.text.strip()
    jobs = search_job_by_name(job_name)
    file_info = pending_photos[chat_id]

    if len(jobs) == 0:
        await message.reply_text(f"❌ No matching jobs found for: {job_name}")
    elif len(jobs) == 1:
        job = jobs[0]
        try:
            result = upload_file_to_job(job['jnid'], file_info['file_url'], file_info['file_name'])
            if result:
                await message.reply_text(f"✅ Uploaded to **{job['name']}**", parse_mode="Markdown")
            else:
                await message.reply_text(f"❌ Upload failed for **{job['name']}**. No result returned.")
        except Exception as e:
            print(f"❌ Upload error: {e}")
            await message.reply_text("❌ Upload error. Check console.")
        del pending_photos[chat_id]
    else:
        pending_photos[chat_id] = file_info
        await message.reply_text(
            "⚠️ Multiple jobs found — please select one:",
            reply_markup=generate_job_buttons(jobs)
        )

async def handle_caption_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    edited = update.edited_message
    if not edited or not edited.caption or not edited.photo:
        return

    message_id = edited.message_id
    chat_id = edited.chat.id

    if message_id not in pending_photos:
        return

    job_name = edited.caption.strip()
    jobs = search_job_by_name(job_name)
    file_info = pending_photos[message_id]

    if len(jobs) == 0:
        await edited.reply_text(f"❌ No matching jobs found for: {job_name}")
    elif len(jobs) == 1:
        job = jobs[0]
        try:
            result = upload_file_to_job(job['jnid'], file_info['file_url'], file_info['file_name'])
            if result:
                await edited.reply_text(f"✅ Uploaded to **{job['name']}**", parse_mode="Markdown")
            else:
                await edited.reply_text(f"❌ Upload failed for **{job['name']}**. No result returned.")
        except Exception as e:
            print(f"❌ Upload error: {e}")
            await edited.reply_text("❌ Upload error. Check console.")
        del pending_photos[message_id]
    else:
        pending_photos[message_id] = file_info
        await edited.reply_text(
            "⚠️ Multiple jobs found — please select one:",
            reply_markup=generate_job_buttons(jobs)
        )

async def handle_job_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    message_id = query.message.reply_to_message.message_id if query.message.reply_to_message else None

    file_info = pending_photos.get(message_id) or pending_photos.get(chat_id)
    if not file_info:
        await query.edit_message_text("⚠️ No pending photo found.")
        return

    job_id = query.data.split(":")[1]
    try:
        result = upload_file_to_job(job_id, file_info['file_url'], file_info['file_name'])
        if result:
            await query.edit_message_text("✅ Photo uploaded successfully.")
        else:
            await query.edit_message_text("❌ Upload failed. No result returned.")
    except Exception as e:
        print(f"❌ Upload error (button): {e}")
        await query.edit_message_text("❌ Upload failed. Check the console.")

    if message_id in pending_photos:
        del pending_photos[message_id]
    elif chat_id in pending_photos:
        del pending_photos[chat_id]

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, handle_caption_edit))
    app.add_handler(CallbackQueryHandler(handle_job_selection))

    print("📸 Photo Bot is live and listening...")
    app.run_polling()

