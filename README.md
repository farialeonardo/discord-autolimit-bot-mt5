This bot was developed to help placing trades based on MT's signals shared on his Discord Server. Below you can find basic information and what you need to get this setup done.


Step-by-Step Guide to Using the Discord Trade Bot

1. What You Need
Before you start, make sure you have the following:

- MetaTrader 5 (MT5): Installed and set up with your broker account.
- Python Installed: A programming tool that runs the bot. You can download it from python.org (Version 3.12.x recommended)
- A Discord Server: [Create](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server) one if you don’t have it. 
- Discord Bot Token: This is a special key that lets your bot connect to Discord.

2. Setting Up Your Discord Bot

Create a Discord Bot:

Go to the Discord Developer Portal.
Click on **"New Application"** name it, and save.
Go to the **"Bot"** tab on the left and click **"Add Bot"**
Click **"Reset Token"** and copy your bot token. Save this token, you'll need it later.
Under **"Privileged Gateway Intents"** make sure **"Message Content Intent"** is enabled.

Invite Your Bot to Your Discord Server:

Go to the **"OAuth2"** section, then to the **"URL Generator"**
Under **"SCOPES"** check **"bot"**
Under **"BOT PERMISSIONS"** check **"Send Messages"** and **"Read Messages"**
Copy the generated link and paste it into your browser. Choose your server to invite the bot.

3. Preparing the Python Bot File

Download the *auto-limit-discord-bot.py* file from this repo.
Edit the Bot Token in the Python Script:
Open the *auto-limit-discord-bot.py* file with a text editor (like Notepad).
Find the line that says **DISCORD_TOKEN = 'YOUR_DISCORD_BOT_TOKEN'**
Replace **'YOUR_DISCORD_BOT_TOKEN'** with the token you copied from the Discord Developer Portal
Save and close the file

4. Running the Bot
Installing the required tools and modules

Open the Command Prompt (Windows) as Administrator:
This command will install the necessary tools to run the bot.

```py -m pip install discord.py MetaTrader5 numpy<2.0```

Run the Bot:

In the Command Prompt or Terminal, navigate to where you saved *auto-limit-discord-bot.py*
Run the bot by typing:

```py discord_trade_bot.py```

If everything is set up correctly, you should see a message saying the bot is connected to Discord.

5. Sending Trade Signals on Discord

To place a trade, go to your Discord server and type a message in this format:

```SELL LIMIT XAUUSD 1.5% 2750.00 2751.00 2749.00```

**What Each Part Means:**
\
**SELL** or **BUY**: Whether to sell or buy.
\
**LIMIT** or **STOP** or **MARKET**: Type of order.
\
**XAUUSD**: The trading symbol (e.g., Gold).
\
**1.5%**: The amount to trade (volume). This will calculate the lot size based on the percentage you want to risk on that particular trade
\
**2750.0**: The entry price where you want the trade to execute.
\
**2751.0**: Stop Loss price (to minimize loss).
\
**2749.0**: Take Profit price (to lock in profit).

6. Checking Trades in MetaTrader 5
Open MetaTrader 5.
Go to **'Terminal'** -> **'Trade'** at the bottom of the screen.
You should see the trade placed by the bot with a comment like "Discord signal trade."

**Common Issues and Simple Fixes**
Bot Isn’t Responding:
Ensure the bot is online in Discord and invited to the right channel.
Make sure the bot has permission to read and send messages in the channel.

**Signal Format Error:**
Ensure your trade signals follow the exact format as shown above. No extra spaces or missing numbers!

**MetaTrader 5 Not Running or Set Up Properly:**
Make sure MetaTrader 5 is installed and logged in with your broker account.
Make sure the symbol (e.g., XAUUSD) is visible in the Market Watch. Right-click in the Market Watch window and select "Show All" to display all symbols.

**Auto Trading not activated:**
Enable the Button in mt5 with the lable "Algo Trading"

**Trade Failed or Invalid Request:**
Ensure the prices (entry, stop loss, take profit) are set according to your broker's rules.
Double-check the volume is within your broker's allowed range. You can see these rules in the "Specification" for each symbol in MetaTrader 5.

**Volume or Symbol Error:**
Ensure you use the correct symbol names and trading volumes allowed by your broker.

**Final Tips**
Test with a Demo Account: Always test the bot on a demo account first to avoid losing real money.
Keep the Bot Running: The bot only works while the Python script is running, so keep it open.
Logging: The bot outputs helpful messages in the Command Prompt or Terminal. Read them to understand what’s happening.
By following these simplified steps, you should be able to set up and use the Discord trade bot with MetaTrader 5 without needing to dive into coding!
