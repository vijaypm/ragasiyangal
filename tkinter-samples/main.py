import tkinter as tk
import csv

#TODO convert the individual column lists into a single list of a data object
ac_sv_list = []
user_sv_list = []
pass_sv_list = []
comments_sv_list = []
updt_bv_list = []
del_bv_list = []
numrows = 0

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
        for row in reader:
            addRow(table, row)

def callback(bool_var):
    print(bool_var)
    bool_var.set(True)

def addRow(table, row):
    global numrows
    numrows += 1
    bgcolor = ('#E0FFFF', '#E6E6FA')[numrows % 2]
    ac_sv = tk.StringVar()
    ac_sv_list.append(ac_sv)
    user_sv = tk.StringVar()
    user_sv_list.append(user_sv)
    pass_sv = tk.StringVar()
    pass_sv_list.append(pass_sv)
    comments_sv = tk.StringVar()
    comments_sv_list.append(comments_sv)
    updt_bv = tk.BooleanVar()
    updt_bv_list.append(updt_bv)
    del_bv = tk.BooleanVar()
    del_bv_list.append(del_bv)

    account = tk.Entry(table, textvariable=ac_sv)
    account.insert(0, row['Account'])
    account.grid(row=numrows, column=0, sticky="ew")
    account.configure({"background": bgcolor})
    ac_sv.trace("w", lambda name, index, mode, var=updt_bv: callback(var))

    username = tk.Entry(table, textvariable=user_sv)
    username.insert(0, row['Username'])
    username.grid(row=numrows, column=1, sticky="ew")
    username.configure({"background": bgcolor})
    user_sv.trace("w", lambda name, index, mode, var=updt_bv: callback(var))

    password = tk.Entry(table, textvariable=pass_sv)
    password.insert(0, row['Password'])
    password.grid(row=numrows, column=2, sticky="ew")
    password.configure({"background": bgcolor})
    pass_sv.trace("w", lambda name, index, mode, var=updt_bv: callback(var))

    comments = tk.Entry(table, textvariable=comments_sv)
    comments.insert(0, row['Comments'])
    comments.grid(row=numrows, column=3, sticky="ew")
    comments.configure({"background": bgcolor})
    comments_sv.trace("w", lambda name, index, mode, var=updt_bv: callback(var))

    up_btn = tk.Checkbutton(table, variable=updt_bv, onvalue=True, offvalue=False)
    up_btn.grid(row=numrows, column=4, sticky="ew")

    del_btn = tk.Checkbutton(table, variable=del_bv, onvalue=True, offvalue=False)
    del_btn.grid(row=numrows, column=5, sticky="ew")
    return

def addBtnClicked(table):
    print("ADD button clicked")
    row = {'Account':'', 'Username':'', 'Password':'', 'Comments':''}
    addRow(table, row)


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
    add_btn = add_btn = tk.Button(root, text='ADD', command=lambda: addBtnClicked(table))
    add_btn.pack(side=tk.LEFT)
    root.mainloop()
