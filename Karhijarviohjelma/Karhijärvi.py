import requests
from bs4 import BeautifulSoup
import schedule
import time
import csv
import tkinter as tk 
from tkinter import messagebox

# URL-address "This about a lake in finland they upload water level daily I guess.."
url = 'http://www.karhijarvi.fi/karhijarvi.html'

def fetch_water_level():
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find <div> and so on... until found the right one.
        #  I went true that HTML to find it.
        #  So if they change it I have to change this
        mainpan_div = soup.find('div', id='mainPan')
        if mainpan_div:
            bodypan = mainpan_div.find('div', id='bodyPan')
            if bodypan:
                leftpan_div = bodypan.find('div', id='leftPan')
                if leftpan_div:
                    ul_element = leftpan_div.find_all('ul')
                    if ul_element:
                        list_items = ul_element[2].find_all('p')
                        
                        for item in list_items:
                            
                            water_level = item.text.strip()
                            print(f'{water_level}')
                            
                            # Save to CSV
                            with open('water_levels.csv', 'a', newline='') as csvfile:
                                csvwriter = csv.writer(csvfile)
                                csvwriter.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), water_level])

                            text_field.insert(tk.END, f"{water_level}\n")

    else:
        with open('water_levels.csv', 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(f'Pyyntö epäonnistui, statuskoodi: {response.status_code}')


#Do everyday if running this. Else everytime program is started. 
#User can set what time they want.
def schedule_task(time_str):
    schedule.every().day.at(time_str).do(fetch_water_level) 
    while True: 
        schedule.run_pending() 
        time.sleep(1) 

#Some user guidance in timer setting.
def start_scheduler(): 
    import threading
    time_input = time_entry.get() 
    if len(time_input) == 4 and time_input.isdigit(): 
        hours = int(time_input[:2]) 
        minutes = int(time_input[2:]) 
        if 0 <= hours < 24 and 0 <= minutes < 60: 
            time_str = time_input[:2] + ":" + time_input[2:] 
            scheduler_thread = threading.Thread(target=schedule_task, args=(time_str,)) 
            scheduler_thread.daemon = True 
            scheduler_thread.start() 
            messagebox.showinfo("Ajastin", f"Ajastin käynnistetty ajalle {time_str}!") 
        else: messagebox.showerror("Virhe", "Syötä aika, joka on 24 tunnin sisällä (esim. 1230).")
    else: messagebox.showerror("Virhe", "Syötä aika muodossa HHMM (esim. 0830).")

#Made it as an app
app = tk.Tk() 
app.title("Karhijärven Vedenkorkeus") 
app.geometry("400x400") 

water_level_label = tk.Label(app, text="Karhijärven vedenkorkeus", font=("Helvetica", 16)) 
water_level_label.pack(pady=20) 

fetch_button = tk.Button(app, text="Hae Vedenkorkeus", command=fetch_water_level) 
fetch_button.pack(pady=10) 

schedule_button = tk.Button(app, text="Käynnistä Ajastin", command=start_scheduler) 
schedule_button.pack(pady=10)

text_field = tk.Text(app, height=10, width=50) 
text_field.pack()

time_label = tk.Label(app, text="Syötä ajastimen aika (HH:MM):") 
time_label.pack(pady=5) 
time_entry = tk.Entry(app) 
time_entry.pack(pady=5)

fetch_water_level()
app.mainloop()