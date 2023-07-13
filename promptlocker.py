#promptlockertk
import tkinter as tk
from tkinter import filedialog, font, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, PngImagePlugin
from pathlib import Path
from time import sleep
import urllib.request
import urllib.parse
import tempfile
import os
import sys
import png
import pyperclip 
from showinfm import show_in_file_manager

noplcrypt = False
try:
    from pl_crypt import encrypt_metadata, decrypt_metadata
except Exception as e:
    if "ImportError" in str(e):
        noplcryptmessage = "Encrypt/Decrypt function only available on the executable version currently"
    else:
        print("Failed importing encryption mechanism: " + str(e))
        noplcryptmessage = "Failed importing encryption mechanism: " + str(e)
    noplcrypt = True

# from urllib.request import urlretrieve
# from getpass import getpass
# import shlex
# from tkinter import scrolledtext

pl_version = "0.0.3"
chunkinfo = int()
pngcrush_path = ""
global_imagepath = ""
batch_imagepaths = []
temp_batch_imagepaths = dict()
every_temppath = []
batch_imageindex = 0

def find_data_file(filename):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)

def create_temp_copy(image_path, max_size):
    global every_temppath
    # Load the original image
    image = Image.open(image_path)

    # Determine the scale factor to resize the image
    scale_factor = min(max_size / image.width, max_size / image.height)

    # Calculate the new dimensions
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)

    # Resize the image
    resized_image = image.resize((new_width, new_height))

    # Create a temporary file to save the resized image
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_file_path = temp_file.name

    every_temppath.append(temp_file_path)

    # Save the resized image to the temporary file
    resized_image.save(temp_file_path)

    return temp_file_path

def read_png_text_chunks(file_path):
    # print(file_path)
    pathlibimage = Path(file_path)

    with pathlibimage.open(mode="rb") as f:
        png_reader = png.Reader(file=f)
        chunks = png_reader.chunks()
        fulltext = ""
        for chunk_type, chunk_data in chunks:
            if chunk_type == b'tEXt':
                # Decode the chunk data as UTF-8
                text = chunk_data.decode('utf-8')
                if text.startswith("parameters"):
                    text = text.lstrip("parameters")
                fulltext += text
        return fulltext.lstrip("\x00")

def refreshui():
    global global_imagepath
    global_imagepath = ""
    image_label.config(image="")
    image_label.image = ""
    check_password()
    pagenumber.configure(text="")
    printandinfo("Not selecting any image / Not a valid PNG image")
    path_label.configure(text="Drag and drop a single image file here, or multiple files,\nor a single folder, \nor press Ctrl+V if you have discord image link in your clipboard.")

