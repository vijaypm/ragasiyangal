'''
A Python Exercise: Reading CSV File & Tkinter Implementation
Including the subjects: Grid Layout, Tk Variables and Binding
'''
import Tkinter as tk
import csv

CSV_FILE = "users.csv"

# Functions
def popup(title, msg):
    '''Open popup window with title and msg'''
    w = tk.Toplevel(root)
    w.title(title)
    w.minsize(200, 200)
    tk.Label(w, text=msg).pack()
    tk.Button(w, text="Close", command=w.destroy).pack(pady=10)
    w.bind("<Return>", lambda f: w.destroy())

def read_from_file():
    '''Read csv file and return a list like: [[username, password, count]]'''
    try:
        with open(CSV_FILE, 'rb') as f:
            users = []
            reader = csv.reader(f)
            for row in reader:
                row[2] = int(row[2]) # Make the count an integer so it can increase later
                users.append(row)
            return users
    except IOError:
        popup("Error", "File not found!")

def write_to_file(users):
    '''Get a list of all users and write it to the csv file'''
    with open(CSV_FILE, 'wb') as f:
        writer = csv.writer(f)
        for row in users:
            row[2] = str(row[2])
        writer.writerows(users)

class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.pack(anchor="w")

        # Labels
        tk.Label(self, text="Username:").grid(sticky="w")
        tk.Label(self, text="Password:").grid(row=1, sticky="e")

        # Entries
        self.n_string = tk.StringVar()
        self.p_string = tk.StringVar()
        name = tk.Entry(self, textvariable=self.n_string, width=30)
        passw = tk.Entry(self, textvariable=self.p_string, show='*', width=20)
        name.grid(row=0, column=1, sticky="we")
        passw.grid(row=1, column=1, sticky="we")

        # Check Button
        self.check_var = tk.BooleanVar()
        check = tk.Checkbutton(self, text="Count Login attempts", variable=self.check_var)
        check.grid(row=2, column=1, sticky="w")

        # Login Button
        login = tk.Button(self, text="Login", command=self.login)
        login.grid(row=2, column=1, sticky="e")

        # Binding
        self.master.bind("<Return>", self.login)

    def login(self, event=None):
        '''Login attempt'''
        users  = read_from_file()
        if not users:
            return
        for row in users:
            if row[0] == self.n_string.get() and row[1] == self.p_string.get():
                msg =  "Welcome %s!\n\nYour login count is %d" % (row[0], row[2])
                popup("Welcome", msg)
                if self.check_var.get(): # Check if "Count Login attempts" button is checked
                    row[2] += 1 # add +1 login count
                    write_to_file(users)
                break
            elif row[0] == self.n_string.get():
                print("Password incorrect.")
                break
        else: # If there isn't a match of the username
            print("User name incorrect!")


# GUI settings
root = tk.Tk()
app = App(root)
root.title("Login Form")
root.minsize(200, 200)

# Initalize GUI
root.mainloop()