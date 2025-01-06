from tkinter import *
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime, timedelta
import time
import tracemalloc
import tkinter as tk
from PIL import Image, ImageTk

window = Tk()
df = pd.read_csv('parkir.csv') #membaca dataset
latar = ImageTk.PhotoImage(Image.open("daa.png").resize((1152, 648))) #membuat background 
terisi_mobil = [] #membuat list kosong untuk spot mobil yang sudah terisi dari dataset
terisi_motor = [] #membuat list kosong untuk spot motor yang sudah terisi dari dataset
buttons = []
terisi_mobil_baru = [] #membuat list kosong untuk spot mobil dari inputan
terisi_motor_baru = [] #membuat list kosong untuk spot motor dari inputan
waktu_mobil_baru = {} #menyimpan waktu masuk dan keluar dari setiap spot mobil
waktu_motor_baru = {} #menyimpan waktu masuk dan keluar dari setiap spot motor

#Kode
#==========================================================================================
def spot_terisi(df, waktu_sekarang, kendaraan): #fungsi untuk menentukan spot parkir yang sudah terisi berdasarkan waktu dan jenis kendaraan
    global terisi, df_sekarang, spot_kosong
    waktu_masuk = pd.to_datetime(df["Entry_Time"], format="%H:%M:%S")
    waktu_keluar = pd.to_datetime(df["Exit_Time"], format="%H:%M:%S")

    ditempati = (waktu_masuk <= waktu_sekarang) & (waktu_keluar > waktu_sekarang)
    if kendaraan == "Car" :
        kendaraan_mobil = df["Vehicle_Type"] == "Car"
        df_sekarang = df[ditempati & kendaraan_mobil]

        terisi_mobil = list(df_sekarang["Parking_Spot_ID"])
        terisi_baru = terisi_mobil_baru
        terisi = terisi_mobil + terisi_baru

        spot_kosong = []
        for spot in range(1,51) :
            if spot not in terisi :
                spot_kosong.append(spot)

    elif kendaraan == "Motorcycle" :
        kendaraan_motor = df["Vehicle_Type"] == "Motorcycle"
        df_sekarang = df[ditempati & kendaraan_motor]
        
        terisi_motor = list(df_sekarang["Parking_Spot_ID"])
        terisi_baru = terisi_motor_baru
        terisi = terisi_motor + terisi_baru
        spot_kosong = []
        for spot in range(1,51) :
            if spot not in terisi :
                spot_kosong.append(spot)
    else :
        messagebox.showinfo("Pemberitahuan", "Error")

    for spot in df_sekarang["Parking_Spot_ID"]:
        buttons[spot - 1].config(bg="red", state=DISABLED)

def heuristic_recommendation(spot_kosong, waktu_sekarang): #fungsi rekomendasi heuristic untuk merekomendasikan tempat parkir berdasarkan waktu parkir sebelumnya dan jarak ke pintu masuk dengan melihat keseluruhan data
    global rekomendasi_heuristic
    
    tracemalloc.start()
    start_time = time.perf_counter()

    waktu_sekarang = pd.to_datetime(waktu_sekarang, format="%H:%M:%S").replace(day=datetime.now().day)

    df["waktu_keluar"] = pd.to_datetime(df["Exit_Time"], format="%H:%M:%S")

    waktu_optimal = None
    jarak_optimal = None
    rekomendasi_heuristic = None

    for i, row in df.iterrows():
        if row["waktu_keluar"] < waktu_sekarang and row["Parking_Spot_ID"] in spot_kosong:
            selisih_waktu = (waktu_sekarang - row["waktu_keluar"]).total_seconds()
            jarak = row["Proximity_To_Entry"]
            if (
                rekomendasi_heuristic is None or  
                (selisih_waktu < waktu_optimal or jarak < jarak_optimal)):
                waktu_optimal = selisih_waktu
                jarak_optimal = jarak
                rekomendasi_heuristic = row["Parking_Spot_ID"]

    end_time = time.perf_counter()
    runtime = end_time - start_time

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    heuristic_rekomendasi = Label(window, text=rekomendasi_heuristic, font=('Helvetica',11,'bold'), bg = '#5CE1E6', fg = 'black', width = 5, border=0)
    heuristic_rekomendasi.place(x = 970, y = 470)
    heuristic_jarak = Label(window, text=jarak_optimal, font=('Helvetica',11,'bold'), bg = '#5CE1E6', fg = 'black',width = 5, border=0)
    heuristic_jarak.place(x = 970, y = 501)
    heuristic_waktu = Label(window, text=f'{runtime:.4f} detik', font=('Helvetica',11,'bold'), bg = '#5CE1E6', fg = 'black', width = 10, border=0)
    heuristic_waktu.place(x = 970, y = 531)
    heuristic_memori = Label(window, text=f'{peak / 10**6:.6f} MB', font=('Helvetica',11,'bold'), bg = '#5CE1E6', fg = 'black', width = 10, border=0)
    heuristic_memori.place(x = 970, y = 558)

