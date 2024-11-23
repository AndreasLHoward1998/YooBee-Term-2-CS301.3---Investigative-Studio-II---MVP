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
from scipy import stats
from colorsys import hls_to_rgb
import time

# Sample AI Document Text for Document Display
def get_ai_document():
    return """
    This is a simple explanation of a Recurrent Neural Network (RNN).
    RNNs are a type of artificial intelligence that learns to understand patterns over time.
    They remember what they learned from past data to make predictions about new data.
    Think of it like remembering a favorite story and knowing what will happen next!
    """

class ColorState:
    def __init__(self):
        self.bg_color = "#f0f0f0"
        self.fg_color = "#333333"
        
    def update_colors(self, bg, fg):
        self.bg_color = bg
        self.fg_color = fg

color_state = ColorState()

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

class BrainStateAnalyzer:
    def __init__(self):
        # Thresholds based on typical EEG patterns
        self.thresholds = {
            'focus': {'alpha': 0.3, 'beta': 0.4, 'theta': 0.2, 'gamma': 0.3},
            'concentration': {'beta': 0.35, 'theta': 0.25},
            'engagement': {'beta': 0.4, 'gamma': 0.3},
            'enjoyment': {'alpha': 0.35, 'gamma': 0.25},
            'memory': {'theta': 0.3, 'gamma': 0.35},
            'distraction': {'theta': 0.4, 'alpha': 0.35}
        }
        
        # Moving windows for trend analysis
        self.window_size = 10
        self.history = {
            'focus': [], 'concentration': [], 'engagement': [],
            'enjoyment': [], 'memory': [], 'distraction': []
        }
        
        # Modified color ranges for better visibility
        self.color_ranges = {
            'hue': (180, 240),  # Blue spectrum
            'lightness': (0.6, 0.95),  # Increased contrast
            'saturation': (0.15, 0.35)  # Slightly more saturated
        }
        
        self.current_colors = {
            'text': '#000000',
            'background': '#FFFFFF'
        }
        
        self.last_update = time.time()
        self.color_transition_delay = 1.0  # Reduced delay for more responsive updates
    
    def analyze_brain_state(self, alpha, beta, theta, gamma):
        """Analyze current brain state using normalized wave values."""
        # Normalize input values
        total = alpha + beta + theta + gamma
        if total == 0:
            return None
            
        norm_alpha = alpha / total
        norm_beta = beta / total
        norm_theta = theta / total
        norm_gamma = gamma / total
        
        # Calculate mental states using weighted combinations
        states = {
            'focus': (norm_beta * 0.4 + norm_gamma * 0.3) / (norm_theta * 0.3),
            'concentration': norm_beta / (norm_theta + 0.1),
            'engagement': (norm_beta + norm_gamma) / (norm_alpha + norm_theta),
            'enjoyment': (norm_alpha + norm_gamma) / 2,
            'memory': (norm_theta + norm_gamma) / 2,
            'distraction': (norm_theta + norm_alpha) / (norm_beta + 0.1)
        }
        
        # Update history
        for state, value in states.items():
            self.history[state].append(value)
            if len(self.history[state]) > self.window_size:
                self.history[state].pop(0)
        
        return states
    
    def get_state_trends(self, states):
        """Calculate trends for each mental state."""
        trends = {}
        for state, values in self.history.items():
            if len(values) >= 3:  # Minimum required for trend analysis
                slope, _, _, _, _ = stats.linregress(range(len(values)), values)
                trends[state] = slope
            else:
                trends[state] = 0
        return trends
    
    def optimize_colors(self, states, trends):
        """Generate optimal colors based on brain states and trends."""
        if not states or time.time() - self.last_update < self.color_transition_delay:
            return self.current_colors
        
        # Calculate base hue based on mental states
        focus_factor = max(0.1, min(0.9, states.get('focus', 0.5)))
        concentration_factor = max(0.1, min(0.9, states.get('concentration', 0.5)))
    
        # Adjust hue based on cognitive state
        hue = self.color_ranges['hue'][0] + (
            (self.color_ranges['hue'][1] - self.color_ranges['hue'][0]) *
            ((focus_factor + concentration_factor) / 2)
        )
    
        # Adjust lightness based on engagement and enjoyment
        lightness = self.color_ranges['lightness'][0] + (
            (self.color_ranges['lightness'][1] - self.color_ranges['lightness'][0]) *
            ((states.get('engagement', 0.5) + states.get('enjoyment', 0.5)) / 2)
        )

        # Adjust saturation based on memory commitment and distraction
        saturation = self.color_ranges['saturation'][0] + (
            (self.color_ranges['saturation'][1] - self.color_ranges['saturation'][0]) *
            (states.get('memory', 0.5) / (states.get('distraction', 0.1) + 0.1))
        )

        # Convert HLS to RGB and then to hex
        rgb = hls_to_rgb(hue/360, lightness, saturation)
        background_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)
        )

        # Calculate contrasting text color
        text_color = '#000000' if lightness > 0.5 else '#FFFFFF'

        self.current_colors = {
            'text': text_color,
            'background': background_color
        }

        # Update the global color state
        color_state.update_colors(background_color, text_color)

        self.last_update = time.time()
        return self.current_colors
    
    def get_optimization_feedback(self, states, trends):
        """Generate feedback about current optimization state."""
        feedback = {
            'status': 'optimal',
            'suggestions': []
        }
        
        # Check for suboptimal conditions
        if states['distraction'] > self.thresholds['distraction']['theta']:
            feedback['status'] = 'needs_improvement'
            feedback['suggestions'].append('High distraction detected. Consider taking a short break.')
            
        if states['focus'] < self.thresholds['focus']['beta']:
            feedback['status'] = 'needs_improvement'
            feedback['suggestions'].append('Focus could be improved. Try deep breathing.')
            
        if states['engagement'] < self.thresholds['engagement']['beta']:
            feedback['status'] = 'needs_improvement'
            feedback['suggestions'].append('Engagement is low. Consider interactive elements.')
            
        return feedback

