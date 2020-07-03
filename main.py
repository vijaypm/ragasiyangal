from tkinter import *
import tkinter.ttk as ttk
import csv

def createHeader():
    label = Label(
        text="Hello, Tkinter",
        fg="black",  # Set the text color to white
        bg="lavender"  # Set the background color to black
    )
    label.pack()

def createTable(window):
    TableMargin = Frame(window, width=500)
    TableMargin.pack(side=TOP)
    scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
    scrollbary = Scrollbar(TableMargin, orient=VERTICAL)
    tree = ttk.Treeview(TableMargin, columns=("Account", "Username", "Password", "Comments"),
                        height=400, selectmode="extended",
                        yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
    scrollbary.config(command=tree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)
    scrollbarx.config(command=tree.xview)
    scrollbarx.pack(side=BOTTOM, fill=X)
    tree.heading('Account', text="Account", anchor=W)
    tree.heading('Username', text="Username", anchor=W)
    tree.heading('Password', text="Password", anchor=W)
    tree.heading('Comments', text="Comments", anchor=W)
    tree.column('#0', stretch=NO, minwidth=0, width=0)
    tree.column('#1', stretch=NO, minwidth=0, width=200)
    tree.column('#2', stretch=NO, minwidth=0, width=200)
    tree.column('#3', stretch=NO, minwidth=0, width=300)
    tree.pack()
    with open('ids.csv') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            account = row['Account']
            username = row['Username']
            password = row['Password']
            comments = row['Comments']
            tree.insert("", 0, values=(account, username, password, comments))

def setupWindow():
    window = Tk()
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
    createTable(root)
    root.mainloop()
