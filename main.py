from tkinter import *
from tkinter import messagebox
import time
import threading
import requests
from decimal import *

from utils import read_default_settings, save_default_settings

API_URL_BTC_USD = 'https://www.okex.com/api/index/v3/BTC-USD/constituents'
API_URL_CNY_UDST = 'https://www.okex.com/v3/c2c/otc-ticker/quotedPrice?baseCurrency=USDT&quoteCurrency=CNY&side=sell&amount=&standard=1&paymentMethod=bank'

global pause_forced

getcontext().prec = 8

'''Event when cliking Start Button --- for starting watch BTC price '''
def start_watch():
    global pause_forced
    if not pause_forced:
        return

    btc_usdt_min = btc_min_threshold_field.get()
    if not btc_usdt_min:
        messagebox.showerror("Input Error", "Please input BTC-USDT minimum threshold")
        pause_forced = True
        return
    btc_usdt_max = btc_max_threshold_field.get()
    if not btc_usdt_max:
        pause_forced = True
        messagebox.showerror("Input Error", "Please input BTC-USDT maximum threshold")
        return
    btc_usdt_sleep_time = btc_sleep_time_field.get()

    usdt_cny_min = sell_min_threshold_field.get()
    if not usdt_cny_min:
        messagebox.showerror("Input Error", "Please input USDT-CNY minimum threshold")
        pause_forced = True
        return
    usdt_cny_max = sell_max_threshold_field.get()
    if not usdt_cny_max:
        pause_forced = True
        messagebox.showerror("Input Error", "Please input USDT-CNY maximum threshold")
        return
    usdt_cny_sleep_time = sell_sleep_time_field.get()

    btc_usdt_settings = {
        "min": btc_usdt_min,
        "max": btc_usdt_max,
        "sleep_time": btc_usdt_sleep_time
    }
    usdt_cny_settings = {
        "min": usdt_cny_min,
        "max": usdt_cny_max,
        "sleep_time": usdt_cny_sleep_time
    }

    save_default_settings("btc_usdt", btc_usdt_settings)
    save_default_settings("usdt_cny", usdt_cny_settings)

    pause_forced = False
    watch_btc_thread = threading.Thread(target=watch_btc_price, args=(btc_usdt_min, btc_usdt_max, btc_usdt_sleep_time,))
    watch_btc_thread.start()

    watch_sell_thread = threading.Thread(target=watch_sell_price, args=(usdt_cny_min, usdt_cny_max, usdt_cny_sleep_time,))
    watch_sell_thread.start()

''' Event when clicking Pause Button --- for pausing watch BTC price '''
def pause_watch():
    global pause_forced
    pause_forced = True

def exit():
    global pause_forced
    pause_forced = True
    win.destroy()

''' Thread for watching BTC price '''
def watch_btc_price(min_threshold_val, max_threshold_val, sleep_time_val):
    global pause_forced

    while(not pause_forced):
        jsonresp = requests.get(API_URL_BTC_USD).json()
        last_price = jsonresp['data']['last']

        if Decimal(last_price) < Decimal(min_threshold_val):
            messagebox.showinfo(
                "Bitcoin Price Alert", f"Current Bitcoin price is below than  minimum threshold.\nCurrent Bitcoin Price: {last_price}"
            )
        
        if Decimal(last_price) > Decimal(max_threshold_val):
            messagebox.showinfo(
                "Price Alert", f"Current Bitcoin price is over than maximum threshold.\nCurrent Bitcoin Price: {last_price}"
            )
    
        print(f"BTC price... {last_price}")
        time.sleep(int(sleep_time_val))

    print("Watching BTC is finished")

def watch_sell_price(min_threshold_val, max_threshold_val, sleep_time_val):
    global pause_forced

    while(not pause_forced):
        jsonresp = requests.get(API_URL_CNY_UDST).json()
        bank_item_list = list(item['price'] for item in jsonresp['data'] if item['payment'] == 'bank')

        last_price = bank_item_list[0]

        if Decimal(last_price) < Decimal(min_threshold_val):
            messagebox.showinfo(
                "CNY Price Alert", f"Current price is below than minimum threshold.\nCurrent CNY Price: {last_price}"
            )
        
        if Decimal(last_price) > Decimal(max_threshold_val):
            messagebox.showinfo(
                "CNY Price Alert", f"Current price is over than maximum threshold.\nCurrent CNY Price: {last_price}"
            )
    
        print(f"CNY price... {last_price}")
        time.sleep(int(sleep_time_val))

    print("Watching CNY is finished")

