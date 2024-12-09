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


#setup default page to say {"detail":"Not Found"}
@app.get("/")
async def root():
    return {f"detail": "Processing webhooks"}


#post request to receive the trading view webhook
@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Parse the JSON payload from the webhook
        data = await request.json()
        print(f"Received webhook data: {data}")
        return {f"detail": "Processing webhooks"}
        
        # Extract order parameters from webhook payload
        order = {
            'symbol': data.get('symbol', 'BTC_USDT'),
            'side': data.get('side', 'BUY'),
            'type': 'MARKET',
            'amount': data.get('amount', '2')
        }
        
        response = await asyncio.to_thread(ordersClient.new_order, **order)
        print(f"Order response: {response}")
        return {
            "status": "success",
            "data": response
        }
        
    except json.JSONDecodeError:
        print("Invalid JSON payload received")
        return {
            "status": "error",
            "error": "Invalid JSON payload",
            "detail": "The webhook data must be valid JSON"
        }
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            "status": "error",
            "error": str(e),
            "detail": "Error processing webhook"
        }


#get request to test the webhook
@app.get("/webhook")
async def webhook_get(request: Request):
    try:
        # Get query parameters from the request
        params = dict(request.query_params)
        print(f"Query parameters: {params}")
        return {f"detail": "Processing webhooks"}
    
        if not params:
            return {"detail": "No query parameters provided"}
        
        print(f"Query parameters: {params}")
        
        # Extract order parameters from query params
        order = {
            'symbol': params.get('symbol', 'BTC_USDT'),
            'side': params.get('side', 'BUY'),
            'type': 'MARKET',
            'amount': params.get('amount', '10')
        }
        
        response = await asyncio.to_thread(ordersClient.new_order, **order)
        print(f"Order response: {response}")
        return response
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            "status": "error",
            "error": str(e),
            "detail": "Error processing webhook"
        }


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