import tkinter as tk
from tkinter import ttk, messagebox
from neurosity import NeurositySDK
from dotenv import load_dotenv
import os
import csv
from datetime import datetime
import numpy as np
import tkinter as tk
from scipy.signal import butter, filtfilt, lfilter

# Sample AI Document Text for Document Display
def get_ai_document():
    return """
    This is a simple explanation of a Recurrent Neural Network (RNN).
    RNNs are a type of artificial intelligence that learns to understand patterns over time.
    They remember what they learned from past data to make predictions about new data.
    Think of it like remembering a favorite story and knowing what will happen next!
    """

# Helper functions for bandpass filters
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)

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
        
        # Initialize brainwave variables
        self.alpha_waves = 0.0
        self.beta_waves = 0.0
        self.theta_waves = 0.0
        self.gamma_waves = 0.0

    def start_session(self):
        """Starts data collection"""
        if not self.session_active:
            self.session_active = True
            self.data = []
            self.unsubscribe = self.neurosity.brainwaves_raw(self.collect_data)
            print("Data collection started.")

    def collect_data(self, data):
        """Collects incoming data into a list and calculates brainwaves."""
        if self.session_active:
            self.data.append(data)
            self.calculate_brain_waves(data['data'])
        
            # Print the calculated brainwave values
            print(f"Alpha: {self.alpha_waves:.2f}, Beta: {self.beta_waves:.2f}, Theta: {self.theta_waves:.2f}, Gamma: {self.gamma_waves:.2f}")

    def calculate_brain_waves(self, eeg_data):
        """Calculates alpha, beta, theta, and gamma waves from EEG data."""
        sampling_rate = 256  # As defined in your 'info' section

        # Convert eeg_data to numpy array for filtering
        eeg_array = np.array(eeg_data)

        # Apply bandpass filters for each frequency band
        alpha_band = bandpass_filter(eeg_array, 8, 13, sampling_rate)
        beta_band = bandpass_filter(eeg_array, 13, 30, sampling_rate)
        theta_band = bandpass_filter(eeg_array, 4, 8, sampling_rate)
        gamma_band = bandpass_filter(eeg_array, 30, 50, sampling_rate)

        # Calculate power (mean square) of each band and update variables
        self.alpha_waves = np.mean(alpha_band ** 2)
        self.beta_waves = np.mean(beta_band ** 2)
        self.theta_waves = np.mean(theta_band ** 2)
        self.gamma_waves = np.mean(gamma_band ** 2)

    def stop_session(self):
        """Stops data collection and saves to a CSV file with specified columns."""
        if self.session_active:
            self.unsubscribe()  # Stop data collection
            self.session_active = False
            self.save_data_to_csv()  # Call the new save function
            self.data = []  # Clear the data after saving

    # New function to save data with specified format
    def save_data_to_csv(self):
        """Saves EEG data to CSV with custom columns, including the username stamp."""
        username = current_user.get() if current_user.get() else "Guest"
        
        filename = f"{username} - eeg_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        headers = ["Sample Count", "CP3", "C3", "F5", "PO3", "PO4", "F6", "C4", "CP4", "Marker Column", "Timestamp"]

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write header row
        
            for i, data_point in enumerate(self.data):
                sample_count = i % 32  # Cycles 0-31 for each set of samples
                eeg_values = data_point['data'][:8]  # First 8 values for EEG channels
                marker = ""  # Placeholder for marker column
                timestamp = int(datetime.now().timestamp() * 1000)  # Current time in milliseconds
            
                writer.writerow([sample_count] + eeg_values + [marker, timestamp])

        # Display an alert popup with the filename
        alert_popup(f"Data has been saved as {filename}")


# Function to show alert popup
def alert_popup(message):
    popup = tk.Toplevel()
    popup.title("Data Saved")
    label = tk.Label(popup, text=message, font=("Arial", 12))
    label.pack(pady=10, padx=10)
    ok_button = tk.Button(popup, text="OK", command=popup.destroy)
    ok_button.pack(pady=5)

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

