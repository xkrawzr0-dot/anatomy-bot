import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# --- Anatomy Question Bank (English) ---
QUESTIONS = [
    {
        "question": "Which anatomical term describes the head area?",
        "options": ["Cervical", "Cephalic", "Thoracic", "Axillary"],
        "answer": 1,
    },
    {
        "question": "Which of the following terms represents the armpit area?",
        "options": ["Axillary", "Brachial", "Acromial", "Antebrachial"],
        "answer": 0,
    },
    {
        "question": (
            "What does the directional term 'Posterior (dorsal)' mean?"
        ),
        "options": [
            "Toward the front of the body",
            "Toward the back of the body",
            "Toward the head",
            "Toward the side",
        ],
        "answer": 1,
    },
    {
        "question": (
            "The term that describes a position farther from the point of"
            " attachment to the trunk is:"
        ),
        "options": ["Proximal", "Distal", "Superficial", "Lateral"],
        "answer": 1,
    },
    {
        "question": (
            "What is the plane that vertically divides the body or an organ"
            " into right and left parts?"
        ),
        "options": [
            "Sagittal plane",
            "Coronal plane",
            "Transverse plane",
            "Frontal plane",
        ],
        "answer": 0,
    },
    {
        "question": "The coronal plane is also known as the:",
        "options": [
            "Sagittal plane",
            "Transverse plane",
            "Frontal plane",
            "Axial plane",
        ],
        "answer": 2,
    },
    {
        "question": (
            "The plane that horizontally divides the body into upper and lower"
            " portions, also known as the axial plane, is the:"
        ),
        "options": [
            "Transverse plane",
            "Coronal plane",
            "Sagittal plane",
            "Midsagittal plane",
        ],
        "answer": 0,
    },
    {
        "question": "What does the regional term 'Patellar' refer to?",
        "options": [
            "Anterior knee area",
            "Posterior knee area",
            "Thigh area",
            "Foot area",
        ],
        "answer": 0,
    },
]

# Dictionary to track each user's session independently
user_sessions = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id

  # Copy and shuffle questions randomly for each user session
  user_questions = QUESTIONS.copy()
  random.shuffle(user_questions)

  user_sessions[user_id] = {
      "questions": user_questions,
      "question_index": 0,
      "score": 0,
  }

  await update.message.reply_text(
      "Welcome to the Anatomy Quiz! 🧠📚\n"
      "Get ready, the questions are randomized. Let's start with the first"
      " question:"
  )
  await send_question(update, context, user_id)


async def send_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
):
  session = user_sessions[user_id]
  q_index = session["question_index"]
  questions_list = session["questions"]

  if q_index < len(questions_list):
    q_data = questions_list[q_index]
    keyboard = [
        [InlineKeyboardButton(option, callback_data=f"ans_{i}")]
        for i, option in enumerate(q_data["options"])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    target = update.message if update.message else update.callback_query.message
    await target.reply_text(q_data["question"], reply_markup=reply_markup)
  else:
    score = session["score"]
    total = len(questions_list)
    target = update.message if update.message else update.callback_query.message
    await target.reply_text(
        f"🎉 Quiz Completed!\n\nYour final score is: **{score}** out of"
        f" **{total}** 🏆\nThank you for participating. To take the quiz"
        " again, send the /start command"
    )
    if user_id in user_sessions:
      del user_sessions[user_id]


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  user_id = update.effective_user.id
  if user_id not in user_sessions:
    await query.message.reply_text(
        "The quiz session has ended or the bot was restarted. Send /start to"
        " begin a new quiz."
    )
    return

  session = user_sessions[user_id]
  q_index = session["question_index"]
  q_data = session["questions"][q_index]

  selected_option = int(query.data.split("_")[1])

  if selected_option == q_data["answer"]:
    session["score"] += 1
    feedback = "✅ Correct answer!"
  else:
    correct_text = q_data["options"][q_data["answer"]]
    feedback = f"❌ Incorrect answer.\nThe correct answer is: *{correct_text}*"

  await query.message.reply_text(feedback, parse_mode="Markdown")

  session["question_index"] += 1
  await send_question(update, context, user_id)


def main():
  TOKEN = "9121368812:AAH_y5dzO1F7NPC1JSz2ohnud14sobMvuyY"

  application = ApplicationBuilder().token(TOKEN).build()

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CallbackQueryHandler(button_handler))

  print("Bot is running successfully... Press Ctrl+C to stop.")
  application.run_polling()


if __name__ == "__main__":
  main()