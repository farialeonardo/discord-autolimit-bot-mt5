import discord
import MetaTrader5 as mt5
import re

# Discord bot token
DISCORD_TOKEN = 'YOUR_DISCORD_BOT_TOKEN_HERE'  # Replace with your actual Discord bot token

# Initialize MetaTrader 5
if not mt5.initialize():
    print(f"MT5 initialization failed: {mt5.last_error()}")
    exit()

# Create the Discord client
intents = discord.Intents.default()
intents.message_content = True  # Ensure message content is enabled
client = discord.Client(intents=intents)

def parse_trade_signal(message):
    """
    Parse trade signals from the message content.
    Expected format: ORDER_TYPE ORDER_KIND SYMBOL RISK_PERCENT ENTRY_PRICE SL TP
    Example: SELL LIMIT XAUUSD 1.5% 2750.00 2751.00 2749.00
    """
    try:
        # Update the regex pattern to allow decimal percentages
        pattern = r"(?P<order_type>BUY|SELL) (?P<order_kind>LIMIT|STOP|MARKET) (?P<symbol>\w+) (?P<risk_percentage>\d+(\.\d+)?)% (?P<entry_price>\d*\.?\d+) (?P<sl>\d*\.?\d+) (?P<tp>\d*\.?\d+)"
        match = re.match(pattern, message)
        if match:
            return match.groupdict()
        else:
            return None
    except Exception as e:
        print(f"Error parsing signal: {e}")
        return None

# In the place_trade function, convert the risk percentage to float before passing it to calculate_lot_size
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Split the message into lines
    lines = message.content.strip().split('\n')

    # Parse the trade signal
    for line in lines:
        # Debug print for line content
        print(f"Processing line: {line}")

        # Parse the trade signal
        trade_signal = parse_trade_signal(line)
        print(f"Parsed trade signal: {trade_signal}")  # Check parsed output

        if trade_signal:
            print(f"Received trade signal: {trade_signal}")
            success = place_trade(
                order_type=trade_signal['order_type'],
                order_kind=trade_signal['order_kind'],
                symbol=trade_signal['symbol'],
                risk_percentage=float(trade_signal['risk_percentage']),  # Ensure this is a float
                entry_price=trade_signal['entry_price'],
                sl=trade_signal['sl'],
                tp=trade_signal['tp']
            )
            if success:
                print(f"Line content before sending message: {line}")
                await message.channel.send(f"Trade placed successfully for: {line}")
            else:
                print(f"Line content before sending message: {line}")
                await message.channel.send(f"Failed to place trade for: {line}. Check logs for details.")
        else:
            print(f"Invalid signal format received for line: {line}")

def calculate_lot_size(balance, risk_percentage, symbol, entry_price, sl):
    """
    Calculate lot size based on account balance, risk percentage, and symbol details.
    This handles various asset classes, including exotic forex pairs, metals, commodities, and indices.
    """
    # Ensure entry_price and sl are floats
    entry_price = float(entry_price)
    sl = float(sl)

    # Calculate the risk amount based on the balance and risk percentage
    risk_amount = balance * (risk_percentage / 100)
    print(f"Risk Amount: {risk_amount}")

    # Retrieve symbol information
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"Symbol info not found for {symbol}")
        return None

    # Contract size and tick size for the symbol
    contract_size = symbol_info.trade_contract_size
    tick_size = symbol_info.point
    tick_value = symbol_info.trade_tick_value  # Tick value per minimum price movement

    # Debug print for symbol info
    print(f"Symbol Info for {symbol}:")
    print(f"  Contract Size: {contract_size}")
    print(f"  Tick Size (Point): {tick_size}")
    print(f"  Tick Value: {tick_value}")
    print(f"  Min Volume: {symbol_info.volume_min}")
    print(f"  Max Volume: {symbol_info.volume_max}")
    print(f"  Volume Step: {symbol_info.volume_step}")

    # Calculate the stop loss in ticks
    stop_loss_ticks = abs(entry_price - sl) / tick_size
    print(f"Stop Loss in Ticks: {stop_loss_ticks}")

    # Calculate potential loss per lot based on stop loss and tick value
    potential_loss_per_lot = stop_loss_ticks * tick_value
    print(f"Potential Loss per Lot: {potential_loss_per_lot}")

    # Handle potential zero or extremely small values
    if potential_loss_per_lot == 0:
        print("Potential loss per lot is zero or negligible, check SL and entry price.")
        return None

    # Calculate the initial lot size based on risk amount and potential loss per lot
    lot_size = risk_amount / potential_loss_per_lot
    print(f"Calculated Lot Size before Rounding: {lot_size}")

    # Ensure lot size respects the broker's volume restrictions and rounds to nearest step
    if lot_size < symbol_info.volume_min:
        lot_size = symbol_info.volume_min
        print("Adjusted Lot Size to Min Volume")
    elif lot_size > symbol_info.volume_max:
        lot_size = symbol_info.volume_max
        print("Adjusted Lot Size to Max Volume")
    else:
        # Round down to nearest valid increment
        lot_size = (int(lot_size / symbol_info.volume_step) * symbol_info.volume_step)

    # Debug output for final calculated lot size
    print(f"Final Calculated Lot Size for {symbol}: {lot_size}")

    return lot_size