def on_drop(event):
    # global global_imagepath
    # global batch_imagepaths
    # global batch_imageindex
    # global temp_batch_imagepaths
    # Get the path of the dropped file
    # path = unquote(event.data).strip('{}')
    output = event.data.strip()
    paths = []

    def separateoutput():
        nonlocal output
        # Handle the path inside curly braces as a single item
        start_index = output.find('{') + 1
        end_index = output.find('}')
        single_path = output[start_index:end_index].strip()
        paths.append(single_path)

        # Remove the path inside curly braces from the output
        output = output[:start_index-1] + output[end_index+1:]

    while '{' in output:
        separateoutput()

    paths.extend(output.split())

    def configuresingleimage(pathofimage):
        global global_imagepath
        pagenumber.configure(text="")
        path_label.config(text="Dropped Image Path: \n" + pathofimage)
        global_imagepath = os.path.normpath(path)
        temp_image_path = create_temp_copy(pathofimage, max_size=1024)
        infotext.config(text='Image "' + os.path.basename(pathofimage) + '" loaded.')
        dencryptcheckbox.configure(state="disabled")
        # Display the image
        display_image(temp_image_path, pathofimage)

    def configuresingledir(pathofdir, local_batch_imagepaths=None):
        global global_imagepath
        global batch_imagepaths
        global batch_imageindex
        global temp_batch_imagepaths
        if local_batch_imagepaths: #then it's images
            samedirectories = all(item.startswith(os.path.dirname(local_batch_imagepaths[0])) for item in local_batch_imagepaths)
            if samedirectories:
                pathofdir = os.path.dirname(local_batch_imagepaths[0])
                path_label.config(text="Selected Multiple images from: \n" + pathofdir)
            else:
                path_label.config(text="Selected Multiple images")
        else: #singledir
            path_label.config(text="Selected Image Directory: \n" + pathofdir)

        image_label.config(image="")
        image_label.image = ""
        if not local_batch_imagepaths:
            batch_imagepaths = [
                os.path.normpath(os.path.join(pathofdir, file)) for file in os.listdir(pathofdir)
                if os.path.splitext(file)[1].lower() == ".png"
            ]
        else:
            batch_imagepaths = ""
            for singlepath in local_batch_imagepaths:
                batch_imagepaths.append(os.path.normpath(singlepath))
            # batch_imagepaths = local_batch_imagepaths
        batch_imageindex = 0
        if batch_imagepaths:
            prevbutton.config(state="normal")
            nextbutton.config(state="normal")
            global_imagepath = batch_imagepaths[batch_imageindex]
            temp_image_path = create_temp_copy(global_imagepath, max_size=1024)
            temp_batch_imagepaths = dict()
            temp_batch_imagepaths[batch_imageindex] = os.path.normpath(temp_image_path)
            infotext.config(text='Image "' + os.path.basename(global_imagepath) + '" loaded.')
            dencryptcheckbox.configure(state="normal")
            pagenumber.configure(text=f"{batch_imageindex + 1}/{len(batch_imagepaths)}")
            display_image(temp_image_path, global_imagepath)

    # Create a temporary copy of the image
    if paths:
        if len(paths) == 1:
            path = paths[0]
            if os.path.isfile(path):
                # Display the path in the label
                configuresingleimage(path)

            elif os.path.isdir(path):
                configuresingledir(path)

            else:
                refreshui()
        
        else: #more than one in the list
            paths = [path for path in paths if os.path.splitext(path)[1].lower() == ".png"] #only select png files
            if len(paths) == 1: #if one png left
                path = paths[0]
                if os.path.isfile(path):
                    # Display the path in the label
                    configuresingleimage(path)
                    
                else:
                    refreshui()
            elif not paths:
                refreshui()
            else: #several paths
                configuresingledir(None, paths)
    else:
        refreshui()

def open_file_dialog():
    global global_imagepath
    # Open a file dialog to select an image file
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png")])

    # Display the path in the label
    path_label.config(text="Selected Image Path: \n" + path)

    # Create a temporary copy of the image
    if path:
        if os.path.isfile(path):
            pagenumber.configure(text="")
            global_imagepath = os.path.normpath(path)
            temp_image_path = create_temp_copy(path, max_size=1024)
            infotext.config(text='Image "' + os.path.basename(path) + '" loaded.')
            dencryptcheckbox.configure(state="disabled")
            # Display the image
            display_image(temp_image_path, path)
        else:
            refreshui()
    else:
        refreshui()

def open_folder_dialog(): #@note beenworkingonthis
    global global_imagepath
    global batch_imagepaths
    global batch_imageindex
    global temp_batch_imagepaths
    # Open a file dialog to select an image file
    path = filedialog.askdirectory()

    # Display the path in the label
    path_label.config(text="Selected Image Directory: \n" + path)

    # Create a temporary copy of the image
    if path:
        if os.path.isdir(path):
            
            infotext.config(text="Directory loaded.")
            # Display the image
            # display_image(temp_image_path, path)
            image_label.config(image="")
            image_label.image = ""
            batch_imagepaths = [
                os.path.normpath(os.path.join(path, file)) for file in os.listdir(path)
                if file.lower().endswith(".png")
            ]
            batch_imageindex = 0
            if batch_imagepaths:
                prevbutton.config(state="normal")
                nextbutton.config(state="normal")
                global_imagepath = batch_imagepaths[batch_imageindex]
                temp_image_path = create_temp_copy(global_imagepath, max_size=1024)
                temp_batch_imagepaths = dict()
                temp_batch_imagepaths[batch_imageindex] = os.path.normpath(temp_image_path)
                infotext.config(text='Image "' + os.path.basename(global_imagepath) + '" loaded.')
                pagenumber.configure(text=f"{batch_imageindex + 1}/{len(batch_imagepaths)}")
                dencryptcheckbox.configure(state="normal")
                display_image(temp_image_path, global_imagepath)
        else:
            global_imagepath = ""
            check_password()
    else:
        global_imagepath = ""
        check_password()

