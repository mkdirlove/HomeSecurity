import cv2
import tkinter as tk
from PIL import Image, ImageTk
import sqlite3
from tkinter import messagebox

# Create a connection to the SQLite database
conn = sqlite3.connect("user_credentials.db")
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        birthday TEXT
    )
""")
conn.commit()

class HomePage:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Homepage")

        # Create a label widget for the image or logo
        image = tk.PhotoImage(file="logo.png")  # Replace "logo.png" with the path to your image file
        image_label = tk.Label(self.root, image=image)
        image_label.pack()

        # Create a label widget for the text
        text_label = tk.Label(self.root, text="Welcome to Home Security!", font=("Helvetica", 18), pady=10)
        text_label.pack()

        # Create login and signup buttons
        login_button = tk.Button(self.root, text="Login", font=("Helvetica", 12), width=10, command=self.login)
        login_button.pack(pady=5)

        signup_button = tk.Button(self.root, text="Signup", font=("Helvetica", 12), width=10, command=self.signup)
        signup_button.pack(pady=5)

        self.root.mainloop()

    def login(self):
        # Destroy the homepage window
        self.root.destroy()

        # Create an instance of the LoginSignupApp class
        login_app = LoginSignupApp()

    def signup(self):
        # Destroy the homepage window
        self.root.destroy()

        # Create an instance of the LoginSignupApp class with the signup flag set to True
        signup_app = LoginSignupApp(signup=True)

class LoginSignupApp:
    def __init__(self, signup=False):
        self.root = tk.Tk()
        self.root.title("Login/Signup")

        self.signup = signup

        # Create a label widget for the title
        if self.signup:
            title_label = tk.Label(self.root, text="Signup", font=("Helvetica", 16), pady=10)
        else:
            title_label = tk.Label(self.root, text="Login", font=("Helvetica", 16), pady=10)
        title_label.pack()

        # Create entry widgets for username, password, and birthday
        username_label = tk.Label(self.root, text="Username:")
        username_label.pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        password_label = tk.Label(self.root, text="Password:")
        password_label.pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        if self.signup:
            birthday_label = tk.Label(self.root, text="Birthday:")
            birthday_label.pack()
            self.birthday_entry = tk.Entry(self.root)
            self.birthday_entry.pack()

        # Create login or signup button
        if self.signup:
            action_button = tk.Button(self.root, text="Signup", command=self.perform_signup)
        else:
            action_button = tk.Button(self.root, text="Login", command=self.perform_login)
        action_button.pack(pady=5)

        self.root.mainloop()

    def perform_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username and password match a record in the database
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            self.show_message2("Login successful!")
            self.root.destroy()
            # Create an instance of the MotionDetectionApp class
            app = MotionDetectionApp()
        else:
            self.show_message2("Invalid username or password.")

    def show_message2(self, message):
        # Create a message box to display the message
        result = messagebox.showinfo("Message", message)

        # Redirect to the MotionDetectionApp if OK button is pressed
        if result == 'ok':
            self.root.destroy()
            app = MotionDetectionApp()

    def perform_signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        birthday = self.birthday_entry.get()
    
        # Check if the username already exists in the database
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
    
        if existing_user:
            self.show_message("Username already exists. Please choose a different username.")
        else:
            # Insert the user data into the users table
            cursor.execute("INSERT INTO users (username, password, birthday) VALUES (?, ?, ?)", (username, password, birthday))
            conn.commit()
    
            self.show_message("Signup successful!")
    
    def show_message(self, message):
        # Create a message box to display the message
        result = messagebox.showinfo("Message", message)
    
        # Redirect to the LoginPage if OK button is pressed
        if result == 'ok':
            self.root.destroy()
            homepage = HomePage()
            

    def __del__(self):
        # Close the database connection when the application is closed
        conn.close()


class MotionDetectionApp:
    def __init__(self, video_source=0):
        self.root = tk.Tk()
        self.root.title("Home Security")
        
        # Create a label widget for the title
        title_label = tk.Label(self.root, text="Home Security", font=("Helvetica", 16), pady=10)
        title_label.pack()
        
        # Create a label widget for the canvas
        canvas_label = tk.Label(self.root, text="Live Video Feed")
        canvas_label.pack()
        
        # Open the video source
        self.video = cv2.VideoCapture(video_source)
        
        # Create a canvas to display the video
        self.canvas = tk.Canvas(self.root, width=self.video.get(3), height=self.video.get(4))
        self.canvas.pack()
        
        # Initialize the previous frame
        self.prev_frame = None
        
        # Create a dictionary to store labels for each motion region
        self.motion_labels = {}
        
        # Start the motion detection
        self.detect_motion()
        
        self.root.mainloop()
    
    def detect_motion(self):
        # Read a frame from the video source
        ret, frame = self.video.read()
        
        if ret:
            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Blur the frame to reduce noise
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            if self.prev_frame is None:
                # Set the previous frame for the first iteration
                self.prev_frame = gray
            else:
                # Compute the absolute difference between the current and previous frame
                frame_delta = cv2.absdiff(self.prev_frame, gray)
                
                # Threshold the delta image to highlight regions with significant changes
                thresh = cv2.threshold(frame_delta, 30, 255, cv2.THRESH_BINARY)[1]
                
                # Apply image dilation to fill in the holes
                thresh = cv2.dilate(thresh, None, iterations=2)
                
                # Find contours of the threshold image
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Create a dictionary to store the active motion regions
                active_motion_regions = {}
                
                # Process the contours
                for contour in contours:
                    if cv2.contourArea(contour) > 500:
                        # Draw a rectangle around the contour
                        (x, y, w, h) = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        
                        # Add the motion region to the active motion regions dictionary
                        active_motion_regions[(x, y, w, h)] = True
                        
                        # Check if a label already exists for this motion region
                        if (x, y, w, h) not in self.motion_labels:
                            # Create a new label for this motion region
                            label_text = "Motion Detected!"
                            label = tk.Label(self.root, text=label_text, fg='red')
                            label.place(x=x, y=y - 20)
                            self.motion_labels[(x, y, w, h)] = label
            
                # Remove labels for inactive motion regions
                inactive_motion_regions = set(self.motion_labels.keys()) - set(active_motion_regions.keys())
                for region in inactive_motion_regions:
                    label = self.motion_labels[region]
                    label.destroy()
                    del self.motion_labels[region]
            
                # Convert the OpenCV image to PIL format
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                
                # Clear the canvas before updating with the new image
                self.canvas.delete("all")
                
                # Update the canvas with the new image
                self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
                self.canvas.image = image
                
                # Update the previous frame
                self.prev_frame = gray
        
        # Schedule the next motion detection iteration
        self.root.after(10, self.detect_motion)

    def __del__(self):
        # Release the video source and destroy the root window
        self.video.release()
        self.root.destroy()

# Create an instance of the HomePage class
homepage = HomePage()