## Read current setings
btc_usdt_settings = read_default_settings("btc_usdt")
usdt_cny_settings = read_default_settings("usdt_cny")

win = Tk()
win.wm_attributes('-topmost', 1)
win.title("OKEX Price Monitor")
win.geometry("280x400")
win.configure(background='Orange1')
pause_forced = True

#Bitcoin frame
btc_frame = LabelFrame(win, text='BTC-USDT')
btc_frame.configure(background='LightBlue2')
btc_frame.grid(row=0, column=0, sticky=NSEW, padx=8, pady=8)
 
#Min Threshold
btc_min_threshold = Label(btc_frame, text='Min Threshold: ').grid(row=0, column=0)
btc_min_threshold_field = Entry(btc_frame, textvariable=btc_min_threshold)
btc_min_threshold_field.insert(END, btc_usdt_settings["min"])
btc_min_threshold_field.grid(row=0, column=1)

#Max Threshold
btc_max_threshold = Label(btc_frame, text='Max Threshold:').grid(row=1, column=0, pady=2)
btc_max_threshold_field = Entry(btc_frame, textvariable=btc_max_threshold)
btc_max_threshold_field.insert(END, btc_usdt_settings["max"])
btc_max_threshold_field.grid(row=1, column=1, padx=8, pady=8)

#API sleeping time
btc_sleep_time = Label(btc_frame, text='Sleep Time(seconds):').grid(row=2, column=0, pady=2)
btc_sleep_time_field = Entry(btc_frame, textvariable=btc_sleep_time)
btc_sleep_time_field.insert(END, btc_usdt_settings["sleep_time"])
btc_sleep_time_field.grid(row=2, column=1, padx=8, pady=8)

# Sell frame
sell_frame = LabelFrame(win, text='USDT-CNY')
sell_frame.configure(background='LightBlue2')
sell_frame.grid(row=1, column=0, sticky=NSEW, padx=8, pady=8)
 
## Min Threshold
sell_min_threshold = Label(sell_frame, text='Min Threshold: ').grid(row=0, column=0)
sell_min_threshold_field = Entry(sell_frame, textvariable=sell_min_threshold)
sell_min_threshold_field.insert(END, usdt_cny_settings["min"])
sell_min_threshold_field.grid(row=0, column=1)

## Max Threshold
sell_max_threshold = Label(sell_frame, text='Max Threshold:').grid(row=1, column=0, pady=2)
sell_max_threshold_field = Entry(sell_frame, textvariable=sell_max_threshold)
sell_max_threshold_field.insert(END, usdt_cny_settings["max"])
sell_max_threshold_field.grid(row=1, column=1, padx=8, pady=8)

## API sleeping time
sell_sleep_time = Label(sell_frame, text='Sleep Time(seconds):').grid(row=2, column=0, pady=2)
sell_sleep_time_field = Entry(sell_frame, textvariable=sell_sleep_time)
sell_sleep_time_field.insert(END, usdt_cny_settings["sleep_time"])
sell_sleep_time_field.grid(row=2, column=1, padx=8, pady=8)

action_frame = LabelFrame(win, text='Action panel')
action_frame.configure(background='LightBlue2')
action_frame.grid(row=2, column=0, sticky=NSEW, padx=8, pady=4)

btn_start = Button(action_frame, text="Start", width=12, command=start_watch)
btn_start.grid(row=3, column=0, padx=8, pady=4)

btn_pause = Button(action_frame, text="Pause", width=12, command=pause_watch)
btn_pause.grid(row=4, column=0, padx=8, pady=4)

btn_exit=Button(action_frame, text="Exit ", width=12, command=exit)
btn_exit.grid(row=5, column=0)

win.mainloop()