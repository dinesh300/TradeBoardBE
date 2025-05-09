import asyncio
import time
# import requests
from pix_apidata import *

api = apidata_lib.ApiData()
event_loop = asyncio.get_event_loop()


async def main():
    # Register connection status callbacks
    api.on_connection_started(connection_started)
    api.on_connection_stopped(connection_stopped)

    # Register data callbacks
    api.on_trade_update(on_trade)
    api.on_best_update(on_best)
    api.on_refs_update(on_refs)
    api.on_srefs_update(on_srefs)
    api.on_tradeSnapshot_update(on_tradeSnapshot)
    api.on_greeks_update(on_greeks)
    api.on_greekSnapshot_update(on_greekSnapshot)

    # Initialize the API
    key = "WdcH05al5jj3VYKpb3DCpxU4AMk="
    host = "apidata.accelpix.in"
    scheme = "http"
    s = await api.initialize(key, host)
    print(s)

    # Retrieve intra-day historical data
    his = await api.get_intra_eod("NIFTY-1", "20210603", "20210604", "5")
    print("History:", his)

    # Define symbols and Greeks symbols
    syms = ['tcs-1','coalindia-1']
    symsGreeks = ["BANKNIFTY2290126500CE"]

    # Subscribe to live data streams
    await api.subscribeAll(syms)
    # Uncomment the following lines to subscribe to additional streams
    # await api.subscribeOptionChain('NIFTY', '20220901')
    # await api.subscribeGreeks(symsGreeks)
    # await api.subscribeOptionChainRange('NIFTY', '20220901', 3)
    print("Subscribe Done")

    # Optionally, unsubscribe after a delay
    # needSnapshot = False
    # await api.subscribeSegments(needSnapshot)
    # time.sleep(5)
    # await api.unsubscribeAll(['NIFTY-1'])
    # await api.unsubscribeGreeks(['BANKNIFTY2290126500CE'])
    # await api.unsubscribeOptionChain('NIFTY', '20220901')


def on_trade(msg):
    trd = apidata_models.Trade(msg)
    print("Trade:", msg)  # Alternatively, access specific attributes like trd.volume


def on_best(msg):
    bst = apidata_models.Best(msg)
    print("Best:", msg)  # Alternatively, access specific attributes like bst.bidPrice


def on_refs(msg):
    ref = apidata_models.Refs(msg)
    print("Refs snapshot:", msg)  # Alternatively, access specific attributes like ref.price


def on_srefs(msg):
    sref = apidata_models.RefsSnapshot(msg)
    print("Refs update:", msg)  # Alternatively, access specific attributes like sref.high


def on_tradeSnapshot(msg):
    trdSnap = apidata_models.Trade(msg)
    print("TradeSnap:", msg)  # Alternatively, access specific attributes like trdSnap.volume


def on_greeks(msg):
    greeks = apidata_models.Greeks(msg)
    print("OptionGreeks:", msg)  # Alternatively, access specific attributes like greeks.gamma


def on_greekSnapshot(msg):
    gr = apidata_models.Greeks(msg)
    print(msg)  # Alternatively, access specific attributes like gr.gamma


def connection_started():
    print("Connection started callback")


def connection_stopped():
    print("Connection stopped callback")


# Create and run the main task
event_loop.create_task(main())
try:
    event_loop.run_forever()
finally:
    event_loop.close()