def is_png_file(file_path):
    with open(file_path, 'rb') as f:
        signature = f.read(8)
        return signature == b'\x89PNG\r\n\x1a\n'

def chunkchecker(filepath):
        
    if is_png_file(filepath):
        textchunks = read_png_text_chunks(filepath)
        if textchunks:
            # print(textchunks)
            return [1, textchunks.lstrip()]
        else:
            return [0, "(The image chosen does not have a \ntEXt chunks in it. It's empty.)"]

    else:
        if filepath.endswith(".png"):
            return [0, "(The image chosen is not a PNG file, despite having a .png extension.)"]
        else:
            return [0, "(The image chosen is not a PNG file.)"]

def open_explorer():
    if not global_imagepath:
        open_file_dialog()
    else:
        if os.path.exists(global_imagepath):
            # print("debug global_imagepath: " + global_imagepath)
            # try:
            show_in_file_manager(global_imagepath)
            # except TypeError:
            #     show_in_file_manager(global_imagepath.replace("/", os.sep))

def discord_download():
    global global_imagepath

    discordlink = pyperclip.paste()
    if not urllib.parse.urlparse(discordlink).scheme:
        printandinfo("The copied link is not a valid link.")
        return
    if not discordlink.startswith("https://cdn.discordapp.com/attachments"):
        printandinfo("The copied link is not a valid discord image link.")
        return
    if not discordlink.startswith("https://cdn.discordapp.com/attachments"):
        printandinfo("The copied link is not a valid discord image link.")
        return
    if not discordlink.endswith(".png"):
        printandinfo("The copied link is not a valid discord png image link.")
        return
    
    download_folder = os.path.expanduser("~\\Downloads")
    os.makedirs(download_folder, exist_ok=True)
    filename = os.path.basename(urllib.parse.urlparse(discordlink).path)
    output_path = os.path.join(download_folder, filename)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        printandinfo(f"Trying to download {filename} from discord...")

        # Create a request object with the custom headers
        request = urllib.request.Request(discordlink, headers=headers)
        
        # Open the URL with the custom request
        response = urllib.request.urlopen(request)
        
        # Read the response and save it to a file
        with open(output_path, 'wb') as file:
            file.write(response.read())

        print("File downloaded successfully!")
        print("Output path:", output_path)
    except Exception as e:
        printandinfo(f"An error occurred while downloading the file: {str(e)}")

    if os.path.isfile(output_path):
        if not is_png_file(output_path):
            printandinfo(f"Image download failed somehow.")
        else:
            path_label.config(text="Image Downloaded. Selected Image Path: \n" + output_path)
            pagenumber.configure(text="")
            global_imagepath = os.path.normpath(output_path)
            temp_image_path = create_temp_copy(output_path, max_size=1024)
            infotext.config(text='Image "' + os.path.basename(output_path) + '" loaded.')
            dencryptcheckbox.configure(state="disabled")
            # Display the image
            display_image(temp_image_path, output_path)

