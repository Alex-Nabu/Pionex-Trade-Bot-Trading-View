from pionex_python.restful.Common import Common
from pionex_python.restful.Orders import Orders
from pionex_python.restful.Account import Account
from fastapi import FastAPI, Request, Query
import uvicorn
import json
import asyncio

app = FastAPI()

# some lines to read in config.json

with open('config.json') as f:
    config = json.load(f)

#setup a web server with a library like expressjs to receive the trading view webhook

apikey, secret = config['pionex']['apiKey'], config['pionex']['secret']

ordersClient = Orders(apikey, secret)
accountClient = Account(apikey, secret)


#post request to receive the trading view webhook
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    
    # Example: Process TradingView webhook data
    # Adjust the order parameters based on your webhook payload
    order = {
        'symbol': data.get('symbol', 'BTC_USDT'),
        'side': data.get('side', 'BUY'),
        'type': 'MARKET',
        'amount': data.get('amount', '2')
    }
    
    response = await ordersClient.new_order(**order)  # Note: Pionex client needs to support async
    return response


#get request to test the webhook
@app.get("/webhook")
async def webhook_get():
    order = {
        'symbol': 'BTC_USDT',
        'side': 'BUY',
        'type': 'MARKET',
        'amount': '10'
    }
    response = await ordersClient.new_order(**order)  # Note: Pionex client needs to support async

    print(response)
    return response


#sell all non usdt coin balances to usdt
#also read in symbol from query string
@app.get("/dump")
async def dump(symbol: str = Query(default=None), amount: str = Query(default=None), side: str = Query(default='SELL')):
    balance = await asyncio.to_thread(accountClient.get_balance)

    # try catch and retrurn error as response
    try:
        response = await asyncio.to_thread(
            ordersClient.new_order,
            symbol=symbol,
            side=side,
            type='MARKET',
            amount=amount,
        )
        print(response)
        return {"status": "success", "data": response}
        
    except Exception as e:
        error_message = str(e)
        print(f"Error occurred: {error_message}")
        # Return a structured error response
        return {
            "status": "error",
            "error": error_message,
            "details": {
                "symbol": symbol,
                "side": side,
                "amount": amount
            }
        }


if __name__ == '__main__':
    balance = accountClient.get_balance()  # Synchronous call
    USDT_balance = balance.get('data', {}).get('USDT', 0)
    print(f'balance: {balance}')
    print(f'USDT_balance: {USDT_balance}')

    # if(USDT_balance < 10):
    #     print('USDT balance is less than 1, Needed for trading, exiting')
    #     exit()

    uvicorn.run(app, host="0.0.0.0", port=5000)