import os
import asyncio
import ccxt.async_support as ccxt
import discord
from discord import Intents
from discord.ext import commands
from pycoingecko import CoinGeckoAPI

TOKEN = "MTA5MjE4MzMyNjQ1MTgzOTA2Ng.GAGWWV.WpobrpwfOJTPIk0DiG0plysVTP3176kq258"
ARBITRAGE_THRESHOLD = 0.01

intents = Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

exchanges = [
    ccxt.binance(),
    ccxt.coinbasepro(),
    ccxt.kraken(),
    ccxt.bybit(),
    ccxt.bitget(),
]

cg = CoinGeckoAPI()

async def load_exchanges():
    for exchange in exchanges:
        try:
            await exchange.load_markets()
            print(f"{exchange.name} marchés chargés.")
        except Exception as e:
            print(f"Erreur lors du chargement des marchés pour {exchange.name}: {e}")

async def get_common_symbols():
    top_cryptos = cg.get_coins_markets(vs_currency='usd', per_page=100)
    top_symbols = set(crypto['symbol'].upper() + '/USDT' for crypto in top_cryptos)
    
    exchange_symbols = []
    for exchange in exchanges:
        if exchange.has['fetchMarkets']:
            markets = await exchange.load_markets()
            symbols = set(market['symbol'] for market in markets.values() if ('active' not in market or market['active']) and market['symbol'] in top_symbols)
            exchange_symbols.append(symbols)

    common_symbols = set()
    for s in top_symbols:
        count = sum(1 for symbols in exchange_symbols if s in symbols)
        if count >= 2:
            common_symbols.add(s)
    
    return list(common_symbols)

async def check_arbitrage_opportunities():
    while True:
        for symbol in custom_symbols:
            prices = []
            for exchange in exchanges:
                ticker = None
                try:
                    ticker = await exchange.fetch_ticker(symbol)
                except Exception as e:
                    print(f"Erreur lors de la récupération du ticker pour {symbol} sur {exchange.name}: {e}")

                if ticker:
                    prices.append((exchange.name, ticker["ask"]))

            if len(prices) < 2:
                continue

            prices.sort(key=lambda x: x[1])
            min_price = prices[0][1]
            max_price = prices[-1][1]
            arbitrage_percentage = (max_price - min_price) / min_price if min_price != 0 else 0

            if arbitrage_percentage > ARBITRAGE_THRESHOLD:
                message = f"Opportunité d'arbitrage détectée pour {symbol}:\n"
                for exchange_name, price in prices:
                    message += f"- {exchange_name}: {price}\n"
                await bot.get_channel(1092184703014027324).send(message)

        await asyncio.sleep(60)

@bot.event
async def on_ready():
    print(f"{bot.user.name} est connecté avec succès.")
    await load_exchanges()
    global custom_symbols
    custom_symbols = await get_common_symbols()
    print(f"Vérification des opportunités d'arbitrage pour les symboles suivants : {custom_symbols}")
    bot.loop.create_task(check_arbitrage_opportunities())

bot.run(TOKEN)
