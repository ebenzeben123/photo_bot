from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def generate_job_buttons(jobs):
    buttons = []
    for job in jobs:
        job_name = job.get("name", "Unnamed Job")
        job_id = job.get("jnid") or job.get("id")  # fallback if jnid missing
        buttons.append([InlineKeyboardButton(job_name, callback_data=f"job:{job_id}")])
    return InlineKeyboardMarkup(buttons)
