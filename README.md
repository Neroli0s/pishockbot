Hey! Thanks for checking out my bot!

PiShockBot is a python-coded bot that makes POST calls to the official API of PiShock to controll shocks, vibrations, and beeps.

Before running the bot, please make those changes:
  - run `pip install -r requirements.txt` to install all requirements needed to run the bot
  - Change the following in `psb.py`:
    - Replace `admin_id = "YOUR_CHATID_HERE"` with your ChatID
    - Replace `YOUR_TELEGRAM_BOT_API_KEY_HERE` with your Bot API key obtained from BotFather
    - Replace `@YOURUSERNAME` on the /start message and the /chatid username
   
After that, do /help to get all the commands! 
You can find all of the PiShock API keys @ `https://pishock.com/#/account` and your UserID by going to `https://pishock.com/#/control`, then click on the Share button on the top right, then finally "New Share code". Finally the `"Username"` is going to be your PiShock username.

If something doesn't work, let me know, and I'll make sure to fix it as soon as possible.

(P.S: This project was created in 2021, and recently updated because I was still using Python 3.7.2 and Python-Telegram-Bot 13.15. After writing this, I realized there is now a PiShock lib. F*ck me, I guess, but hey, that's my first programming project and I'm still proud of what I did, even though it looks janky as hell.)
