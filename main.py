import tkinter as tk
import csv

sv_list = []
bv_list = []


def createHeader():
    label = tk.Label(
        text="Hello, Tkinter",
        fg="black",  # Set the text color to white
        bg="green yellow"  # Set the background color to black
    )
    label.pack()

def createTable(window):
    table = tk.LabelFrame(window, text="Passwords")
    table.grid_columnconfigure(0, weight=1)
    tk.Label(table, text="Account", anchor="w").grid(row=0, column=0, sticky="ew")
    tk.Label(table, text="User", anchor="w").grid(row=0, column=1, sticky="ew")
    tk.Label(table, text="Password", anchor="w").grid(row=0, column=2, sticky="ew")
    tk.Label(table, text="Comments", anchor="w").grid(row=0, column=3, sticky="ew")
    tk.Label(table, text="Update", anchor="w").grid(row=0, column=4, sticky="ew")
    tk.Label(table, text="Delete", anchor="w").grid(row=0, column=5, sticky="ew")
    return table

def populateTable(table):
    with open('ids.csv') as f:
        reader = csv.DictReader(f, delimiter=',')
        odd = True
        idx = 1
        for row in reader:
            bgcolor = ('#E0FFFF', '#E6E6FA')[odd]
            sv = tk.StringVar()
            bv = tk.BooleanVar()
            sv_list.append(sv)
            bv_list.append(bv)

            account = tk.Entry(table, textvariable=sv)
            account.insert(0, row['Account'])
            account.grid(row=idx, column=0, sticky="ew")
            account.configure({"background":bgcolor})
            sv.trace("w", lambda name, index, mode, var=bv: callback(var))
            # account.pack()

            username = tk.Entry(table)
            username.insert(0, row['Username'])
            username.grid(row=idx, column=1, sticky="ew")
            username.configure({"background":bgcolor})
            # username.pack()

            password = tk.Entry(table)
            password.insert(0, row['Password'])
            password.grid(row=idx, column=2, sticky="ew")
            password.configure({"background":bgcolor})
            # password.pack()

            comments = tk.Entry(table)
            comments.insert(0, row['Comments'])
            comments.grid(row=idx, column=3, sticky="ew")
            comments.configure({"background":bgcolor})
            # comments.pack()

            up_btn = tk.Checkbutton(table, variable=bv, onvalue=True, offvalue=False)
            up_btn.grid(row=idx, column=4, sticky="ew")
            # up_btn.pack()

            del_btn = tk.Checkbutton(table, onvalue=True, offvalue=False)
            del_btn.grid(row=idx, column=5, sticky="ew")
            # del_btn.pack()

            odd = not odd
            idx += 1

# def callbackUpdateCheck(event):
#     print(event)

def callback(bool_var):
    print(bool_var)
    bool_var.set(True)

def setupWindow():
    window = tk.Tk()
    window.title("Password Manager")
    width = 1000
    height = 400
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.geometry("%dx%d+%d+%d" % (width, height, x, y))
    window.resizable(True, True)
    return window

#============================INITIALIZATION==============================
if __name__ == '__main__':
    root = setupWindow()
    createHeader()
    table = createTable(root)
    populateTable(table)
    table.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    root.mainloop()
