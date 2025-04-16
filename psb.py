from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import time
from datetime import datetime
import logging
import requests
import random
from random import randint
import os
import json

intensity_shock = 0
duration_shock = 0
intensity_vibrate = 0
duration_vibrate = 0
duration_beep = 0
mode_random = 0
duration_random = 0
intensity_random = 0
time2 = datetime.now()
current_time = time2.strftime("%H:%M:%S")
admin_id = "YOUR_CHATID_HERE"
remove_id = 0
IsUserAllowed = 0

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
logging.basicConfig(filename='logs.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the welcome message"""
    await update.message.reply_text('Hi!\nWelcome to that poorly written PiShock bot!\nPlease note that this bot is only for use on @YOURUSERNAME !\nBe kind and do not use this bot without authorisation from myself!\nDo /help to get commands!')

async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "No username"
    first_name = update.effective_user.first_name or "No first name"
    
    await update.message.reply_text(
        f"Here's your chat ID information:\n\n"
        f"User ID: `{user_id}`\n"
        f"Send this ID to @YOURUSERNAME to get whitelisted.",
        parse_mode='Markdown'
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """The ✨help command ✨"""
    chat_id = update.message.chat_id
    username = update.message.chat.username

    config = load_config()

    is_whitelisted = str(chat_id) in config['whitelist']
    is_privileged = str(chat_id) in config['privileged_whitelist']
    is_admin = chat_id == admin_id

    help_message = f"Hello, {username}!\n\n"

    if not is_whitelisted:
        help_message += "You are not whitelisted. No commands will be shown."
    elif is_whitelisted and not is_privileged:
        help_message += "Available commands for normal users (whitelisted):\n"
        help_message += "/shock [Intensity] [Duration] - Send a shock with limits for normal users.\n"
        help_message += "/vibrate [Intensity] [Duration] - Send a vibration with limits for normal users.\n"
        help_message += "/gradualrandom - Send random shocks/vibrations with normal user limits.\n"
    elif is_privileged:
        help_message += "Available commands for privileged users (including whitelisted):\n"
        help_message += "/shock [Intensity] [Duration] - Send a shock with limits for privileged users.\n"
        help_message += "/vibrate [Intensity] [Duration] - Send a vibration with limits for privileged users.\n"
        help_message += "/gradualrandom - Send random shocks/vibrations with privileged user limits.\n"
        help_message += "/hiddenvibrate - Send a hidden vibration (privileged users only).\n"
        help_message += "/hiddenshock - Send a hidden shock (privileged users only).\n"
    if is_admin:
        help_message += "Admin commands (all available commands):\n"
        help_message += "/setlimits - Set shock and vibration limits for normal and privileged users.\n"
        help_message += "/adduser [ChatID] [whitelist/privileged] - Add a user to the whitelist or privileged list.\n"
        help_message += "/removeuser [ChatID] - Remove a user from the whitelist or privileged list.\n"
        help_message += "/setapikey [APIKEY] - Set the API key.\n"
        help_message += "/setuserkey [USERKEY] - Set the user key.\n"
        help_message += "/setusername [USERNAME] - Set the username.\n"
        help_message += "/showlist - Show the whitelisted users.\n"
        help_message += "/getconfig - Get the current configuration.\n"

    await update.message.reply_text(help_message)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def load_config(file_path="config.json"): 
    """Load configuration from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def save_config(config, file_path="config.json"): 
    """Save configuration to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

def check_user(chat_id, config): 
    """Check if a user is in the whitelist or privileged whitelist."""
    chat_id_str = str(chat_id)
    is_whitelisted = chat_id_str in config.get("whitelist", [])
    is_privileged = chat_id_str in config.get("privileged_whitelist", [])
    return is_whitelisted, is_privileged

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to add someone to the whitelist"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:  
        try:
            add_id = update.message.text.split(" ")[1]  
            list_type = update.message.text.split(" ")[2].lower()  
        except IndexError:
            await update.message.reply_text("Incorrect command! Use: /adduser [ChatID] [whitelist/privileged]")
            return
        
        config = load_config()

        if list_type not in ["whitelist", "privileged"]:
            await update.message.reply_text("Incorrect command! Use: 'whitelist' or 'privileged'.")
            return
        key = "whitelist" if list_type == "whitelist" else "privileged_whitelist"
        if str(add_id) in config[key]:
            await update.message.reply_text(f"This ChatID is already in the {list_type} list!")
        else:
            config[key].append(str(add_id))  
            save_config(config)  
            await update.message.reply_text(f"ChatID `{add_id}` has been added to the {list_type}!")
            print(f"Chat ID {add_id} has been added to the {list_type}.")
    else:
        await update.message.reply_text("You aren't allowed to use this command!")

async def setlimits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sets limits for shock/vibration mode, and normal/privileged users."""
    chat_id = update.message.chat_id
    if chat_id == admin_id: 
        try:
            mode = update.message.text.split(" ")[1].lower()  
            user_type = update.message.text.split(" ")[2].lower()  
            max_intensity = int(update.message.text.split(" ")[3])  
            max_duration = int(update.message.text.split(" ")[4])  
        except IndexError:
            await update.message.reply_text("Incorrect command! Usage: /setlimits [shock/vibrate] [normal/privileged] [max_intensity] [max_duration]")
            return
        except ValueError:
            await update.message.reply_text("Intensity and duration must be integers!")
            return
        config = load_config()
        if mode not in ["shock", "vibrate"]:
            await update.message.reply_text("Invalid mode! Use 'shock' or 'vibrate'.")
            return
        if user_type not in ["normal", "privileged"]:
            await update.message.reply_text("Invalid user type! Use 'normal' or 'privileged'.")
            return
        if max_intensity > 100:
            max_intensity = 100
        if max_duration > 15:
            max_duration = 15
        if mode == "shock":
            if user_type == "normal":
                config["shock_limits"]["normal"]["max_intensity"] = max_intensity
                config["shock_limits"]["normal"]["max_duration"] = max_duration
            else:
                config["shock_limits"]["privileged"]["max_intensity"] = max_intensity
                config["shock_limits"]["privileged"]["max_duration"] = max_duration
        elif mode == "vibrate":
            if user_type == "normal":
                config["vibrate_limits"]["normal"]["max_intensity"] = max_intensity
                config["vibrate_limits"]["normal"]["max_duration"] = max_duration
            else:
                config["vibrate_limits"]["privileged"]["max_intensity"] = max_intensity
                config["vibrate_limits"]["privileged"]["max_duration"] = max_duration
        save_config(config)
        await update.message.reply_text(f"Successfully updated the {mode} limits for {user_type} users: "
                                  f"Max intensity = {max_intensity}, Max duration = {max_duration} seconds.")
        print(f"Admin updated {mode} limits for {user_type} users: Max intensity = {max_intensity}, Max duration = {max_duration} seconds.")
    else:
        await update.message.reply_text("You are not authorized to use this command!")

async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to remove someone from the whitelist"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:  
        try:
            remove_id = update.message.text.split(" ")[1]  
        except IndexError:
            await update.message.reply_text("Incorrect command! Use: /removeuser [ChatID]")
            return
        config = load_config()

        removed_from = []  
        if remove_id in config["whitelist"]:
            config["whitelist"].remove(remove_id)
            removed_from.append("whitelist")
        if remove_id in config["privileged_whitelist"]:
            config["privileged_whitelist"].remove(remove_id)
            removed_from.append("privileged whitelist")
        if removed_from:
            save_config(config)  
            await update.message.reply_text(
                f"ChatID `{remove_id}` has been removed from: {', '.join(removed_from)}."
            )
            print(f"Chat ID {remove_id} has been removed from: {', '.join(removed_from)}.")
        else:
            await update.message.reply_text(f"ChatID `{remove_id}` was not found in any list.")
            print(f"Chat ID {remove_id} was not found in any list.")
    else:
        await update.message.reply_text("You aren't allowed to use this command!")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to send the log.txt file"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:
        if os.path.exists('log.txt'):
            with open('log.txt', 'rb') as log:
                await context.bot.send_document(chat_id, log)
        else:
            with open('log.txt', 'x'):
                await update.message.reply_text("The log file didn't exist! It has just been created, though.")
    if chat_id != admin_id:
        await update.message.reply_text(f"You aren't allowed to use this command!")
        
async def clearlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to clear the log.txt file"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:
        with open('log.txt', 'w') as logc:
            logc.write("")
            logc.write('[' + current_time + '] ' f'logfile has been cleared by ChatID {chat_id}\n')
            await update.message.reply_text("Log file has been cleared!")
    if chat_id != admin_id:
        await update.message.reply_text(f"You aren't allowed to use this command!")
            
async def set_apikey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to set the API key in the POST requests"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:
        try:
            new_apikey = update.message.text.split(" ")[1]
        except IndexError:
            await update.message.reply_text("Incorrect command! Use: /set_apikey [new_apikey]")
            return
        with open("config.json", 'r') as f:
            config = json.load(f)
    
        config["apikey"] = new_apikey
        with open("config.json", 'w') as f:
            json.dump(config, f, indent=4)
        await update.message.reply_text(f"API key has been updated to: {new_apikey}")
        print(f"API key has been updated to: {new_apikey}")
    else:
        await update.message.reply_text("You aren't allowed to use this command!")

async def set_userkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to set the Userkey in the POST requests"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:
        try:
            new_userkey = update.message.text.split(" ")[1]  
        except IndexError:
            await update.message.reply_text("Incorrect command! Use: /set_userkey [new_userkey]")
            return
        with open("config.json", 'r') as f:
            config = json.load(f)
        config["userkey"] = new_userkey
        with open("config.json", 'w') as f:
            json.dump(config, f, indent=4)
        await update.message.reply_text(f"User key has been updated to: {new_userkey}")
        print(f"User key has been updated to: {new_userkey}")
    else:
        await update.message.reply_text("You aren't allowed to use this command!")

async def set_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to set the username in the POST requests"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:
        try:
            new_username = update.message.text.split(" ")[1]  
        except IndexError:
            await update.message.reply_text("Incorrect command! Use: /set_username [new_username]")
            return
        with open("config.json", 'r') as f:
            config = json.load(f)
        config["username"] = new_username
        with open("config.json", 'w') as f:
            json.dump(config, f, indent=4)
        await update.message.reply_text(f"Username has been updated to: {new_username}")
        print(f"Username has been updated to: {new_username}")
    else:
        await update.message.reply_text("You aren't allowed to use this command!")

async def showlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to show the ChatIDs in the whitelist and privileged whitelist"""
    chat_id = update.message.chat_id
    if chat_id == admin_id:
        with open("config.json", 'r') as f:
            config = json.load(f)
        whitelist_users = config.get("whitelist", [])
        privileged_users = config.get("privileged_whitelist", [])
        response = "Users in Whitelist:\n"
        if not whitelist_users:
            response += "No users in the whitelist.\n"
        else:
            for user in whitelist_users:
                response += f"- {user}\n"
        
        response += "\nUsers in Privileged Whitelist:\n"
        if not privileged_users:
            response += "No users in the privileged whitelist.\n"
        else:
            for user in privileged_users:
                response += f"- {user}\n"
        
        await update.message.reply_text(response)
        print(f"Admin requested to view the whitelist and privileged whitelist.")
    else:
        await update.message.reply_text("You aren't allowed to use this command!")

async def getconfig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the configuration settings for whitelisted and privileged users"""
    chat_id = update.message.chat_id
    username = update.message.chat.username
    try:
        config = load_config()
    except Exception as e:
        await update.message.reply_text(f"Error loading config: {e}")
        return
    if chat_id != admin_id:
        await update.message.reply_text("You are not authorized to view the configuration.")
        return
    required_keys = ['shock_limits', 'vibrate_limits', 'apikey', 'userkey', 'username']
    if not all(key in config for key in required_keys):
        await update.message.reply_text("The configuration file is missing required fields.")
        return
    config_message = f"Current Configuration:\n\n"
    config_message += f"Shock Mode Limits (Normal Users):\n"
    config_message += f"Intensity: 0-{config['shock_limits']['normal']['max_intensity']}%\n"
    config_message += f"Duration: 0-{config['shock_limits']['normal']['max_duration']} seconds\n\n"
    config_message += f"Shock Mode Limits (Privileged Users):\n"
    config_message += f"Intensity: 0-{config['shock_limits']['privileged']['max_intensity']}%\n"
    config_message += f"Duration: 0-{config['shock_limits']['privileged']['max_duration']} seconds\n\n"

    config_message += f"Vibrate Mode Limits (Normal Users):\n"
    config_message += f"Intensity: 0-{config['vibrate_limits']['normal']['max_intensity']}%\n"
    config_message += f"Duration: 0-{config['vibrate_limits']['normal']['max_duration']} seconds\n\n"
    config_message += f"Vibrate Mode Limits (Privileged Users):\n"
    config_message += f"Intensity: 0-{config['vibrate_limits']['privileged']['max_intensity']}%\n"
    config_message += f"Duration: 0-{config['vibrate_limits']['privileged']['max_duration']} seconds\n\n"

    config_message += f"API Key: {config['apikey']}\n"
    config_message += f"User Key: {config['userkey']}\n"
    config_message += f"Username: {config['username']}\n"

    await update.message.reply_text(config_message)

async def shock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a shock and logs it to the logfile"""
    chat_id = update.message.chat_id
    username = update.message.chat.username
    with open("config.json", 'r') as f:
        config = json.load(f)
    apikey = config.get('apikey')
    userkeyapi = config.get('userkey')
    usernameapi = config.get('username')
    if not all([apikey, userkeyapi, usernameapi]):
        await update.message.reply_text('API keys are not properly configured!')
        print(f'{username} tried sending a shock but API keys are missing.')
        return
    is_whitelisted, is_privileged = check_user(chat_id, config)

    if not is_whitelisted:
        await update.message.reply_text('Unauthorized user! If you think this is a mistake, please contact @HypnoJuno.')
        print(f'User {username} ({chat_id}) tried issuing a command but was not allowed.')
        return
    try:
        intensity_shock = int(update.message.text.split(" ")[1])
        duration_shock = int(update.message.text.split(" ")[2])
    except (IndexError, ValueError):
        await update.message.reply_text('Incorrect command! Correct usage is /shock [Intensity 1-100] [Duration 1-15]')
        return
    if intensity_shock < 1 or intensity_shock > 100 or duration_shock < 1 or duration_shock > 15:
        await update.message.reply_text('Incorrect command! Correct usage is /shock [Intensity 1-100] [Duration 1-15]')
        print(f'{username} tried sending a shock with invalid values: {intensity_shock}% for {duration_shock} seconds.')
        return
    response = requests.post('https://do.pishock.com/api/apioperate', json={
        "Username": usernameapi,
        "Name": username,
        "Code": userkeyapi,
        "Intensity": intensity_shock,
        "Duration": duration_shock,
        "Apikey": apikey,
        "Op": "0"
    })

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    with open('log.txt', 'a') as f:
        if is_privileged:
            await update.message.reply_text(f'You have sent a privileged shock with {intensity_shock}% intensity for {duration_shock} seconds!')
            print(f'{username} sent privileged shock with {intensity_shock}% intensity for {duration_shock} seconds.')
            f.write(f'[{current_time}] {username} sent privileged shock with {intensity_shock}% intensity for {duration_shock} seconds.\n')
        else:
            await update.message.reply_text(f'Sent a shock with {intensity_shock}% intensity for {duration_shock} seconds!')
            print(f'{username} sent a shock with {intensity_shock}% intensity for {duration_shock} seconds.')
            f.write(f'[{current_time}] {username} sent a shock with {intensity_shock}% intensity for {duration_shock} seconds.\n')

async def hiddenshock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a shock without logging it to the logfile"""
    chat_id = update.message.chat_id
    username = update.message.chat.username
    with open("config.json", 'r') as f:
        config = json.load(f)
    _, is_privileged = check_user(chat_id, config)

    if not is_privileged:
        await update.message.reply_text('Unauthorized user! Only privileged users can execute this command.')
        print(f'User {username} ({chat_id}) tried issuing a hidden shock command but was not allowed.')
        return
    intensity_shock = int(update.message.text.split(" ")[1])
    duration_shock = int(update.message.text.split(" ")[2])
    if intensity_shock >= 101 or intensity_shock <= 0 or duration_shock >= 16 or duration_shock <= 0:
        await update.message.reply_text('Incorrect command! Correct usage is /hiddenshock [Intensity 1-100] [Duration 1-15]')
        print(f'{username} tried sending a hidden shock with invalid values: {intensity_shock}% for {duration_shock} seconds.')
        return
    with open('log.txt', 'a') as f:
        f.write(f'[{current_time}] {username} sent a hidden shock for {duration_shock} seconds.\n')
    await update.message.reply_text(f'You sent a hidden shock for {duration_shock} seconds!')
    print(f'{username} sent a hidden shock for {duration_shock} seconds.')

async def vibrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a vibration and logs it to the logfile"""
    chat_id = update.message.chat_id
    username = update.message.chat.username
    with open("config.json", 'r') as f:
        config = json.load(f)
    is_whitelisted, is_privileged = check_user(chat_id, config)

    if not is_whitelisted:
        await update.message.reply_text('Unauthorized user! If you think this is a mistake, please contact @HypnoJuno.')
        print(f'User {username} ({chat_id}) tried issuing a command but was not allowed.')
        return
    try:
        intensity_vibrate = int(update.message.text.split(" ")[1])
        duration_vibrate = int(update.message.text.split(" ")[2])
    except (IndexError, ValueError):
        await update.message.reply_text('Incorrect command! Correct usage is /vibrate [Intensity 1-100] [Duration 1-15]')
        return
    if intensity_vibrate < 1 or intensity_vibrate > 100 or duration_vibrate < 1 or duration_vibrate > 15:
        await update.message.reply_text('Incorrect command! Correct usage is /vibrate [Intensity 1-100] [Duration 1-15]')
        print(f'{username} tried sending a vibration with invalid values: {intensity_vibrate}% for {duration_vibrate} seconds.')
        return
    apikey = config.get('apikey')
    userkeyapi = config.get('userkey')
    usernameapi = config.get('username')
    if not all([apikey, userkeyapi, usernameapi]):
        await update.message.reply_text('API keys are not properly configured!')
        print(f'{username} tried sending a vibration but API keys are missing.')
        return
    response = requests.post('https://do.pishock.com/api/apioperate', json={
        "Username": usernameapi,
        "Name": username,
        "Code": userkeyapi,
        "Intensity": intensity_vibrate,
        "Duration": duration_vibrate,
        "Apikey": apikey,
        "Op": "1"
    })
    if is_privileged:
        await update.message.reply_text(f'You have sent a privileged vibration with {intensity_vibrate}% intensity for {duration_vibrate} seconds!')
        print(f'{username} sent privileged vibration with {intensity_vibrate}% intensity for {duration_vibrate} seconds.')
        with open('log.txt', 'a') as f:
            f.write(f'[{current_time}] {username} sent privileged vibration with {intensity_vibrate}% intensity for {duration_vibrate} seconds.\n')
    else:
        await update.message.reply_text(f'Sent a vibration with {intensity_vibrate}% intensity for {duration_vibrate} seconds!')
        print(f'{username} sent a vibration with {intensity_vibrate}% intensity for {duration_vibrate} seconds.')
        with open('log.txt', 'a') as f:
            f.write(f'[{current_time}] {username} sent a vibration with {intensity_vibrate}% intensity for {duration_vibrate} seconds.\n')

async def hiddenvibrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a vibration without logging it to the logfile"""
    chat_id = update.message.chat_id
    username = update.message.chat.username
    with open("config.json", 'r') as f:
        config = json.load(f)
    _, is_privileged = check_user(chat_id, config)

    if not is_privileged:
        await update.message.reply_text('Unauthorized user! Only privileged users can execute this command.')
        print(f'User {username} ({chat_id}) tried issuing a hidden vibrate command but was not allowed.')
        return
    intensity_vibrate = int(update.message.text.split(" ")[1])
    duration_vibrate = int(update.message.text.split(" ")[2])
    if intensity_vibrate >= 101 or intensity_vibrate <= 0 or duration_vibrate >= 16 or duration_vibrate <= 0:
        await update.message.reply_text('Incorrect command! Correct usage is /hiddenvibrate [Intensity 1-100] [Duration 1-15]')
        print(f'{username} tried sending a hidden vibration with invalid values: {intensity_vibrate}% for {duration_vibrate} seconds.')
        return
    with open('log.txt', 'a') as f:
        f.write(f'[{current_time}] {username} sent a hidden vibration for {duration_vibrate} seconds.\n')
    await update.message.reply_text(f'You sent a hidden vibration for {duration_vibrate} seconds!')
    print(f'{username} sent a hidden vibration for {duration_vibrate} seconds.')

async def gradualrandom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends 3 shocks or vibrations, with higher intensity and longer duration each shock/vibration"""
    chat_id = update.message.chat_id
    username = update.message.chat.username
    config = load_config()
    if str(chat_id) not in config['privileged_whitelist']:
        await update.message.reply_text("Unauthorised user! You are not on the privileged list! If you think this is a mistake, please contact @HypnoJuno")
        print(f"User {username} ({chat_id}) tried issuing a command but was not allowed.")
        return
    mode_random = random.randint(0, 1)
    duration_random1 = random.randint(0, 9)
    intensity_random1 = random.randint(0, 50)
    apikey = config.get('apikey')
    userkeyapi = config.get('userkey')
    usernameapi = config.get('username')
    a = duration_random1
    b = intensity_random1
    amount_of_zaps = 0

    while amount_of_zaps <= 2:
        amount_of_zaps += 1
        response = requests.post('https://do.pishock.com/api/apioperate', json={
            "Username": usernameapi,
            "Name": username,
            "Code": userkeyapi,
            "Intensity": b,
            "Duration": a,
            "Apikey": apikey,
            "Op": mode_random
        })

        if mode_random == 0:
            await update.message.reply_text(f"Shock number {amount_of_zaps} has been sent with {b}% intensity for {a} seconds!")
            print(f"Shock {amount_of_zaps} done")
            with open('log.txt', 'a') as f:
                f.write(f'[{current_time}] {username} sent a graduate shock!\n') 

        if mode_random == 1:
            await update.message.reply_text(f"Vibration number {amount_of_zaps} has been sent with {b}% intensity for {a} seconds!")
            print(f"Vibration {amount_of_zaps} done")
            with open('log.txt', 'a') as f:
                f.write(f'[{current_time}] {username} sent a graduate vibration!\n')
        a += random.randint(1, 3)
        b += random.randint(1, 16)
        print("")
        time.sleep(a)
        time.sleep(1)
    await update.message.reply_text("Done!")

def main():
    """Start the bot."""
    application = Application.builder().token("YOUR_TELEGRAM_BOT_API_KEY_HERE").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("adduser", adduser))
    application.add_handler(CommandHandler("removeuser", removeuser))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("shock", shock))
    application.add_handler(CommandHandler("vibrate", vibrate))
    application.add_handler(CommandHandler("reload", main))
    application.add_handler(CommandHandler("chatid", chatid))
    application.add_handler(CommandHandler("hiddenshock", hiddenshock))
    application.add_handler(CommandHandler("hiddenvibrate", hiddenvibrate))
    application.add_handler(CommandHandler("gradualrandom", gradualrandom))
    application.add_handler(CommandHandler("showlist", showlist))
    application.add_handler(CommandHandler("clearlog", clearlog))
    application.add_handler(CommandHandler("getconfig", getconfig))
    
    application.add_error_handler(error)
    
    application.run_polling()

if __name__ == '__main__':
    main() 
