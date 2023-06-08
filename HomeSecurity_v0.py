import cv2
import tkinter as tk
from PIL import Image, ImageTk

class MotionDetectionApp:
    def __init__(self, video_source=0):
        self.root = tk.Tk()
        self.root.title("DLSP Home Security")
        
        # Create a label widget for the title
        title_label = tk.Label(self.root, text="DLSP Home Security", font=("Helvetica", 16), pady=10)
        title_label.pack()
        
        # Create a label widget for the canvas
        canvas_label = tk.Label(self.root, text="Video Feed")
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

# Create an instance of the MotionDetectionApp class
app = MotionDetectionApp()
