from pionex_python.restful.Common import Common
from pionex_python.restful.Orders import Orders
from pionex_python.restful.Account import Account
from fastapi import FastAPI, Request
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
@app.get("/dump")
async def dump():
    balance = await asyncio.to_thread(accountClient.get_balance)

    #iterate through the balance and sell all non usdt coin balances to usdt
    for balance_item in balance.get('data', {}).get('balances', []):
        coin = balance_item.get('coin')
        free_amount = balance_item.get('free')
        if coin != 'USDT' and float(free_amount) > 0:
            print(f'Selling {coin} balance: {free_amount}')

            #async do a sell order for the coin
            response = await asyncio.to_thread(
                ordersClient.new_order,
                symbol=coin + '_USDT',
                side='SELL',
                type='MARKET',
                amount= free_amount
            )
            
            print(response)

            #concatenate the response to a string and if last balance item print the string
            response_string = response_string + str(response) + '\n'
            print(response_string)

            # if coin == balance.get('data', {}).get('balances', [])[-1].get('coin')  :
            #       return response_string

    return f"Dumpeding all non USDT coins to USDT"


if __name__ == '__main__':
    balance = accountClient.get_balance()  # Synchronous call
    USDT_balance = balance.get('data', {}).get('USDT', 0)
    print(f'USDT_balance: {USDT_balance}')

    # if(USDT_balance < 10):
    #     print('USDT balance is less than 1, Needed for trading, exiting')
    #     exit()

    uvicorn.run(app, host="0.0.0.0", port=5000)