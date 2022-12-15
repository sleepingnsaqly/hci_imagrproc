import os
import cv2
import sys
import numpy as np
import tkinter as tk
import customtkinter as ct
from tkinter import filedialog
import tkinter.scrolledtext as st
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Set the initial themes of the app window
ct.set_appearance_mode("Dark")
ct.set_default_color_theme(BASE_DIR + "\\themes.json")

class TextRedirector(object):
    # Handles console output to GUI
    def __init__(self, widget, tag= "stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag))
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        self.widget.update()

class App(ct.CTk):

    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        super().__init__()

        self.title("Image Processing using OpenCV")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.resizable(width=False, height=False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # call .on_closing when app gets closed
        self.iconbitmap(BASE_DIR + "\\poweredby24.ico")

        # =================== create two frames ===================

        #configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0,weight=1)

        self.frame_left = ct.CTkFrame(master=self, width=180, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = ct.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ================== frame left ==================

        #configure grid layout(1x11)

        self.frame_left.grid_rowconfigure(0, minsize=10) # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(8, weight=1) # empty row as spacing
        self.frame_left.grid_rowconfigure(9, minsize=20) # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10) # empty row with minsize as spacing

        self.lbl_menu = ct.CTkLabel(master=self.frame_left, text="Image Options", 
                                    text_font=("Roboto Medium", -16)) # font name and size in px
        self.lbl_menu.grid(row=1, column=0, pady=10, padx=10)
        self.cmd_edge = ct.CTkButton(master=self.frame_left, text="Edge Detection",
                                        command=self.edge_detection)
        self.cmd_edge.grid(row=2, column=0, pady=5, padx=20)

        self.cmd_gblur = ct.CTkButton(master=self.frame_left, text="Gaussian Blur",
                                        command=self.gaus_blur)
        self.cmd_gblur.grid(row=3, column=0, pady=5,padx=20)

        self.cmd_crop = ct.CTkButton(master=self.frame_left, text="Crop Image",
                                        command=self.crop_img)
        self.cmd_crop.grid(row=4, column=0, pady=5, padx=20)

        self.cmd_sharp = ct.CTkButton(master=self.frame_left, text= "Sharpen Image",
                                        command=self.sharpen_img)
        self.cmd_sharp.grid(row=5, column=0, pady=5, padx=20)

        self.cmd_camera = ct.CTkButton(master=self.frame_left, text= "Open Camera",
                                        command=self.open_camera)
        self.cmd_camera.grid(row=6, column=0, pady=5, padx=20)

        self.cmd_reset = ct.CTkButton(master=self.frame_left, text= "Reset Image",
                                        command=self.reset_img)
        self.cmd_reset.grid(row=7, column=0, pady=5, padx=20) 

        self.cmd_exit = ct.CTkButton(master=self.frame_left, text= "Exit", fg_color="red",
                                        command=self.exit_app)
        self.cmd_exit.grid(row=8, column=0, pady=5, padx=20)

        self.lbl_theme = ct.CTkLabel(master=self.frame_left, text="Window Theme:",
                                        text_font=("Roboto Medium", -12)) # font name and size in px
        self.lbl_theme.grid(row=9, column=0, pady=5, padx=10, sticky="s")

        self.opt_theme = ct.CTkOptionMenu(master=self.frame_left, values=["Light", "Dark", "System"],
                                        command=self.set_window_theme)
        self.opt_theme.grid(row=10, column=0, pady=5, padx=20, sticky="n")      

        # ================== frame_right ==================

        # configure layout (1x11)
        self.frame_right.grid_rowconfigure(0, minsize=10) # empty row with minsize as spacing
        self.frame_right.grid_rowconfigure(5, weight=1) # empty row as spacing 

        self.frame = np.random.randint(0,255,[100,100,3],dtype='uint8')
        self.frame_img = ImageTk.PhotoImage(Image.fromarray(self.frame))

        self.img_holder = ct.CTkLabel(master=self.frame_right, text="Image placeholder",
                                        bg_color="gray", text_font=("Roboto Medium", -14))                               
        self.img_holder.grid(row=0, column=0, columnspan=2, pady=15, padx=10, sticky= "we")

        self.status_area = st.ScrolledText(master=self.frame_right, width=73, height=7,
                                            wrap="word", font =("Roboto Medium", 10))
        self.status_area.grid(row=9, column=0, pady=10, padx=10, sticky= "nwe")
        self.status_area.tag_configure("stderr", foreground="#b22222")
        self.status_area.tag_configure("stdout", foreground="#000000")

        self.cmd_capture = tk.Button(master=self.frame_right, text="Capture", command=self.saveimg_prompt)
        self.cmd_capture.place(bordermode=tk.INSIDE, relx=0.3, rely=0.5, anchor=tk.CENTER, width=300, height=30)

        self.cmd_changecam = tk.Button(master=self.frame_right, text="Switch Camera", command=self.change_cam)
        self.cmd_changecam.place(bordermode=tk.INSIDE, relx=0.85, rely=0.1, anchor=tk.CENTER, width=120, height=30)

        self.txt_imgpath = ct.CTkEntry(master=self.frame_right, width=240, placeholder_text="Path to image file")
        self.txt_imgpath.grid(row=10, column=0, columnspan=2, pady=5, padx=10, sticky="swe")

        self.cmd_browse = ct.CTkButton(master=self.frame_right, text="Browse", command=self.browse_image)
        self.cmd_browse.grid(row=11, column=0, pady=10, padx=10, sticky="nw")

        #Manage redirection of console output to GUI
        sys.stdout = TextRedirector(self.status_area, "stdout")
        sys.stderr = TextRedirector(self.status_area, "stderr")

        #Default values/setup
        self.filename = ""
        self.cam_active = False
        self.on_capture = False
        self.cancel = False
        self.opt_theme.set("Dark")
        self.cam_button_stat(False)
        self.imgproc_btns('disabled')
        print("Browse and select picture to load for processing..")

    def browse_image(self):
        # Handles file browsing for image
        global img
        self.filename = filedialog.askopenfilename(initialdir="/",
                                            title="Select image to identify",
                                            filetypes=(("Image files", ".png .jpg .bmp"), ("All files", "*.*")))
                
        self.clear_status()
        self.cam_button_stat(False)
        if self.cam_active == True:
            self.cancel = True
            self.cam_active = False
            self.cap.release()
            cv2.destroyAllWindows()

        if self.on_capture == True:
            self.on_capture = False
            self.cmd_saveimg.place_forget()
            self.cmd_tryagain.place_forget()

        self.txt_imgpath.configure(textvariable="")
        self.txt_imgpath.insert(tk.END, self.filename)

        if self.filename != "":
            self.display_img(self.filename)
            self.imgproc_btns('normal')
        else:
            print("No image loaded for processing.")
            self.imgproc_btns('disabled')
        self.txt_imgpath.configure(state = 'disabled')

    def display_img(self, file_path):
        # Manage loading images to be displayed using label
        global imgtk
        self.clear_status()
        img = cv2.imread(file_path)
        orig_ht, orig_wt, chan = img.shape

        print('Image Height: \t\t', orig_ht)
        print('Image Width: \t\t', orig_wt)
        print('No. of Channels: \t\t', chan)

        # Resize image to fit display
        scale_percent = self.img_scale(orig_ht)
        width = int(img.shape[1] *  scale_percent / 100)
        height = int(img.shape[0] *  scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        # Rearrange colors
        blue,green,red = cv2.split(resized)
        resized = cv2.merge((red,green,blue))
        im = Image.fromarray(resized)
        imgtk = ImageTk.PhotoImage(image=im)

        self.img_holder.configure(image=imgtk)
        print('Resized Dimensions: ', resized.shape)

    def img_scale(self, orig_ht):
        # Scaling the image to fit in the tkinter form before displaying
        if orig_ht > 1700:
            scale = 16
        elif orig_ht > 1000 and orig_ht < 1700:
            scale = 19
        elif orig_ht > 699 and orig_ht < 999:
            scale = 45
        elif orig_ht > 500 and orig_ht < 700:
            scale = 50
        elif orig_ht > 211 and orig_ht < 500:
            scale = 65
        else:
            scale = 500
        return scale

    def edge_detection(self):
        # Manage edge detection to the loaded image
        global imgtk
        self.clear_status()
        info = "Edge detection is an iage processing technique to find "
        info += "boundaries of objects in the image. "
        print(info)

        #Read image from a file
        img  = cv2.imread(self.filename)

        #Resize image to fit display
        scale_percent = self.img_scale(img.shape[0])
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        edges = cv2.Canny(resized,100,200)

        im = Image.fromarray(edges)
        imgtk = ImageTk.PhotoImage(image=im) 

        print("Image edge detection using Canny() function.")
        self.img_holder.configure(image=imgtk)
        self.status_area.configure(state='disabled')
        self.cmd_reset.configure(state='normal')

    def gaus_blur(self):
        # Manage applying Gaussian BLur to theloaded image
        global imgtk
        self.clear_status()
        info = "Gaussian filter is used for image smoothing or "
        info += "reducing image noise."""

        # Read image from a file
        img =cv2.imread(self.filename)

        # Apply Gaussian Blur filter to the loaded image
        dst = cv2.GaussianBlur(img,(5,5),cv2.BORDER_DEFAULT)

        # Display input and output image
        cv2.imshow("Gaussian Smoothing", np.hstack((img,dst)))
        cv2.waitKey(0) # waits until a key is pressed
        cv2.destroyAllWindows() # destroys the window showing the image

    def crop_img(self):
        global imgtk
        info = "Cropping is used to get a particular part of an image."
        info += "To crop an image, you just need the coordinates from an "
        info += "image according to your area of interest."
        print(info)

        # Read image from a file
        img = cv2.imread(self.filename)

        # Set the rectangular portio of the image to be cropped
        hgt, wdt = img.shape[:2]
        start_row, start_col = int(hgt * .25), int(wdt * .25)
        end_row, end_col = int(hgt * .75), int(wdt * .75)
        cropped = img[start_row: end_row, start_col:end_col]

        cv2.imshow("Original", img)
        cv2.imshow("Cropped", cropped)

        cv2.waitKey(0) # waits until a key is pressed
        cv2.destroyAllWindows() # destroys the window showing the image

    def sharpen_img(self):
        # Manage sharpening to the loaded image
        global imgtk
        self.clear_status()
        info = "Sharpening image"

        # Read image from a file
        img =cv2.imread(self.filename)

        # Set the portion of the image to be sharpened
        kernel_sharpening = np.array([[-1,-1,-1,],
                            [-1,9,-1],
                            [-1,-1,-1]])
        dst = cv2.filter2D(img, -1, kernel_sharpening)

        # Display input and output image
        cv2.imshow("Image Sharpening", np.hstack((img,dst)))
        cv2.waitKey(0) # waits until a key is pressed
        cv2.destroyAllWindows() # destroys the window showing the image

    def open_camera(self):
        if self.cam_active == False:
            global prevImg
            self.imgproc_btns('disabled')
            self.cam_button_stat(True)
            self.cam_active = True
            self.cam_index = self.load_cam_index()
            self.clear_status()
            self.txt_imgpath.configure(textvariable="")
            print("Using camera feed to take pictures.")

            self.start_resize_cam()
            success, frame = self.cap.read()
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            # Assign camera feed/grames to an image holder
            prevImg = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=prevImg)
            self.img_holder.imgtk = imgtk
            self.img_holder.configure(image=imgtk)
            self.cmd_capture.focus()

            if not self.cancel:
                self.img_holder.after(10, self.show_frame)
        else:
            self.clear_status()
            print("Using camera feed to take pictures.")

    def load_cam_index(self):
        # Create and access file containing list of previously used camera
        self.cam_list = os.environ['ALLUSERSPROFILE'] + "WebcamCap.txt"
        try:
            f = open(self.cam_list, 'r')
            return int(f.readline())
        except:
            return 0

    def start_resize_cam(self):
        # Start capturing and resizing camera resolution
        self.cap = cv2.VideoCapture(self.cam_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv2.CAP_PROP_FPS, 25)

    def show_frame(self):
        # Continuously update image being loaded to a label
        global prevImg

        _, frame = self.cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

        prevImg = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=prevImg)
        self.img_holder.imgtk = imgtk
        self.img_holder.configure(image=imgtk)
        if not self.cancel:
            self.img_holder.after(10, self.show_frame)

    def saveimg_prompt(self):
        # Captured still image and ready for saving
        self.cancel = True
        self.on_capture = True

        self.cmd_capture.place_forget()
        self.cmd_saveimg = tk.Button(master=self.frame_right, text="Save Image", command=self.saveimg_exit)
        self.cmd_tryagain = tk.Button(master=self.frame_right, text="Try Again", command=self.retake_img)
        self.cmd_saveimg.place(anchor=tk.CENTER, relx=0.3, rely=0.5, width=110, height=30)
        self.cmd_tryagain.place(anchor=tk.CENTER, relx=0.65, rely=0.5, width=110, height=30)
        self.cmd_saveimg.focus()

    def change_cam(self, event=0, nextCam=-1):
        # Manage changing camera source
        if nextCam == -1:
            self.cam_index += 1
        else:
            self.cam_index = nextCam
        del(self.cap)
        self.start_resize_cam()

        # Try to get a frame, if it returns nothing
        success, frame = self.cap.read()
        if not success:
            self.cam_index = 0
            del(self.cap)
            self.start_resize_cam()

        # Add existing list of previously accessed camera to a file
        f = open(self.cam_list, "w")
        f.write(str(self.cam_index))
        f.close()

    def saveimg_exit(self):
        import glob
        global prevImg

        # Look for the occurence of the image file and file number to the filename.
        file_ctr = 0
        files = glob.glob(BASE_DIR + "\imageCap*.*", recursive=True)
        for file in files:
            file_ctr +=1

        if (len(sys.argv) < 2):
            filepath = BASE_DIR + "\imageCap{}.png".format(file_ctr)
        else:
            filepath = sys.argv[1]

        print ("File saved at " + filepath)

        # Resize image before saving
        basewidth = 600
        wpercent = (basewidth/float(prevImg.size[0]))
        hsize = int((float(prevImg.size[1])*float(wpercent)))
        prevImg = prevImg.resize((basewidth,hsize), Image.Resampling.LANCZOS)
        prevImg.save(filepath)

    def retake_img(self):
        # Returning to capturing another image from camera
        self.cancel = False
        self.cmd_saveimg.place_forget()
        self.cmd_tryagain.place_forget()
        self.cmd_capture.focus()

        self.bind('<Return>', self.saveimg_prompt)
        self.cmd_capture.place(bordermode=tk.INSIDE, relx=0.48, rely=0.5, anchor=tk.CENTER, width=300, height=30)
        self.img_holder.after(10, self.show_frame)

    def cam_button_stat(self, stat):
        # Managing necessary buttons for capturing image and changing camera source
        if stat == True:
            self.cmd_capture.place(bordermode=tk.INSIDE, relx=0.48, rely=0.5, anchor=tk.CENTER, width=300, height=30)
            self.cmd_capture.place(bordermode=tk.INSIDE, relx=0.84, rely=0.08, anchor=tk.CENTER, width=105, height=30)
        else:
            self.img_holder.configure(image="")
            self.cmd_capture.place_forget()
            self.cmd_changecam.place_forget()

    def imgproc_btns(self, stat):
        # Set the status of buttons
        self.cmd_edge.configure(state=stat)
        self.cmd_gblur.configure(state=stat)
        self.cmd_crop.configure(state=stat)
        self.cmd_sharp.configure(state=stat)
        self.cmd_reset.configure(state=stat)

    def reset_img(self):
        self.display_img(self.filename)

    def set_window_theme(self, new_theme):
        ct.set_appearance_mode(new_theme)

    def clear_status(self):
        self.status_area.configure(state='normal')
        self.status_area.delete("1.0", tk.END)

    def exit_app(self):
        self.quit()

    def on_closing(self, event=0):
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()