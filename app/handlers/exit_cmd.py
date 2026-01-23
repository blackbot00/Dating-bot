from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import banned_guard
from app.services.match_service import end_chat
from app.services.queue_service import remove_from_queue
from app.services.user_service import set_ai_prefs
from app.keyboard import choose_again_kb


async def exit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await banned_guard(update, context):
        return

    uid = update.effective_user.id

    # stop AI mode
    set_ai_prefs(uid, ai_mode=False)

    # remove from queue
    remove_from_queue(uid)

    # end human chat if any
    chat = end_chat(uid)

    if chat:
        partner_id = chat["user2"] if chat["user1"] == uid else chat["user1"]
        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text="✅ Partner left🚶🏼\n\nChoose again:",
                reply_markup=choose_again_kb()
            )
        except:
            pass

    await update.message.reply_text(
        "✅ Conversation stopped.\n\nChoose again:",
        reply_markup=choose_again_kb()
  )