def display_image(tempimagepath, actualimagepath):
    global chunkinfo
    # Load the image using PIL
    image = Image.open(tempimagepath)

    # Resize the image based on the window size
    resized_image = resize_image(image)

    # Convert the resized image to Tkinter-compatible format
    tk_image = ImageTk.PhotoImage(resized_image)

    # Update the image on the GUI interface
    image_label.config(image=tk_image)
    image_label.image = tk_image

    # Configure a callback to resize the image when the window size changes
    left_frame.bind("<Configure>", lambda event: resize_and_update_image(image, tk_image))

    if os.path.exists(actualimagepath):
        chunkinfo, chunktext = chunkchecker(actualimagepath)
        insertpnginfo(chunktext)
    else:
        insertpnginfo("")
        printandinfo("This image no longer exist.")
    check_password()
        
        # pnginfotext.config(text=str(chunktext))
        # pnginfotext.insert(tk.INSERT, chunktext)

def resize_image(image):
    # Get the current size of the window
    window_width = left_frame.winfo_width() / 1.5
    window_height = left_frame.winfo_height()

    # Calculate the new size of the image based on the window size while maintaining aspect ratio
    width_ratio = window_width / image.width
    height_ratio = window_height / image.height
    scale_factor = min(width_ratio, height_ratio)
    if scale_factor > 0.7 : scale_factor = 0.7
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)

    # Resize the image
    resized_image = image.resize((new_width, new_height))
    # print(f"window_width: {window_width}\nwindow_height: {window_height},\n",
    #       f"width_ratio: {width_ratio}\nheight_ratio: {height_ratio},\n"
    #       f"scale_factor: {scale_factor}\nnew_width: {new_width},\n"
    #       f"new_height: {new_height}")

    return resized_image

def resize_and_update_image(image, tk_image):
    # Resize the image based on the window size
    resized_image = resize_image(image)

    # Update the image on the GUI interface
    tk_image_resized = ImageTk.PhotoImage(resized_image)
    image_label.config(image=tk_image_resized)
    image_label.image = tk_image_resized

def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

def printandinfo(textwithinfo):
    infotext.config(text=textwithinfo)
    print(textwithinfo)

# def check_pngcrush():
#     global pngcrush_path
#     script_dir = get_script_directory()
#     # print(script_dir)
#     pngcrush_path = os.path.join(script_dir, "pngcrush_1_8_11_w64.exe")  # Assuming Windows

#     if not os.path.exists(pngcrush_path):
#         printandinfo("pngcrush not found. Downloading...")

#         # Download pngcrush from the provided link
#         download_url = "https://onboardcloud.dl.sourceforge.net/project/pmt/pngcrush-executables/1.8.11/pngcrush_1_8_11_w64.exe"
#         urlretrieve(download_url, pngcrush_path)

#         printandinfo("pngcrush downloaded")
#     else:
#         printandinfo("pngcrush already installed.")

def check_password():
    if global_imagepath and chunkinfo:
        if len(password_entry.get()) > 0:
            encryptbutton.config(state=tk.NORMAL)
            decryptbutton.config(state=tk.NORMAL)
        else:
            encryptbutton.config(state=tk.DISABLED)
            decryptbutton.config(state=tk.DISABLED)

# def pngcrushrewritemetadata(newmetadata, imagepath):
#     directory = os.path.dirname(imagepath)
#     base_filename = os.path.splitext(os.path.basename(imagepath))[0]
#     tempfile = os.path.join(directory, base_filename + "_temp.png")

#     # newmetadata = "test" # REMOVETHISLATER
#     newmetadata = newmetadata.encode('unicode-escape').decode() # REMOVETHISLATER

#     pngcrush_filename = os.path.basename(pngcrush_path)
#     command = f'{pngcrush_filename} -ow -nocheck -noreduce -max 65536 -rem text -oldtimestamp -text b "parameters" "{shlex.quote(newmetadata)}" "{imagepath}" "{tempfile}"'
#     # os.system(command)
#     #command = command.replace('"', '\\"') # Escape inner quote

#     original_directory = os.getcwd()
#     try:
#         os.chdir(os.path.dirname(pngcrush_path))
#         os.system(command)
#         # os.system(f'start cmd /k "{command}"')
#     except Exception as e:
#         print("An error occurred:", str(e))
#     finally:
#         os.chdir(original_directory)

