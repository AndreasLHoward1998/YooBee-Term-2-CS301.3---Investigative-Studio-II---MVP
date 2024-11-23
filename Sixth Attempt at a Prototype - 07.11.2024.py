import tkinter as tk
from tkinter import ttk, messagebox
from neurosity import NeurositySDK
from dotenv import load_dotenv
import os
import csv
from datetime import datetime

# Load environment variables
load_dotenv()

# Load user list from file
def load_users():
    users = {}
    with open("User_List.txt", "r") as file:
        for line in file:
            if "Username" in line and "Password" in line:
                parts = line.strip().split()
                username = parts[1]
                password = parts[3]
                users[username] = password
    return users

# Initialize user list and current user variable
users = load_users()

# Tkinter setup
root = tk.Tk()
root.title("Multi-Screen Display")
root.geometry("400x600")

# Initialize user list and current user variable
current_user = tk.StringVar(value="Guest")

# Neurosity data collector setup
class NeurosityDataCollector:
    def __init__(self):
        self.neurosity = NeurositySDK({
            "device_id": os.getenv("NEUROSITY_DEVICE_ID")
        })
        self.neurosity.login({
            "email": os.getenv("NEUROSITY_EMAIL"),
            "password": os.getenv("NEUROSITY_PASSWORD")
        })
        self.data = []
        self.session_active = False

    def start_session(self):
        """Starts data collection"""
        if not self.session_active:
            self.session_active = True
            self.data = []
            self.unsubscribe = self.neurosity.brainwaves_raw(self.collect_data)
            print("Data collection started.")

    def collect_data(self, data):
        """Collects incoming data into a list"""
        if self.session_active:
            self.data.append(data)

    def stop_session(self):
        """Stops data collection and saves to a CSV file"""
        if self.session_active:
            self.unsubscribe()  # Stop data collection
            self.session_active = False
            filename = f"Data_Collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "brainwave_data"])  # Adjust columns as needed
                for entry in self.data:
                    writer.writerow([entry['timestamp'], entry['value']])  # Adjust data keys as needed
            print(f"Data saved to {filename}")
            self.data = []  # Clear the data after saving

# Initialize data collector instance
data_collector = NeurosityDataCollector()

# Tkinter setup
# root = tk.Tk()
# root.title("Multi-Screen Display")
# root.geometry("400x600")

# Main screen setup
main_screen = tk.Frame(root, bg="#1d5899")
main_screen.pack(fill="both", expand=True)

# Function to display current user on each screen
def display_current_user(frame):
    user_label = tk.Label(frame, text=f"Logged in as: {current_user.get()}", bg="#1d5899", fg="#a0e4cb", font=("Arial", 10))
    user_label.place(relx=0.02, rely=0.02)

def open_screen(bg_color="#1d5899", start_session=False):
    """Generic function to open a new screen with specified background color and optional session start"""
    main_screen.pack_forget()
    screen = tk.Frame(root, bg=bg_color)
    screen.pack(fill="both", expand=True)

    display_current_user(screen)

    # Back button to return to main menu
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen), bg="#a0e4cb", font=("Arial", 10))
    back_button.place(relx=0.5, rely=0.9, anchor="center")

    if start_session:
        data_collector.start_session()

def open_user_screen():
    """Open the 'Current User/Guest' screen with login functionality"""
    main_screen.pack_forget()
    screen = tk.Frame(root, bg="#1d5899")
    screen.pack(fill="both", expand=True)

    display_current_user(screen)

    # Username entry
    username_entry = tk.Entry(screen, font=("Arial", 12))
    username_entry.insert(0, "Username")
    username_entry.bind("<FocusIn>", lambda event: username_entry.delete(0, tk.END))
    username_entry.place(relx=0.5, rely=0.3, anchor="center")

    # Password entry
    password_entry = tk.Entry(screen, font=("Arial", 12), show="*")
    password_entry.insert(0, "Password")
    password_entry.bind("<FocusIn>", lambda event: password_entry.delete(0, tk.END))
    password_entry.place(relx=0.5, rely=0.4, anchor="center")

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        if username not in users:
            messagebox.showerror("Error", "Username is incorrect")
        elif users[username] != password:
            messagebox.showerror("Error", "Password is incorrect")
        else:
            current_user.set(username)
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            show_main_screen(screen)

    # Login button
    login_button = tk.Button(screen, text="Login", command=validate_login, bg="#a0e4cb", font=("Arial", 12))
    login_button.place(relx=0.5, rely=0.5, anchor="center")

    # Back button
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen), bg="#a0e4cb", font=("Arial", 10))
    back_button.place(relx=0.5, rely=0.6, anchor="center")

