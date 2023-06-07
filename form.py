import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as fd
import ytube as yd

app = tk.Tk()
app.title("Загрузка видео, аудио и субтитров с YouTube")
app.geometry('700x200')

frm = tk.Frame(master=app, height=200, width=700)
frm.pack()

label_down = ttk.Label(master=frm, text="Укажите папку загрузки")
label_down.grid(row=0, column=0)
label_video = ttk.Label(master=frm, text="Укажите видео YouTube")
label_video.grid(row=2, column=0)
label_low = ttk.Label(master=frm)
label_low.grid(row=500, column=0)


text_down = ttk.Entry(master=frm, width=70)
text_down.grid(row=0, column=1)
text_video = ttk.Entry(master=frm, width=70)
text_video.grid(row=2, column=1)


def searchBtn():
    direcrtory = fd.askdirectory(title='', initialdir='//')
    if direcrtory:
        text_down = direcrtory


def videoBtn():
    pass

btn_down = ttk.Button(master=frm, text="Папка загрузки", width=20, command=searchBtn)
btn_down.grid(row=0, column=2)
btn_video = ttk.Button(master=frm, text="Загрузить", width=20, command=videoBtn)
btn_video.grid(row=2, column=2)

text_down.bind('<Return>', btn_down)
text_video.bind('<Return>', btn_down)


app.mainloop()

