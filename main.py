from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from io import BytesIO
from dotenv import load_dotenv
import os, requests

class Shinobi:
    def __init__(self, hostname, apikey, groupkey):
        self.hostname = hostname
        self.apikey = apikey
        self.groupkey = groupkey
        self.url = f"http://{hostname}/{apikey}/"
    
    def getMonitors(self):
        resp = requests.get(self.url + "monitor/" + self.groupkey)
        return resp.json()
        
    def getMonitorNames(self):
        names = []
        for m in self.getMonitors():
            names.append(m["name"])
        return names
    
    def getMonitorIdByName(self, name):
        monitors = self.getMonitors()
        for m in monitors:
            if m["name"] == name:
                return m["mid"]
        return ""
    
    def getSnapshot(self, monitorID):
        url = self.url + f"jpeg/{self.groupkey}/{monitorID}/s.jpg"
        resp = requests.get(url)
        return resp.content

class Bot:
    def __init__(self, shinobi, admins):
        self.shinobi = shinobi
        if type(admins) == str:
            self.admins = admins.split(",")
        elif type(admins) == list:
            self.admins = admins

    def getAdmins(self):
        x = []
        for a in self.admins:
            try:
                x.append(int(a))
            except:
                pass
        return x
    
    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user.id in self.getAdmins():
            await update.message.reply_text(f'Hello admin {update.effective_user.first_name}, {update.effective_message.text}')
        else:
            await update.message.reply_text(f'Hello {update.effective_user.first_name}')
    
    async def command_snapshot_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user.id not in self.getAdmins():
            await update.message.reply_text(f'You are not allowed to perform this action')
            return
        buttons = []
        for mon in self.shinobi.getMonitors():
            buttons.append(["/s " + mon["name"]])
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, selective=True)
        await update.message.reply_text("Please select a monitor", reply_markup=reply_markup)
    
    async def command_snapshot_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in self.getAdmins():
            await update.message.reply_text(f'You are not allowed to perform this action')
            return
        
        args = update.effective_message.text.split(" ")
        if len(args) < 2:
            await update.message.reply_text(f'Please specify a monitor!')
            return
        
        monitor_name = " ".join(args[1:])
        if monitor_name not in self.shinobi.getMonitorNames():
            await update.message.reply_text(f'Invalid monitor!')
            return
        
        monitor_id = self.shinobi.getMonitorIdByName(monitor_name)
        stream = BytesIO()
        stream.write(self.shinobi.getSnapshot(monitor_id))
        stream.seek(0)
        
        await update.message.reply_photo(stream)

def main():
    load_dotenv()
    SHINOBI_DOMAIN = os.environ["SHINOBI_DOMAIN"]
    SHINOBI_APIKEY = os.environ["SHINOBI_APIKEY"]
    SHINOBI_GROUPKEY = os.environ["SHINOBI_GROUPKEY"]
    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
    ADMINS = os.environ["ADMINS"]
    
    shinobi = Shinobi(SHINOBI_DOMAIN, SHINOBI_APIKEY, SHINOBI_GROUPKEY)
    bot = Bot(shinobi, ADMINS)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", bot.command_start))
    app.add_handler(CommandHandler("snapshot", bot.command_snapshot_start))
    app.add_handler(CommandHandler("s", bot.command_snapshot_callback))
    app.run_polling()

if __name__ == "__main__":
    main()