def replacepngmetadata(newmetadata, imagepath):
    # Open the image and retrieve the existing PngInfo object
    im = Image.open(imagepath)
    existing_info = im.info.get("pnginfo")

    # Create a new PngInfo object for the updated "tEXt" chunks
    new_info = PngImagePlugin.PngInfo()

    # Iterate over the existing "tEXt" chunks and copy all keys except "parameters"
    if existing_info:
        for key, value in existing_info.items():
            if key.lower().strip() != "parameters":
                new_info.add_text(key, value)

    # Add the new "parameters" key with the desired value
    new_info.add_text("parameters", newmetadata)

    # Save the image with the updated PngInfo object
    im.save(imagepath, "PNG", pnginfo=new_info)

def checkdatemodified(path, originaltime):
    if is_preservemodifiedtime.get() == 1:
        os.utime(path, (os.path.getatime(path), originaltime))

def redirect_output(widget):
    class StdoutRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, message):
            self.widget.configure(state="normal")
            self.widget.insert(tk.END, message)
            self.widget.see(tk.END)  # Scroll to the end of the Text widget
            self.widget.configure(state="disabled")

    sys.stdout = StdoutRedirector(widget)

def undo_redirect_output():
    sys.stdout = sys.__stdout__

new_window = None

def create_new_window(jobname=None):
    global new_window
    new_window = tk.Toplevel(window)
    new_window.protocol("WM_DELETE_WINDOW", lambda: close_window(new_window, jobname))
    output_text = tk.Text(new_window)
    output_text.pack()
    redirect_output(output_text)

def close_window(window, jobname=None):
    window.destroy()
    undo_redirect_output()
    if jobname == "batchdencrypt":
        global processingbatch
        processingbatch = False

processingbatch = False

# class PopupWindow(tk.Toplevel):
#     def __init__(self, master):
#         # super().__init__(master)
#         self.title("No plcrypt module found")
#         self.geometry("200x100")
#         self.resizable(False, False)
#         self.protocol("WM_DELETE_WINDOW", self.close_popup)
        
#         self.label_noplcrypt = tk.Label(self, text=noplcryptmessage)
#         self.close_button = tk.Button(self, text="OK", command=self.close_popup)
#         self.close_button.pack(pady=20)
    
#     def close_popup(self):
#         # self.master.show_popup_button.config(state=tk.NORMAL)
#         self.destroy()

def spawnpopup():
    global dencryptpopup
  
    dencryptpopup = tk.Toplevel(window)
    dencryptpopup.title("No plcrypt module found")
    dencryptpopup.geometry("200x100")
    dencryptpopup.resizable(False, False)
    dencryptpopup.protocol("WM_DELETE_WINDOW", dencryptpopup.destroy)

    dencryptpopup.attributes('-topmost', True)
    # dencryptpopup.attributes('-alpha', 0.8)

    # Center the popup window on the screen
    window_x = window.winfo_rootx()
    window_y = window.winfo_rooty()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    popup_width = dencryptpopup.winfo_reqwidth()
    popup_height = dencryptpopup.winfo_reqheight()
    x = window_x + (window_width - popup_width) // 2
    y = window_y + (window_height - popup_height) // 2
    dencryptpopup.geometry(f"+{x}+{y}")

    label_noplcrypt = tk.Label(dencryptpopup, text=noplcryptmessage, wraplength=180)
    label_noplcrypt.pack(padx=10, pady=10)
    close_button = tk.Button(dencryptpopup, text="OK", command=dencryptpopup.destroy, width=10, height=5)
    close_button.pack(pady=5)
    
    try:
        # Play a system beep sound
        dencryptpopup.bell()
    except:
        pass
    
    dencryptpopup.grab_set()
    dencryptpopup.wait_window(dencryptpopup)

def noplcryptpopup():
    global dencryptpopup
    if dencryptpopup is None or not dencryptpopup.winfo_exists():
        spawnpopup() # dencryptpopup = PopupWindow(window)
    elif dencryptpopup is not None and dencryptpopup.winfo_exists():
        dencryptpopup.destroy()# dencryptpopup.close_popup()