def greedy_recommendation(spot_kosong, waktu_sekarang): #fungsi rekomendasi greedy untuk merekomendasikan tempat parkir berdasarkan waktu parkir sebelumnya namun tidak melihat keseluruhan data
    global rekomendasi_greedy

    tracemalloc.start()
    start_time = time.perf_counter()
    waktu_sekarang = pd.to_datetime(waktu_sekarang, format="%H:%M:%S").replace(day=datetime.now().day)
    df["waktu_keluar"] = pd.to_datetime(df["Exit_Time"], format="%H:%M:%S")
    terkecil = None
    rekomendasi_greedy = None

    for i, row in df.iterrows():
        if row["waktu_keluar"] < waktu_sekarang and row["Parking_Spot_ID"] in spot_kosong:
            selisih_waktu = (waktu_sekarang - row["waktu_keluar"]).total_seconds()
            if rekomendasi_greedy is None or selisih_waktu < terkecil:
                terkecil = selisih_waktu
                rekomendasi_greedy = row["Parking_Spot_ID"]
                jarak = row["Proximity_To_Entry"]
                break
    
    end_time = time.perf_counter()
    runtime = end_time - start_time

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    greedy_rekomendasi = Label(window, text=rekomendasi_greedy, font=('Helvetica',11,'bold'), bg = '#FACEE1', fg = 'black', width = 5, border=0)
    greedy_rekomendasi.place(x = 970, y = 274)
    greedy_jarak = Label(window, text=jarak, font=('Helvetica',11,'bold'), bg = '#FACEE1', fg = 'black',width = 5, border=0)
    greedy_jarak.place(x = 970, y = 304)
    greedy_waktu = Label(window, text=f'{runtime:.4f} detik', font=('Helvetica',11,'bold'), bg = '#FACEE1', fg = 'black', width = 10, border=0)
    greedy_waktu.place(x = 970, y = 334)
    greedy_memori = Label(window, text=f'{peak / 10**6:.6f} MB', font=('Helvetica',11,'bold'), bg = '#FACEE1', fg = 'black', width = 10, border=0)
    greedy_memori.place(x = 970, y = 364)
    
def update_button_colors(waktu, kendaraan): #fungsi untuk mengatur warna button berdasarkan rekomendasi dan status parkir kendaraan
    spot_terisi(df, waktu, kendaraan)
    if len(spot_kosong)>0:
        heuristic_recommendation(spot_kosong, waktu_sekarang)
        greedy_recommendation(spot_kosong, waktu_sekarang)
    for i, button in enumerate(buttons, start=1):
        if i in terisi:
            button.config(bg="red", state = DISABLED)
        elif rekomendasi_greedy==rekomendasi_heuristic:
            button.config(bg="magenta", fg = "black", state = ACTIVE)
        elif i == rekomendasi_greedy:
            button.config(bg="pink", fg = "black", state = ACTIVE)
        elif i == rekomendasi_heuristic:
            button.config(bg="cyan", fg = "black", state = ACTIVE)
        else:
            button.config(bg="grey", state = ACTIVE)
            

def klik(spot, i): #fungsi untuk konfirmasi spot yang dipilih
    messagebox.showinfo("Pemberitahuan", "Silahkan mengisi tempat parkir tersebut")
    spot.config(bg="red", state=DISABLED)
    
    if kendaraan == "Car" :
        terisi_mobil_baru.append(i)
        waktu_mobil_baru[i] = [waktu_mini, durasi]
        update_waktu()
    else :
        terisi_motor_baru.append(i)
        waktu_motor_baru[i] = [waktu_mini, durasi]
        update_waktu()

    update_button_colors(waktu_sekarang, kendaraan)

    for i, button in enumerate(buttons, start=1):
        if i in terisi:
            button.config(bg="red")
        else:
            button.config(bg="grey", state = DISABLED)

    waktu_box.delete(0, 'end')
    durasi_box.delete(0, 'end')
    kendaraan_box.delete(0, 'end')