def open_progress_screen():
    """Function to open the 'Progress' screen with specified metrics and layout"""
    main_screen.pack_forget()
    screen = tk.Frame(root, bg="#1d5899")
    screen.pack(fill="both", expand=True)

    display_current_user(screen)

    # Back button
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen), bg="#a0e4cb")
    back_button.place(relx=0.5, rely=0.1, anchor="n")

    # Metrics frame with outline
    metrics_frame = tk.Frame(screen, bg="#1d5899", bd=2, relief="solid", highlightbackground="#a0e4cb", highlightthickness=2)
    metrics_frame.place(relx=0.5, rely=0.35, relwidth=0.8, anchor="n")

    # Metrics data
    metrics = [
        ("• Concentration", "42%"),
        ("• Engagement", "73%"),
        ("• Memory Commitment", "65%"),
        ("• Distractions", "30%")
    ]

    # Display metrics
    for i, (metric, value) in enumerate(metrics):
        label = tk.Label(metrics_frame, text=metric, bg="#1d5899", fg="#a0e4cb", anchor="w", font=("Arial", 12))
        label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
        value_label = tk.Label(metrics_frame, text=value, bg="#1d5899", fg="#a0e4cb", anchor="e", font=("Arial", 12))
        value_label.grid(row=i, column=1, sticky="e", padx=10, pady=5)

def open_settings_screen():
    """Function to open the 'Settings' screen with toggle switches and dropdown menus"""
    main_screen.pack_forget()
    screen = tk.Frame(root, bg="#1d5899")
    screen.pack(fill="both", expand=True)

    display_current_user(screen)

    # Back button
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen), bg="#a0e4cb")
    back_button.place(relx=0.5, rely=0.1, anchor="n")

    # Settings frame with outline
    settings_frame = tk.Frame(screen, bg="#1d5899", bd=2, relief="solid", highlightbackground="#a0e4cb", highlightthickness=2)
    settings_frame.place(relx=0.5, rely=0.35, relwidth=0.8, anchor="n")

    # Toggle switches and dropdown menu settings
    settings = [
        ("• Audio", "toggle"),
        ("• Colour Lock", "toggle"),
        ("• Colour Blind", "dropdown"),
        ("• Document Type", "dropdown")
    ]

    # State variables for toggles and dropdowns
    audio_var = tk.BooleanVar(value=False)
    color_lock_var = tk.BooleanVar(value=False)
    color_blind_var = tk.StringVar(value="Red")
    document_type_var = tk.StringVar(value="AI")

    for i, (setting, setting_type) in enumerate(settings):
        label = tk.Label(settings_frame, text=setting, bg="#1d5899", fg="#a0e4cb", anchor="w", font=("Arial", 12))
        label.grid(row=i, column=0, sticky="w", padx=10, pady=5)

        if setting_type == "toggle":
            # Toggle switch for Audio and Colour Lock
            toggle = tk.Checkbutton(settings_frame, variable=audio_var if setting == "• Audio" else color_lock_var,
                                    bg="#1d5899", activebackground="#1d5899", onvalue=True, offvalue=False)
            toggle.grid(row=i, column=1, sticky="e", padx=10, pady=5)

        elif setting_type == "dropdown":
            # Dropdown menu for Colour Blind and Document Type
            options = ["Red", "Yellow", "Green", "Blue"] if setting == "• Colour Blind" else ["AI", "English", "Math", "Science"]
            dropdown = ttk.Combobox(settings_frame, values=options, textvariable=color_blind_var if setting == "• Colour Blind" else document_type_var)
            dropdown.grid(row=i, column=1, sticky="e", padx=10, pady=5)
            dropdown.config(width=10)
            dropdown.set(options[0])  # Set default value

def open_feedback_screen():
    """Open the 'Feedback' screen with a text box, submit button, and back button"""
    main_screen.pack_forget()
    screen = tk.Frame(root, bg="#1d5899")
    screen.pack(fill="both", expand=True)

    display_current_user(screen)

    # Textbox for user feedback
    feedback_text = tk.Text(screen, width=40, height=10, wrap="word", font=("Arial", 12))
    feedback_text.place(relx=0.5, rely=0.4, anchor="center")

    def submit_feedback():
        feedback = feedback_text.get("1.0", tk.END).strip()
        if feedback:
            with open("feedback.txt", "a") as file:
                file.write(f"{datetime.now()}: {feedback}\n")
            print("Feedback submitted.")
        show_main_screen(screen)

    # Submit and Back buttons
    submit_button = tk.Button(screen, text="Submit", command=submit_feedback, bg="#a0e4cb", font=("Arial", 12))
    submit_button.place(relx=0.5, rely=0.6, anchor="center")
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen), bg="#a0e4cb", font=("Arial", 10))
    back_button.place(relx=0.5, rely=0.7, anchor="center")

def show_main_screen(screen):
    """Return to the main screen and stop data collection if active"""
    screen.pack_forget()
    data_collector.stop_session()
    main_screen.pack(fill="both", expand=True)

# Configure buttons for the main screen
button_configs = [
    ("Current User/Guest", "#1d5899"),
    ("Start Session", "#1d5899", True),
    ("Progress", "#1d5899"),
    ("Feedback", "#1d5899"),
    ("Settings", "#1d5899"),
]

for idx, (text, color, *args) in enumerate(button_configs):
    start_session = args[0] if args else False
    command = open_user_screen if text == "Current User/Guest" else (open_feedback_screen if text == "Feedback" else (open_progress_screen if text == "Progress" else (open_settings_screen if text == "Settings" else lambda color=color, start_session=start_session: open_screen(color, start_session))))
    button = tk.Button(main_screen, text=text, width=20, height=2, command=command)
    button.pack(pady=10)

# Add "Exit" button
exit_button = tk.Button(main_screen, text="Exit", width=20, height=2, command=root.quit)
exit_button.pack(pady=20)

# Run the application
root.mainloop()