def encryptbuttonpressed(): #@note
    global new_window
    def encryptprocess(pathtoencrypt):
        filename = os.path.basename(pathtoencrypt)
        chunkcheck, metadata = chunkchecker(pathtoencrypt) #onlythechunk #pnginfotext.get('1.0', 'end')
        if chunkcheck:
            encrypted_metadata = encrypt_metadata(metadata, password_entry.get(), comment_entry.get('1.0', 'end'), infotext)
            if encrypted_metadata != metadata:
                originaldatemodified = os.path.getmtime(pathtoencrypt)
                replacepngmetadata(encrypted_metadata, pathtoencrypt)
                checkdatemodified(pathtoencrypt, originaldatemodified)
                # pngcrushrewritemetadata(encrypted_metadata, global_imagepath)
                insertpnginfo(encrypted_metadata)
                printandinfo(f"{filename}: Metadata encrypted successfully!")
        else:
            printandinfo(f"{filename}: No tEXt chunk in this image to process")

    if not noplcrypt:
        if is_dencryptall.get() == 1:
            printandinfo("Attempting to encrypt every PNG image in current directory")
            create_new_window()
            sleep(2)
            if batch_imagepaths:
                global processingbatch
                processingbatch = True
                for path in batch_imagepaths:
                    if not processingbatch:
                        break
                    if os.path.exists(path):
                        encryptprocess(path)
            try:
                close_window(new_window)
            except:
                pass

        else:
            printandinfo("Attempting to encrypt the chosen image...")
            encryptprocess(global_imagepath)
    else:
        # printandinfo(noplcryptmessage)
        noplcryptpopup()

def decryptbuttonpressed():

    def decryptprocess(pathtodecrypt):
        filename = os.path.basename(pathtodecrypt)
        chunkcheck, metadata = chunkchecker(pathtodecrypt) #onlythechunk #pnginfotext.get('1.0', 'end')
        if chunkcheck:
                decrypted_metadata = decrypt_metadata(metadata, password_entry.get(), infotext)
                if decrypted_metadata is not None:
                    originaldatemodified = os.path.getmtime(pathtodecrypt)
                    replacepngmetadata(decrypted_metadata, pathtodecrypt)
                    checkdatemodified(pathtodecrypt, originaldatemodified)
                    insertpnginfo(decrypted_metadata)
                    printandinfo(f"{filename}: Metadata decrypted successfully!")
        else:
            printandinfo(f"{filename}: No tEXt chunk in this image to process")

    if not noplcrypt:
        if is_dencryptall.get() == 1:
            printandinfo("Attempting to decrypt every PNG image in current directory")
            create_new_window("batchdencrypt")
            if batch_imagepaths:
                global processingbatch
                processingbatch = True
                for path in batch_imagepaths:
                    if not processingbatch:
                        break
                    if os.path.exists(path):
                        decryptprocess(path)
            try:
                close_window(new_window)
            except:
                pass
        else:
            printandinfo("Attempting to decrypt the chosen image...")
            decryptprocess(global_imagepath)
    else:
        # printandinfo(noplcryptmessage)
        noplcryptpopup()

def copypnginfo():
    if global_imagepath:
        state, chunktocopy = chunkchecker(global_imagepath)
        if state:
            pyperclip.copy(chunktocopy)
            printandinfo("PNG Info copied to clipboard.")
        else:
            printandinfo("No PNG Info to copy.")
    else:
        printandinfo("No PNG Info to copy.")

def prev_image():
    global batch_imagepaths
    global batch_imageindex
    global temp_batch_imagepaths
    global global_imagepath
    if batch_imageindex > 0:
        batch_imageindex -= 1
    else:
        batch_imageindex = len(batch_imagepaths) - 1
    global_imagepath = batch_imagepaths[batch_imageindex]
    if temp_batch_imagepaths.get(batch_imageindex) is not None:
        temp_image_path = temp_batch_imagepaths[batch_imageindex]
    else:
        temp_image_path = create_temp_copy(global_imagepath, max_size=1024)
        temp_batch_imagepaths[batch_imageindex] = temp_image_path
    pagenumber.configure(text=f"{batch_imageindex + 1}/{len(batch_imagepaths)}")
    infotext.config(text='Image "' + os.path.basename(global_imagepath) + '" loaded.')
    display_image(temp_image_path, global_imagepath)