def show_tooltip(event, spot_id): #fungsi untuk menampilan waktu masuk dan keluar pada spot ketika user mengarahkan kursor ke setiap button spot
    global df_sekarang
    
    if 'df_sekarang' not in globals():
        tooltip.config(text="Data parkir\nbelum tersedia")
        return

    entry_time = df_sekarang[df_sekarang["Parking_Spot_ID"] == spot_id]["Entry_Time"].values
    exit_time = df_sekarang[df_sekarang["Parking_Spot_ID"] == spot_id]["Exit_Time"].values
    if entry_time.any() and exit_time.any():
        entry_time = entry_time[0]
        exit_time = exit_time[0]
        tooltip.config(text=f"Waktu masuk : {entry_time}\nWaktu keluar : {exit_time}")
        tooltip.place(x=980, y=174)
    else:
        if spot_id in waktu_baru:
            entry_time, exit_time = waktu_baru[spot_id]
            tooltip.config(text=f"Waktu masuk : {entry_time}\nWaktu keluar : {exit_time}")
            tooltip.place(x=980, y=174)
        else:   
            tooltip.config(text="Waktu masuk : ---//---\nWaktu keluar : ---//---")

def hide_tooltip(event): #fungsi untuk menyembunyikan waktu parkir
    tooltip.config(text=f"Waktu masuk : ---//---\nWaktu keluar : ---//---")

def update_waktu() : #fungsi untuk memperbarui waktu
    global waktu_baru
    if kendaraan == "Car" :
        waktu_baru = waktu_mobil_baru
    else :
        waktu_baru = waktu_motor_baru

def cari_parkir() : #fungsi untuk mencari tempat parkir kosong berdasarkan waktu masuk, jenis kendaraan, durasi dan memanggil rekomendasi algoritma yang telah dibuat
    global waktu_sekarang, waktu_mini, durasi, kendaraan, waktu_baru

    waktu_sekarang = waktu_box.get()
    kendaraan = kendaraan_box.get()
    durasi = durasi_box.get()
    update_waktu()
    if kendaraan != "" and  waktu_sekarang != "" and durasi != "" :
        try :
            waktu_mini = waktu_box.get()
            waktu_int = datetime.strptime(waktu_mini, "%H:%M:%S")
            durasi = waktu_int + timedelta(hours = int(durasi))
            durasi = durasi.strftime("%H:%M:%S")

            waktu_sekarang = pd.to_datetime(waktu_sekarang, format="%H:%M:%S")
            update_button_colors(waktu_sekarang, kendaraan)
            if not spot_kosong:
                messagebox.showwarning("Peringatan", "Tidak ada spot kosong yang tersedia!")
            analog2.config(text = f'{waktu_mini}')
        except ValueError :
            messagebox.showinfo("Pemberitahuan", "Silahkan isi data WAKTU MASUK dengan benar.")
    else : 
        messagebox.showinfo("Pemberitahuan", "Silahkan isi semua data yang diperlukan.")
    
#Tkinter
#==========================================================================================
window.title("parking")
window.geometry("1152x648")

Label(window, image = latar).place(x = 0, y = 0)

frame = Frame(window)
frame.place(x = 593, y = 370, anchor='center')

kotak = LabelFrame(frame, text = '')
kotak.pack()

waktu_box = Entry(window, font=('Helvetica',11,'bold'), width = 25, border=0)
waktu_box.place(x = 92, y = 283)

durasi_box = Entry(window, font=('Helvetica',11,'bold'), width = 24, border=0)
durasi_box.place(x = 91, y = 370)

kendaraan_list = ["", "Car", "Motorcycle"]
kendaraan_box = ttk.Combobox(window, values=list(kendaraan_list), font=('Helvetica',12,'bold'), width = 20)
kendaraan_box.place(x = 90, y = 445)

button=tk.Button(window, text="Cari Tempat Parkir", font=('Helvetica',11,'bold'), bg = '#38B6FF', fg = 'black', border = 0, cursor = "hand2", command = cari_parkir, width=21)
button.place(x=91, y=490)

analog2 = Label(window, text = "----//----", bg="white", font=('Helvetica',17,'bold'))
analog2.place(x = 990, y = 100, anchor='center')

tooltip = Label(window, text =f"Waktu masuk : ---//---\nWaktu keluar : ---//---", width=18, bg='#ffde59', font=('Helvetica',14,'bold'))
tooltip.place(x = 980, y = 174, anchor='center')

for i in range(1, 51):
    spot = Button(kotak, text=str(i), width=3, bg="grey", fg="white", border=0, cursor="hand2", command=lambda b=i: klik(buttons[b - 1], b), state = DISABLED)
    spot.grid(row=(i - 1) % 10, column=(i - 1) // 10, padx=20, pady=5)
    buttons.append(spot)

    spot.bind("<Enter>", lambda event, b=i: show_tooltip(event, b))
    spot.bind("<Leave>", hide_tooltip)

window.mainloop()
