# Welcome
This is a python bot to take trades on pionex based on your tradingview alerts. Enable and set alerts in tradingview in webhooks and host the bot and then point your tradingview webook alerts to but server ip or url. 
Bot will then execute the trades based on the alerts it receives to buy or sell. 


# Installation Guide

1. **Ensure Python is Installed**  
   Make sure you have Python installed on your system.

2. **Install Required Libraries**  
   Run the following command to install the necessary libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Bot**  
   You can start the bot using:
   ```bash
   python3 bot.py
   ```

---

# Configuration

The configuration is straightforward. Below is an example of the configuration file:
```json
{
  "log_file": "log.json",  // the name you want to give your log file where trades done are logged. Also errors.
  "auth_token": "5CwfzRLTBcU2x4KnuqF",  // Your tradingview webhook auth code. secures api calls
  "tradeAmount": 10,  // The amount in dollars or percentage you want to execute trades for.
  "investmentType": "FIXED",  // FIXED = TradeAmount is using dollars so 10 = $10 dollars, PERCENTAGE = TradeAmount is percentage so 10 = 10% of your total USDT Pionex account balance
  "pionex": {
    "apiKey": "pionexApiKey",  // pionex apikey found in pionex settings
    "secret": "pionexApiSecret"  // pionex apikey secret found in pionex settings when creating api key
  },
  "enabled": true  // setting to say if the bot should process tradingview alert signals or not. true or false. For quick disable
}
```

# Conclusion

You can visit your ipaddress or localhost or http://localhost/docs for a easy webpage to set these config. Changes here will update config file also but only list the obvious ones that should be changed without restart loke amount and investmentType. 

---

# Donations
If you apprecaiate my work you tip me here I appreciate all tips but you dont have to :) 

- **Solana Tips:** `E2bn7uqJL1AX2U5GwqbJ5ZH87B2eZGgBcfPLbXnRaDew`
- **ETH Tips:** `0x10CB0691868C87673A177d3130205cfB0930ee0A`
- **BTC Tips (SegWit):** `bc1q6f4fge0pw4ang6pwfa9ufm9x9v03aqtw29wq3u`

---

# Contact

If you need help with your own project feel free to reach out to my agency [king.xanda+pn@gmail.com](mailto:king.xanda+pn@gmail.com). I reply pretty quickly! :D 👋👋

Happy Trading 👋👋👋
