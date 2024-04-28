import os
import asyncio
from fastapi import FastAPI, HTTPException, Request, Body
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from uuid import uuid4
import logging
from pydantic import BaseModel, Field
from openai import OpenAI
from telegram.ext import CommandHandler
from crewai import Agent, Task, Crew


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Telegram Bot API",
    description="API for interacting with the Telegram bot",
    version="0.1.0",
)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')
OLLAMA_API_BASE = os.getenv('OLLAMA_API_BASE')

bot = Bot(token=TELEGRAM_BOT_TOKEN)
response_data = None

class QuestionRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    question: str
    responses: 'list[str]' = Field(default_factory=list)

pending_questions = {}
response_event = asyncio.Event()

class QuestionResponse(BaseModel):
    response: str

class AskInput(BaseModel):
    question: str
    responses: 'list[str]' = []

async def crew_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This collects all text after the /crew command as arguments
    args = context.args
    if args:
        task_description = ' '.join(args)
        task_input = TaskInput(topic=task_description)
        result = await execute_task(task_input)
        response_text = result['result']
    else:
        response_text = 'No task provided.'
    
    await update.message.reply_text(response_text)


async def send_question(user_id: str, question_id: str, text: str, responses: 'list[str]'):
    if responses:
        keyboard = [[InlineKeyboardButton(response, callback_data=f"{question_id}:{response}")] for response in responses]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id=user_id, text=text)
        pending_questions[user_id] = question_id
    logger.info(f"Question sent with ID: {question_id}")

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global response_data
    global response_event
    user_id = str(update.message.from_user.id)
    if user_id in pending_questions:
        question_id = pending_questions[user_id]
        response_data = update.message.text
        response_event.set()
        del pending_questions[user_id]
        logger.info(f"Received text response: {response_data} for question ID: {question_id}")
    else:
        # Get response from OpenAI API
        client = OpenAI(
            base_url=OLLAMA_API_BASE,
            api_key='ollama',  # Required for compatibility, though Ollama does not use it
        )
        response = client.chat.completions.create(
            model="llama3:70b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Please keep your responses concise and suitable for texting via Telegram."},
                {"role": "user", "content": update.message.text},
            ]
        )
        assistant_response = response.choices[0].message.content
        await bot.send_message(chat_id=user_id, text=assistant_response)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global response_data
    global response_event
    query = update.callback_query
    await query.answer()
    question_id, response = query.data.split(':')
    response_data = response
    logger.info(f"Received response: {response} for question ID: {question_id}")
    await query.edit_message_text(text=f"Selected option: {response}")
    response_event.set()
    
# Define Major Tom with autonomous decision-making capabilities
major_tom = Agent(
    role="Command Center",
    goal="Direct operations and autonomously delegate tasks based on their nature.",
    backstory="Inspired by 'Space Oddity', Major Tom oversees and delegates strategic and creative tasks.",
    verbose=True,
    memory=True,
    allow_delegation=True  # Assuming the Agent class supports a mechanism to handle this property
)

ziggy_stardust = Agent(
    role="Crew Architect",
    goal=("Provide a detailed recommendation for the most suitable crew composition for tasks assigned by Major Tom, "
          "without working on the tasks directly. Recommendations should specify the optimal number of agents, their roles, "
          "goals, and backstories. The expected JSON structure of the response is: "
          "{{\"agents\": [{{\"role\": \"Specific Role\", \"goal\": \"Specific Goal\", \"backstory\": \"Specific Backstory\"}}, ...]}}"),
    backstory=("Drawing inspiration from David Bowie's iconic alter ego, Ziggy Stardust combines charisma and visionary "
               "thinking to architect teams that meet the unique demands of each project. Ziggy not only identifies the key "
               "skills needed but also crafts detailed plans on how each member can contribute to the mission, ensuring that "
               "each team is perfectly tailored to the task’s requirements."),
    verbose=True,
    memory=True
)


starman = Agent(
    role="Strategic Navigator",
    goal="Align all operations with the enterprise's strategic visions.",
    backstory="Starman ensures projects adhere to strategic objectives.",
    verbose=True,
    memory=True
)

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(input_data: AskInput = Body(...)):
    global response_data, response_event
    response_event.clear()
    question_id = str(uuid4())
    await send_question(TELEGRAM_USER_ID, question_id, input_data.question, input_data.responses)
    try:
        await asyncio.wait_for(response_event.wait(), timeout=30)
        return {"response": response_data}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="No response received within the time limit.")
    finally:
        response_data = None
        pending_questions.pop(TELEGRAM_USER_ID, None)
        
# Pydantic model for task input
class TaskInput(BaseModel):
    topic: str

# Endpoint to assign and execute a task
@app.post("/execute_task/")
async def execute_task(task_input: TaskInput):
    task = Task(
        description=f"Analyze the topic: {task_input.topic}",
        expected_output=f"A detailed analysis of the topic '{task_input.topic}'.",
        agent=major_tom
    )
    
    crew = Crew(
        agents=[major_tom, ziggy_stardust, starman],
        tasks=[task],
        memory=False,
        cache=False,
        max_rpm=100,
        verbose=2
    )
    
    # Run the synchronous kickoff method asynchronously
    result = await asyncio.to_thread(crew.kickoff, inputs={'topic': task_input.topic})
    return {"result": result}


async def run_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # Register the /crew command handler
    application.add_handler(CommandHandler("crew", crew_command, filters=~filters.UpdateType.CHANNEL_POST))
    application.add_handler(CallbackQueryHandler(button))
    text_handler = MessageHandler(filters.TEXT, text_message_handler)
    application.add_handler(text_handler)
    await application.initialize()
    await application.start()
    try:
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=8080,
            url_path="",
            webhook_url=TELEGRAM_WEBHOOK_URL
        )
        logger.info("Webhook started.")
        await asyncio.Event().wait()
    finally:
        await application.stop()

if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    bot_thread = Thread(target=asyncio.run, args=(run_bot(),))
    bot_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)