brain_analyzer = BrainStateAnalyzer()

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

    # Start session if applicable
    if start_session:
        data_collector.start_session()

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
    document_text = tk.Text(
        screen,
        wrap="word",
        font=("Arial", 10),
        bg=color_state.bg_color,  # Changed from bg_color
        fg=color_state.fg_color,  # Changed from fg_color
        height=10,
        width=40
    )
    document_text.insert("1.0", get_ai_document())
    document_text.config(state="disabled")
    document_text.place(relx=0.5, rely=0.5, anchor="center")

    # Start the data collection session
    data_collector.start_session()

    def update_display_optimization():
        """Updates the display colors based on brain state analysis"""
        if data_collector.session_active:
            # Get current brain states
            states = brain_analyzer.analyze_brain_state(
                data_collector.alpha_waves,
                data_collector.beta_waves,
                data_collector.theta_waves,
                data_collector.gamma_waves
            )
        
            if states:
                # Get trends and optimal colors
                trends = brain_analyzer.get_state_trends(states)
                colors = brain_analyzer.optimize_colors(states, trends)

                # Update document text colors using current color state
                document_text.configure(
                    fg=color_state.fg_color,
                    bg=color_state.bg_color
                )

                # Force update
                document_text.update_idletasks()

            # Schedule next update
            screen.after(100, update_display_optimization)  # Reduced delay for more responsive updates

    # Start the optimization updates
    update_display_optimization()

    # Add periodic update for the brainwave display
    def periodic_update():
        if data_collector.session_active:
            update_brainwave_display(
                screen,
                data_collector.alpha_waves,
                data_collector.beta_waves,
                data_collector.theta_waves,
                data_collector.gamma_waves
            )
            screen.after(500, periodic_update)

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
    ("Current User/Guest", "#1d5899", open_user_screen),
    ("Start Session", "#1d5899", open_start_session_screen),  # Explicitly assign the correct function
    ("Progress", "#1d5899", open_progress_screen),
    ("Feedback", "#1d5899", open_feedback_screen),
    ("Settings", "#1d5899", open_settings_screen),
]

for idx, (text, color, command) in enumerate(button_configs): # Removed he logic that was dynamically assigning functions (lambda). 
    button = tk.Button(main_screen, text=text, width=20, height=2, command=command) #Each button gets its command directly from the button_configs list.
    button.pack(pady=10) # Every button now behaves exactly as expected, and there's no need for redundant code in multiple functions.

# Add "Exit" button
exit_button = tk.Button(main_screen, text="Exit", width=20, height=2, command=root.quit)
exit_button.pack(pady=20)

# Run the application
root.mainloop() # Make SURE there is only ONE instance of the program running!!!! Try removing specific colours from program to attempt to fix it!