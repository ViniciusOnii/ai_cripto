import config as k
import ccxt
import pandas as pd
import numpy as np
import pandas_ta as ta
import decimal as dc
import matplotlib as mt
import time

binance = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': k.binancekey,
    'secret': k.binacesecret,
    'options': {
        'defaultType': 'future'
    },
})

bal = binance.fetch_positions(symbols=['XRPUSDT']) #moeda entra aqui


def posicoes_abertas(symbol):
    lado = []
    tamanho =[]
    preco_entrada = []
    notional =[]
    percetage = []
    pnl = []
    bal = binance.fetch_positions(symbols=[symbol]) #moeda entr aqui

    for i in bal:
        lado = i['side']
        tamanho = i['info']['positionAmt'].replace('-', '')
        preco_entrada = i['entryPrice']
        notional = i['notional']
        percetage = i['percetage']
        pnl = i['info']['umRealizeProfit']

    if lado == 'long':
            pos_aberta = True
    elif lado == 'short':
            pos_aberta = True
    else:
            pos_aberta = False
        

            return lado, tamanho, preco_entrada,pos_aberta, notional, percetage,pnl
    
def livro_ofertas(symbol):
    livro_ofertas = binance.fetch_order_book(symbol)
    bid = dc.Decimal(livro_ofertas['bids'][0][0])
    ask = dc.Decimal(livro_ofertas['asks'][0][0])
    return bid, ask #melhor preco de compr e venda

def encerra_posicao(symbol):
    pos_aberta = posicoes_abertas(symbol=symbol)[3]

    while pos_aberta == True:
        lado = posicoes_abertas(symbol=symbol)[0]
        tamanho = posicoes_abertas(symbol=symbol)[1]


        if lado == 'long':
            binance.cancel_all_orders(symbol)
            bid,ask = livro_ofertas(symbol)
            ask = binance.price_to_precision(symbol,ask)
            binance.create_order(symbol, side='sell', type='LIMIT', price=ask, amount=tamanho, params={'hedged': 'True'})
            print(f'Vendendo posição long de {tamanho} moedas de {symbol}')
            time.sleep(20)


        elif lado == 'short':
            binance.cancel_all_orders(symbol)
            bid,ask = livro_ofertas(symbol)
            bid = binance.price_to_precision(symbol,bid)
            
            binance.create_order(symbol, side='buy', type='LIMIT', price=bid, amount=tamanho, params={'hedged': 'True'})
            print(f'Comprando posição short de {tamanho} moedas de {symbol}')
            time.sleep(20)
        else:
            print('Impossivel encerrar posição')

        pos_aberta = posicoes_abertas(symbol=symbol)[3]


def fecha_pnl(symbol,loss,target):
    percent = posicoes_abertas(symbol=symbol)[5]
    pnl = posicoes_abertas(symbol=symbol)[6]
    if percent:
        if percent <=loss:
            print(f'Encerrdo posicao por loss! {pnl}')
            encerra_posicao(symbol)
        elif percent >= target:
            print(f'Encerrdo posicao por gain! {pnl}')



def posicao_max(symbol, max_pos):
   pos = posicoes_abertas(symbol)[1]
   if isinstance(pos, list):
        max_posicao = False
   elif float(pos) >= max_pos:
        max_posicao = True 
   else:
        max_posicao = False

   return max_posicao       
         

def ultima_orderm_aberta(symbol):
    order = []
    try:
        order = binance.fetch_orders(symbol)[-1]['status']
        if order == 'open':
            open_order = True
        else: 
            open_order = False
    except:  
         open_order = False   
         
    return open_order        