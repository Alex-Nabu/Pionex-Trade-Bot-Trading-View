from pionex_python.restful.Common import Common
from pionex_python.restful.Orders import Orders
from pionex_python.restful.Account import Account
from fastapi import FastAPI, Request, Query, Body
import uvicorn
import json
import asyncio
import pandas as pd
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

# some lines to read in config.json

with open('config.json') as f:
    config = json.load(f)


# Create or load the existing Excel file
# EXCEL_FILE = config['log_file']
# try:
#     df = pd.read_excel(EXCEL_FILE)
# except FileNotFoundError:
#     df = pd.DataFrame(columns=[
#         'timestamp', 'symbol', 'side', 'amount', 'order_type',
#         'status', 'order_id', 'error_message'
#     ])

# Define a function to log orders
def log_order(response, order, error_message=''):
    try:
        log_entry = {
            'timestamp': datetime.fromtimestamp(response.get('timestamp', 0)/1000).isoformat() if response.get('timestamp') else datetime.now().isoformat(),
            'symbol': order['symbol'],
            'side': order['side'],
            'amount': order['amount'],
            'order_type': order['type'],
            'status': 'SUCCESS' if response.get('result') else 'FAILED' if not error_message else 'ERROR',
            'order_id': response.get('data', {}).get('orderId', ''),
            'error_message': error_message or response.get('error', '')
        }
        
        print(f"Writing log entry: {log_entry}")  # Debug print

                
        #global df
        #df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
        #df.to_excel(EXCEL_FILE, index=False)

        with open(config['log_file'], 'a') as f:
            json_line = json.dumps(log_entry)
            f.write(json_line + '\n')
            f.flush()  # Force write to disk
            
    except Exception as e:
        print(f"Error writing to log file: {e}")

#setup a web server with a library like expressjs to receive the trading view webhook

apikey, secret = config['pionex']['apiKey'], config['pionex']['secret']

ordersClient = Orders(apikey, secret)
accountClient = Account(apikey, secret)


#setup default page to say {"detail":"Not Found"}
@app.get("/")
async def root():
    return {f"detail": "Processing webhooks"}


# Add this model class after the imports
class WebhookData(BaseModel):
    auth_token: str
    action: str
    contracts: str | None = None
    price: str | None = None
    symbol: str
    time: str | None = None


# Modify the webhook endpoint
@app.post("/webhook")
async def webhook(request: Request, webhook_data: WebhookData | None = Body(default=None)):
    try:

        # First try to get data from the request body directly (for existing webhook)
        try:
            data = await request.json()
        except:
            # If direct JSON parsing fails, use the webhook_data from FastAPI
            if webhook_data:
                data = webhook_data.model_dump()
            else:
                raise ValueError("No valid data provided")

        print(f"Received webhook data: {data}")
        
        # Validate auth token
        if data.get('auth_token') != config['auth_token']:
            # return {
            #     "status": "error",
            #     "error": "Invalid authentication token",
            #     "detail": "Unauthorized access"
            # }
            print(f"Invalid authentication token, skipping signal")
            return
        
        
        # Check if trading is enabled
        if not config.get('enabled'):  # Default to True if not set
            print(f"Trading is disabled, skipping signal")
            return 

    
        # Format symbol (e.g., XRPUSDT -> XRP_USDT)
        raw_symbol = data.get('symbol')
        if 'USDT' in raw_symbol and '_' not in raw_symbol:
            formatted_symbol = raw_symbol.replace('USDT', '_USDT')
        else:
            formatted_symbol = raw_symbol
        
        # Extract order parameters from webhook payload

        #check investmentType and set amount accordingly
        if config['investmentType'] == 'FIXED':
            amount = config['tradeAmount']
        elif config['investmentType'] == 'PERCENTAGE':
            balance = await asyncio.to_thread(accountClient.get_balance)
            USDT_balance = balance.get('data', {}).get('USDT', 0)
            amount = round(config['tradeAmount'] / USDT_balance * 100, 2)


        order = {
            'symbol': formatted_symbol,
            'side': data.get('action').upper(),
            'type': 'MARKET',
            'amount': amount
        }

        print(f"Order: {order}");
        #return {f"detail": "Processing webhooks..."}
        
        #response = await asyncio.to_thread(ordersClient.new_order, **order)
        response =  {
            'result': True, 
            'data': {'orderId': 10997315733345430, 'clientOrderId': ''}, 
            'timestamp': 1733818081950
        }
        print(f"Order response: {response}")
        
        # Log the order
        log_order(response, order)
                
    except json.JSONDecodeError:
        print("Invalid JSON payload received")
        return {f"detail": "Processing webhooks..."}
        return {
            "status": "error",
            "error": "Invalid JSON payload",
            "detail": "The webhook data must be valid JSON"
        }
    except Exception as e:
        print(f"Error occurred: {e}")
        
        # Log the error
        log_order({}, order, str(e))
        

#get request to test the webhook
@app.get("/webhook")
async def webhook_get(request: Request):
    try:
        # Get query parameters from the request
        params = dict(request.query_params)
        print(f"Query parameters: {params}")
        return {f"detail": "Processing webhooks..."}
    
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


# Modify the update_config endpoint to use individual Query parameters
@app.get("/update_config")
async def update_config(
    auth_token: str = Query(None),
    tradeAmount: float = Query(None),
    investmentType: str = Query(None),
    enabled: bool = Query(None)
):
    try:
        data = {
            'auth_token': auth_token,
            'tradeAmount': tradeAmount,
            'investmentType': investmentType,
            'enabled': enabled
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        print(f"Config update parameters: {data}")

        #check auth token
        if data.get('auth_token') != config['auth_token']:
            return {"status": "error", "error": "Invalid authentication token", "detail": "Unauthorized access"}

        updated = False
        
        # Update tradeAmount if provided
        if 'tradeAmount' in data:
            config['tradeAmount'] = float(data['tradeAmount'])
            updated = True
            
        # Update investmentType if provided
        if 'investmentType' in data:
            config['investmentType'] = data['investmentType']
            updated = True
            
        # Update enabled if provided
        if 'enabled' in data:
            config['enabled'] = data['enabled']
            updated = True

        if updated:
            #write the updated config to the config.json file
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            return {"status": "success", "data": config}
        else:
            return {"status": "success", "status": "No changes to config", "data": config}

    except Exception as e:
        return {"status": "error", "error": str(e), "detail": "Error updating config"}

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

    uvicorn.run(app, host="0.0.0.0", port=80)