def update_brainwave_display(screen, alpha, beta, theta, gamma):
    """Updates the brainwave display in the specified screen."""
    # Create a frame for the brainwave display if it doesn't already exist
    if not hasattr(screen, 'brainwave_display'):
        screen.brainwave_display = tk.Frame(screen, bg="#f0f0f0", bd=2, relief="solid")
        screen.brainwave_display.place(relx=0.8, rely=0.1, anchor="ne")

        # Add labels for brainwave metrics
        screen.alpha_label = tk.Label(screen.brainwave_display, text="Alpha: 0.00", font=("Arial", 10), bg="#f0f0f0")
        screen.alpha_label.pack(anchor="w")
        screen.beta_label = tk.Label(screen.brainwave_display, text="Beta: 0.00", font=("Arial", 10), bg="#f0f0f0")
        screen.beta_label.pack(anchor="w")
        screen.theta_label = tk.Label(screen.brainwave_display, text="Theta: 0.00", font=("Arial", 10), bg="#f0f0f0")
        screen.theta_label.pack(anchor="w")
        screen.gamma_label = tk.Label(screen.brainwave_display, text="Gamma: 0.00", font=("Arial", 10), bg="#f0f0f0")
        screen.gamma_label.pack(anchor="w")

    # Update labels with the latest brainwave data
    screen.alpha_label.config(text=f"Alpha: {alpha:.2f}")
    screen.beta_label.config(text=f"Beta: {beta:.2f}")
    screen.theta_label.config(text=f"Theta: {theta:.2f}")
    screen.gamma_label.config(text=f"Gamma: {gamma:.2f}")

def open_screen(bg_color="#1d5899", start_session=False):
    """Generic function to open a new screen with specified background color and optional session start"""
    main_screen.pack_forget()
    screen = tk.Frame(root, bg=bg_color)
    screen.pack(fill="both", expand=True)

    display_current_user(screen)

    # Back button to return to main menu
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen), bg="#a0e4cb", font=("Arial", 10))
    back_button.place(relx=0.5, rely=0.9, anchor="center")

    # Document display box for AI Document
    document_text = tk.Text(screen, wrap="word", font=("Arial", 10), bg="#f0f0f0", fg="#333333", height=10, width=40)
    document_text.insert("1.0", get_ai_document())  # Insert the document text from `get_ai_document`
    document_text.config(state="disabled")  # Make the text box read-only
    document_text.place(relx=0.5, rely=0.5, anchor="center")  # Adjust position as desired

    # Start session if applicable
    if start_session:
        data_collector.start_session()

    # Add a periodic update for the brainwave display
    def periodic_update():
        if data_collector.session_active:
            update_brainwave_display(
                screen,
                data_collector.alpha_waves,
                data_collector.beta_waves,
                data_collector.theta_waves,
                data_collector.gamma_waves
            )
            screen.after(500, periodic_update)  # Update every 500ms

    periodic_update()

def open_start_session_screen():
    """Function to open the 'Start Session' screen and begin data collection."""
    main_screen.pack_forget()
    screen = tk.Frame(root, bg="#1d5899")
    screen.pack(fill="both", expand=True)

    display_current_user(screen)

    # Back button to return to main menu
    back_button = tk.Button(screen, text="Back", command=lambda: show_main_screen(screen), bg="#a0e4cb", font=("Arial", 10))
    back_button.place(relx=0.5, rely=0.9, anchor="center")

    # Document display box for AI Document
    document_text = tk.Text(screen, wrap="word", font=("Arial", 10), bg="#f0f0f0", fg="#333333", height=10, width=40)
    document_text.insert("1.0", get_ai_document())  # Insert the document text from `get_ai_document`
    document_text.config(state="disabled")  # Make the text box read-only
    document_text.place(relx=0.5, rely=0.5, anchor="center")  # Adjust position as desired

    # Start the data collection session
    data_collector.start_session()

    # Add a periodic update for the brainwave display
    def periodic_update():
        if data_collector.session_active:
            update_brainwave_display(
                screen,
                data_collector.alpha_waves,
                data_collector.beta_waves,
                data_collector.theta_waves,
                data_collector.gamma_waves
            )
            screen.after(500, periodic_update)  # Update every 500ms

    periodic_update()

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
    ("Start Session", "#1d5899", open_start_session_screen),
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