def next_image():
    global batch_imagepaths
    global batch_imageindex
    global temp_batch_imagepaths
    global global_imagepath
    if batch_imageindex < len(batch_imagepaths) - 1:
        batch_imageindex  += 1
    else:
        batch_imageindex  = 0
    global_imagepath = batch_imagepaths[batch_imageindex]
    if temp_batch_imagepaths.get(batch_imageindex) is not None:
        temp_image_path = temp_batch_imagepaths[batch_imageindex]
    else:
        temp_image_path = create_temp_copy(global_imagepath, max_size=1024)
        temp_batch_imagepaths[batch_imageindex] = temp_image_path
    pagenumber.configure(text=f"{batch_imageindex + 1}/{len(batch_imagepaths)}")
    infotext.config(text='Image "' + os.path.basename(global_imagepath) + '" loaded.')
    display_image(temp_image_path, global_imagepath)

# Create the main Tkinter window
window = TkinterDnD.Tk()
window.title(f"Promptlocker {pl_version} - by etherealxx")

# Set a fixed size for the window
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_width = 1200
window_height = 930
window.geometry(f"{window_width}x{window_height}")

x_coordinate = (screen_width - window_width) // 2
y_coordinate = int((screen_height - window_height) // 3)
window.geometry(f"+{x_coordinate}+{y_coordinate}")

# Divide the window into two areas
left_frame = tk.Frame(window)
left_frame.grid(row=0, column=0, sticky="nsew")

right_frame = tk.Frame(window)
right_frame.grid(row=0, column=1, sticky="nsew")

# Configure the grid layout to evenly divide the window
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
# window.grid_rowconfigure(0, weight=1)

# Create a label to display the image path
path_label = tk.Label(left_frame, text="Drag and drop a single image file here, or multiple files,\nor a single folder, \nor press Ctrl+V if you have discord image link in your clipboard.")
path_label.grid(row=0, column=0, pady=10)

# Create a frame inside the left frame for image and path label
image_frame = tk.Frame(left_frame)
image_frame.grid(row=1, column=0, sticky="nsew")

# Create a label to display the image
image_label = tk.Label(image_frame)
image_label.pack()

# Configure the grid layout for the left frame
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=0)
left_frame.grid_columnconfigure(0, weight=1)

# Set up the drag and drop functionality
left_frame.drop_target_register(DND_FILES)
left_frame.dnd_bind('<<Drop>>', on_drop)

nav_button_frame = tk.Frame(image_frame)
nav_button_frame.pack(padx=10, pady=5)

openthisimagebutton = tk.Button(nav_button_frame, text="View on Explorer", command=open_explorer)
openthisimagebutton.pack(side=tk.LEFT, padx=5)
prevbutton = tk.Button(nav_button_frame, text="   <   ", state="disabled", command=prev_image)
prevbutton.pack(side=tk.LEFT, padx=5)
nextbutton = tk.Button(nav_button_frame, text="   >   ", state="disabled", command=next_image)
nextbutton.pack(side=tk.LEFT, padx=5)
pagenumber = tk.Label(nav_button_frame, text="")
pagenumber.pack(side=tk.LEFT, padx=5)

open_button_frame = tk.Frame(image_frame)
open_button_frame.pack(padx=10, pady=10)

# Create a button to open a file dialog
openfilebutton = tk.Button(open_button_frame, text="Open PNG File", command=open_file_dialog)
openfilebutton.pack(side=tk.LEFT, padx=5)
openfolderbutton = tk.Button(open_button_frame, text="Open Folder (Batch)", command=open_folder_dialog)
openfolderbutton.pack(side=tk.LEFT, padx=5)