def place_trade(order_type, order_kind, symbol, risk_percentage, entry_price, sl, tp):
    """
    Places a trade on MT5 with the given parameters.
    """
    # Ensure the symbol is available in the Market Watch
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol {symbol}")
        return False

    # Get current account balance
    balance = mt5.account_info().balance
    
    # Calculate volume based on account balance percentage
    volume = calculate_lot_size(balance, float(risk_percentage), symbol, entry_price, sl)
    
    if volume is None:
        print("Failed to calculate volume.")
        return False

    # Determine the order type for MT5
    if order_kind.upper() == "LIMIT":
        order_type_mt5 = mt5.ORDER_TYPE_BUY_LIMIT if order_type.upper() == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT
    elif order_kind.upper() == "STOP":
        order_type_mt5 = mt5.ORDER_TYPE_BUY_STOP if order_type.upper() == "BUY" else mt5.ORDER_TYPE_SELL_STOP
    else:
        order_type_mt5 = mt5.ORDER_TYPE_BUY if order_type.upper() == "BUY" else mt5.ORDER_TYPE_SELL

    # Debug prints
    print(f"Placing trade: {order_type_mt5} {symbol} Volume: {volume} Entry: {entry_price} SL: {sl} TP: {tp}")

    # Create the order request
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type": order_type_mt5,
        "price": float(entry_price),
        "sl": float(sl),
        "tp": float(tp),
        "deviation": 20,
        "magic": 234000,
        "comment": "Discord signal trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    # Send the order
    result = mt5.order_send(request)
    
    # Check result
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed: {result.retcode} - {mt5.last_error()}")
        return False
    else:
        print(f"Order placed successfully: {result}")
        return True

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Split the message into lines
    lines = message.content.strip().split('\n')

    # Parse the trade signal
    for line in lines:
        # Debug print for line content
        print(f"Processing line: {line}")

        # Parse the trade signal
        trade_signal = parse_trade_signal(line)
        print(f"Parsed trade signal: {trade_signal}")  # Check parsed output

        if trade_signal:
            print(f"Received trade signal: {trade_signal}")
            success = place_trade(
                order_type=trade_signal['order_type'],
                order_kind=trade_signal['order_kind'],
                symbol=trade_signal['symbol'],
                risk_percentage=trade_signal['risk_percentage'],
                entry_price=trade_signal['entry_price'],
                sl=trade_signal['sl'],
                tp=trade_signal['tp']
            )
            if success:
                print(f"Line content before sending message: {line}")
                await message.channel.send(f"Trade placed successfully for: {line}")
            else:
                print(f"Line content before sending message: {line}")
                await message.channel.send(f"Failed to place trade for: {line}. Check logs for details.")
        else:
            print(f"Invalid signal format received for line: {line}")

# Start the Discord bot
client.run(DISCORD_TOKEN)

# Shutdown MetaTrader 5 on exit
mt5.shutdown()