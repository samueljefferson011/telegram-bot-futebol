import requests
import datetime
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    JobQueue, CallbackContext
)

TELEGRAM_TOKEN = os.getenv('7558870387:AAFRVajR8Whb_4VSWJDxjg2U4NB5cNdrfxY')
API_FOOTBALL_KEY = os.getenv('90bd4520c7b53c0e60058cb6f3a96cea')
CHAT_ID = os.getenv(' 7923522312')
API_HOST = 'v3.football.api-sports.io'

def get_today_fixtures():
    today = datetime.date.today().isoformat()
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": today}
    headers = {
        "x-apisports-key": API_FOOTBALL_KEY,
        "x-rapidapi-host": API_HOST
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def get_match_stats(fixture_id):
    url = "https://v3.football.api-sports.io/fixtures/statistics"
    params = {"fixture": fixture_id}
    headers = {
        "x-apisports-key": API_FOOTBALL_KEY,
        "x-rapidapi-host": API_HOST
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

async def hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_today_fixtures()
    fixtures = data.get("response", [])

    if not fixtures:
        await update.message.reply_text("Nenhum jogo encontrado para hoje.")
        return

    msg = "\U0001F4C5 Jogos de hoje:\n"
    for fix in fixtures[:10]:
        fixture_id = fix['fixture']['id']
        home = fix['teams']['home']['name']
        away = fix['teams']['away']['name']
        msg += f"- {home} x {away} (ID: {fixture_id})\n"

    msg += "\nUse /analisar <ID> para ver a análise de um jogo."
    await update.message.reply_text(msg)

def gerar_analise(fixture_id):
    # Aqui você pode fazer chamadas reais para obter dados e gerar análise
    # Para exemplo, dados mock
    time1 = "Time A"
    time2 = "Time B"
    gols1 = 1.6
    gols2 = 1.4
    cartoes1 = 2.3
    cartoes2 = 2.1
    escanteios1 = 5.8
    escanteios2 = 4.7

    msg = f"\U0001F50D Análise: {time1} x {time2}\n\n"
    msg += f"\u26bd Gols esperados:\n- {time1}: {gols1} (Chance +1.5: {min(100, int((gols1 / 2.5) * 100))}%)\n"
    msg += f"- {time2}: {gols2} (Chance +1.5: {min(100, int((gols2 / 2.5) * 100))}%)\n\n"
    msg += f"🔪 Cartões esperados:\n- {time1}: {cartoes1}\n- {time2}: {cartoes2}\n\n"
    msg += f"🚩 Escanteios esperados:\n- {time1}: {escanteios1} (Chance +4.5: {min(100, int((escanteios1 / 6) * 100))}%)\n"
    msg += f"- {time2}: {escanteios2} (Chance +4.5: {min(100, int((escanteios2 / 6) * 100))}%)\n\n"

    if gols1 + gols2 > 2.8:
        sugestao = "Mais de 1.5 gols no jogo"
        chance = int(((gols1 + gols2) / 2.5) * 100)
    elif escanteios1 + escanteios2 > 10:
        sugestao = "Mais de 9.5 escanteios no jogo"
        chance = int(((escanteios1 + escanteios2) / 12) * 100)
    else:
        sugestao = "Jogo com menos de 3.5 gols"
        chance = 60

    msg += f"💡 Sugestão de aposta:\n{sugestao} (Chance: {chance}%)"
    return msg

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use o comando assim: /analisar <ID do jogo>")
        return

    fixture_id = context.args[0]
    msg = gerar_analise(fixture_id)
    await update.message.reply_text(msg)

async def auto_analise(context: CallbackContext):
    chat_id = CHAT_ID
    data = get_today_fixtures()
    fixtures = data.get("response", [])

    if not fixtures:
        await context.bot.send_message(chat_id=chat_id, text="Nenhum jogo encontrado para hoje.")
        return

    for fix in fixtures[:3]:
        fixture_id = fix['fixture']['id']
        msg = gerar_analise(fixture_id)
        await context.bot.send_message(chat_id=chat_id, text=msg)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("analisar", analisar))
    app.add_handler(CommandHandler("hoje", hoje))

    job_queue = app.job_queue
    job_queue.run_daily(auto_analise, time=datetime.time(hour=11, minute=0, second=0))

    app.run_polling()

if __name__ == '__main__':
    main()