infotext = tk.Label(right_frame, text="")
infotext.pack(padx=10, pady=10)

ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=10)

comment_frame = tk.Frame(right_frame)
comment_frame.pack(padx=10, pady=10)

tk.Label(comment_frame, text="Comment (Optional)").grid(row=0, column=0, sticky="e", padx=5)
# comment_entry = tk.Entry(comment_frame)
comment_entry = tk.Text(right_frame, font=font.nametofont("TkDefaultFont"), wrap="word", width=60, height=2)
comment_entry.pack(padx=10, pady=10)

password_frame = tk.Frame(right_frame)
password_frame.pack(padx=10, pady=10)

tk.Label(password_frame, text="Password").grid(row=0, column=0, sticky="e", padx=5)
password_entry = tk.Entry(password_frame, show="●")
password_entry.grid(row=0, column=1, padx=5, sticky="w")
password_entry.bind("<KeyRelease>", lambda event: check_password())

is_preservemodifiedtime = tk.IntVar(value=1)
checkbox_frame = tk.Frame(right_frame)
checkbox_frame.pack(padx=10, pady=10)
checkbox = tk.Checkbutton(checkbox_frame, text="Preserve date_modified metadata", variable=is_preservemodifiedtime)
checkbox.pack(padx=10, pady=1)
is_dencryptall = tk.IntVar(value=0)
dencryptcheckbox = tk.Checkbutton(checkbox_frame, text="Batch Encrypt/Decrypt to all file in this folder", variable=is_dencryptall, state="disabled")
dencryptcheckbox.pack(padx=10, pady=1)

dencrypt_frame = tk.Frame(right_frame)
dencrypt_frame.pack(padx=10, pady=5)

encryptbutton = tk.Button(dencrypt_frame, text="Encrypt", command=encryptbuttonpressed)
encryptbutton.pack(side=tk.LEFT, padx=5)

decryptbutton = tk.Button(dencrypt_frame, text="Decrypt", command=decryptbuttonpressed)
decryptbutton.pack(side=tk.LEFT, padx=5)

dencryptpopup = None

# pnginfotext = tk.Label(right_frame, text="Label 2")
# pnginfotext.pack(padx=10, pady=10)

# pnginfotext = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
# pnginfotext.pack(fill=tk.BOTH, expand=True)
ttk.Separator(right_frame, orient="horizontal").pack(fill="x", pady=10)

tk.Label(right_frame, text="PNG Info (tEXt Chunk)").pack(padx=10, pady=10)

pnginfotext = tk.Text(right_frame, font=font.nametofont("TkDefaultFont"), wrap="word", width=60, height=20)
pnginfotext.pack(padx=10, pady=10)

copybutton = tk.Button(right_frame, text="Copy PNG Info", command=copypnginfo)
copybutton.pack(padx=10, pady=5)

def insertpnginfo(texttoinsert):
    pnginfotext.configure(state="normal")
    pnginfotext.delete("1.0", tk.END)
    # for line in texttoinsert.splitlines():
    #     # print(line)
    #     pnginfotext.insert(tk.END, line)
    pnginfotext.insert(tk.END, texttoinsert)
    pnginfotext.configure(state="disabled")

def onstartofgui():
    # check_pngcrush()
    pnginfotext.configure(state="disabled")
    check_password()
    encryptbutton.config(state=tk.DISABLED)
    decryptbutton.config(state=tk.DISABLED)

def remove_alltemp():
    for tempfile in every_temppath:
        if os.path.exists(tempfile):
            os.remove(tempfile)
    window.destroy()

# Schedule the script to run after a delay of 0 milliseconds
window.after(0, onstartofgui)

window.protocol("WM_DELETE_WINDOW", remove_alltemp)
window.bind("<Control-v>", lambda event: discord_download())

icon_path = find_data_file("promptlockericon.ico")

# Set the icon
try:
    window.iconbitmap(icon_path)
except:
    pass

# Run the Tkinter event loop
window.mainloop()
