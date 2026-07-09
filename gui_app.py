import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import os
import random
import shutil
import signal
import subprocess
import sys
import webbrowser
from PIL import Image, ImageDraw, ImageFont, ImageTk
from ocr_pdf import images_to_searchable_pdf

# color palette
DARK_GRAY = "#1b3038"
LIGHT_GRAY = "#b7f4f1"
LIGHT_CYAN = "#76fff3"
DARKER_CYAN = "#0d6f7a"
MAGNETA = "#ff6fbd"

# temp colors
BG_COLOR = "#1b3038"
PANEL_COLOR = "#f4fdff"
BUTTON_COLOR = "#42ddd6"
BUTTON_TEXT = "#12323a"
ACCENT_COLOR = "#ff8ed1"
TEXT_COLOR = "#17313b"

# grabs the miku image
BASE_DIR = Path(__file__).resolve().parent
MIKU_IMAGE_PATH = BASE_DIR/"assets"/"miku.png"
LEEK_IMAGE_PATH = BASE_DIR / "assets" / "leek_small.png"
MUSIC_PATH = BASE_DIR / "assets" / "song" / "music.mp3"

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 750
SCENE_HEIGHT = 400
LEEK_COUNT = 28

VT323_FONT_PATH = BASE_DIR / "assets" / "fonts" / "VT323" / "VT323-Regular.ttf"
GITHUB_URL = "https://github.com/Javicshz"
LINKEDIN_URL = "https://www.linkedin.com/in/javicshz94/"
INSTAGRAM_URL = "https://www.instagram.com/ritesofjavi/"

def make_pixel_box_image(text, width, height, bg_color, text_color, font_size):
    # makes the chunky pixel style image for buttons and status text
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(VT323_FONT_PATH), font_size)

    shadow = "#071d25"
    border = "#0f4350"
    step = 8
    shadow_offset = 6

    # draws the dark shadow so it feels like a chunky pixel button
    draw.rectangle((step + shadow_offset, shadow_offset, width - step, height - step), fill=shadow)
    draw.rectangle((shadow_offset, step + shadow_offset, width, height - step * 2), fill=shadow)

    # draws the outside blocky border
    draw.rectangle((step, 0, width - step - shadow_offset, height - step - shadow_offset), fill=border)
    draw.rectangle((0, step, width - shadow_offset, height - step * 2 - shadow_offset), fill=border)

    # draws the inside color with stepped corners
    inset = 10
    draw.rectangle((inset + step, inset, width - inset - step - shadow_offset, height - inset - shadow_offset), fill=bg_color)
    draw.rectangle((inset, inset + step, width - inset - shadow_offset, height - inset - step - shadow_offset), fill=bg_color)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w - shadow_offset) // 2 - bbox[0]
    y = (height - text_h - shadow_offset) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=text_color)

    return ImageTk.PhotoImage(img)

def draw_pixel_button(canvas, x, y, text, command):
    normal_img = make_pixel_box_image(text, 260, 76, BUTTON_COLOR, BUTTON_TEXT, 34)
    pressed_img = make_pixel_box_image(text, 260, 76, ACCENT_COLOR, BUTTON_TEXT, 34)
    button_tag = f"button_{text.replace(' ', '_').lower()}"

    # draws the pixel button onto the main canvas
    image_item = canvas.create_image(x, y, image=normal_img, anchor="center", tags=(button_tag, "button"))
    click_item = canvas.create_rectangle(
        x - 130,
        y - 38,
        x + 130,
        y + 38,
        fill="",
        outline="",
        tags=(button_tag, "button_click"),
    )

    canvas.button_images.extend([normal_img, pressed_img])

    def press_button(event):
        # changes the button color and moves it down a little bit
        canvas.itemconfigure(image_item, image=pressed_img)
        canvas.coords(image_item, x, y + 2)

    def release_button(event):
        # puts the button back and runs the command
        canvas.itemconfigure(image_item, image=normal_img)
        canvas.coords(image_item, x, y)
        command()

    canvas.tag_bind(button_tag, "<ButtonPress-1>", press_button)
    canvas.tag_bind(button_tag, "<ButtonRelease-1>", release_button)
    canvas.tag_bind(button_tag, "<Enter>", lambda event: canvas.configure(cursor="hand2"))
    canvas.tag_bind(button_tag, "<Leave>", lambda event: canvas.configure(cursor=""))

    return image_item, click_item

def draw_footer_link(canvas, x, y, text, url):
    # adds a small clickable link at the bottom of the app
    link = canvas.create_text(
        x,
        y,
        text=text,
        fill=LIGHT_CYAN,
        font=("TkFixedFont", 9, "underline"),
        anchor="center",
        tags=("footer_link",),
    )
    click_box = canvas.create_rectangle(
        x - 38,
        y - 8,
        x + 38,
        y + 8,
        fill="",
        outline="",
        tags=("footer_link",),
    )

    def open_link(event):
        # opens the profile link in the user's browser
        webbrowser.open_new_tab(url)

    canvas.tag_bind(link, "<ButtonRelease-1>", open_link)
    canvas.tag_bind(click_box, "<ButtonRelease-1>", open_link)
    canvas.tag_bind(link, "<Enter>", lambda event: canvas.configure(cursor="hand2"))
    canvas.tag_bind(click_box, "<Enter>", lambda event: canvas.configure(cursor="hand2"))
    canvas.tag_bind(link, "<Leave>", lambda event: canvas.configure(cursor=""))
    canvas.tag_bind(click_box, "<Leave>", lambda event: canvas.configure(cursor=""))

def draw_footer(canvas):
    # adds a small creator note and profile links
    canvas.create_text(
        WINDOW_WIDTH // 2,
        705,
        text="Created by Javicshz",
        fill=PANEL_COLOR,
        font=("TkFixedFont", 7, "bold"),
        anchor="center",
    )
    draw_footer_link(canvas, 220, 727, "GitHub", GITHUB_URL)
    draw_footer_link(canvas, 300, 727, "LinkedIn", LINKEDIN_URL)
    draw_footer_link(canvas, 392, 727, "Instagram", INSTAGRAM_URL)

def shorten_status_text(text):
    if len(text) > 44:
        return text[:41] + "..."

    return text

def make_status_image(text):
    # makes the status box match the pixel button style
    return make_pixel_box_image(shorten_status_text(text), 430, 72, PANEL_COLOR, TEXT_COLOR, 32)

def set_status(text):
    status_var.set(text)
    if "status_label" in globals():
        img = make_status_image(text)
        main_canvas.itemconfigure(status_label, image=img)
        main_canvas.status_img = img

def make_main_canvas(parent):
    # makes one full canvas so leeks can float over the whole app
    main_canvas = tk.Canvas(
        parent,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        bg=DARK_GRAY,
        bd=0,
        highlightthickness=0,
    )
    main_canvas.button_images = []

    # adds miku to the canvas
    main_canvas.create_image(
        WINDOW_WIDTH // 2,
        SCENE_HEIGHT // 2,
        image=miku_photo,
        anchor="center",
    )
    main_canvas.miku_photo = miku_photo

    return main_canvas

def start_leek_snow(canvas):
    # loads the leek image and keeps it small so it is not distracting
    leek_image = Image.open(LEEK_IMAGE_PATH).convert("RGBA")
    leek_image.thumbnail((18, 30), Image.Resampling.LANCZOS)
    leek_photo = ImageTk.PhotoImage(leek_image)
    canvas.leek_photo = leek_photo

    leeks = []
    for _ in range(LEEK_COUNT):
        x = random.randint(0, WINDOW_WIDTH)
        y = random.randint(-WINDOW_HEIGHT, 0)
        speed = random.uniform(0.6, 1.6)
        drift = random.uniform(-0.35, 0.35)
        item = canvas.create_image(x, y, image=leek_photo, anchor="center", tags=("leek",))
        leeks.append({"item": item, "speed": speed, "drift": drift})

    def animate_leeks():
        # moves each leek down a little bit each frame
        for leek in leeks:
            canvas.move(leek["item"], leek["drift"], leek["speed"])
            x, y = canvas.coords(leek["item"])

            # puts the leek back at the top after it falls off screen
            if y > WINDOW_HEIGHT + 20:
                new_x = random.randint(0, WINDOW_WIDTH)
                new_y = random.randint(-80, -20)
                canvas.coords(leek["item"], new_x, new_y)
                leek["speed"] = random.uniform(0.6, 1.6)
                leek["drift"] = random.uniform(-0.35, 0.35)
            elif x < -20:
                canvas.coords(leek["item"], WINDOW_WIDTH + 20, y)
            elif x > WINDOW_WIDTH + 20:
                canvas.coords(leek["item"], -20, y)

        # keeps the leeks above miku, status, and buttons
        canvas.tag_raise("leek")
        canvas.tag_raise("button_click")

        root.after(40, animate_leeks)

    animate_leeks()

music_process = None
app_is_closing = False

def get_music_command():
    # skips music if the file is missing
    if not MUSIC_PATH.exists():
        return None

    # uses the built in mac music player
    if sys.platform == "darwin" and shutil.which("afplay") is not None:
        return ["afplay", "-v", "0.12", str(MUSIC_PATH)]

    # uses powershell on windows so we can play mp3 without another library
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if sys.platform.startswith("win") and powershell is not None:
        return [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "param($song) "
                "Add-Type -AssemblyName PresentationCore; "
                "$player = New-Object System.Windows.Media.MediaPlayer; "
                "$player.Open([Uri]::new($song)); "
                "$player.Volume = 0.12; "
                "$player.Play(); "
                "Start-Sleep -Milliseconds 500; "
                "while ($player.NaturalDuration.HasTimeSpan -eq $false) { "
                "Start-Sleep -Milliseconds 100 "
                "} "
                "while ($player.Position -lt $player.NaturalDuration.TimeSpan) { "
                "Start-Sleep -Milliseconds 500 "
                "} "
                "$player.Close();"
            ),
            str(MUSIC_PATH),
        ]

    # uses common linux music players if the user already has one installed
    linux_players = [
        ("ffplay", ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", "-volume", "12", str(MUSIC_PATH)]),
        ("mpg123", ["mpg123", "-q", "-f", "4000", str(MUSIC_PATH)]),
        ("mpv", ["mpv", "--no-video", "--really-quiet", "--volume=12", str(MUSIC_PATH)]),
    ]
    for player, command in linux_players:
        if shutil.which(player) is not None:
            return command

    return None

def start_background_music():
    global music_process

    # tries to play music without adding a new python library
    if app_is_closing:
        return

    command = get_music_command()
    if command is None:
        return

    process_options = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "posix":
        process_options["start_new_session"] = True
    elif os.name == "nt":
        process_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    music_process = subprocess.Popen(
        command,
        **process_options,
    )
    root.after(1000, check_background_music)

def check_background_music():
    # starts the song again if it finished playing
    if app_is_closing or music_process is None:
        return

    if music_process.poll() is not None:
        start_background_music()
    else:
        root.after(1000, check_background_music)

def stop_background_music():
    global music_process

    # stops the music when the app closes
    if music_process is None or music_process.poll() is not None:
        music_process = None
        return

    try:
        if os.name == "posix":
            os.killpg(music_process.pid, signal.SIGTERM)
        else:
            music_process.terminate()

        music_process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(music_process.pid, signal.SIGKILL)
        else:
            music_process.kill()
    finally:
        music_process = None

def close_app():
    global app_is_closing

    app_is_closing = True
    stop_background_music()
    root.destroy()


#tkinter root window
root = tk.Tk()
root.title("Miku Document Scanner")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", close_app)

# resizes it and makes it usable
miku_image = Image.open(MIKU_IMAGE_PATH)
miku_image = miku_image.resize((250,384))
miku_photo = ImageTk.PhotoImage(miku_image)

selected_files = []

def choose_files():
    global selected_files

    # Open the native macOS file picker and allow multiple image selections.
    selected_files = list(
        filedialog.askopenfilenames(
            title="Choose images to scan",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"),
                ("All files", "*.*"),
            ],
        )
    )

    # Show simple feedback in the window.
    set_status(f"Selected {len(selected_files)} file(s).")


def scan_files():
    # Do not run the scanner if the user has not chosen files.
    if not selected_files:
        messagebox.showwarning("No files", "Choose at least one image first.")
        return

    # Ask where the finished PDF should be saved.
    output_pdf = filedialog.asksaveasfilename(
        title="Save searchable PDF",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
    )
    if not output_pdf:
        return

    try:
        # Update the UI before starting the slow OCR work.
        set_status("Scanning and running OCR...")
        root.update_idletasks()

        # Run the real scanner/OCR/PDF pipeline.
        images_to_searchable_pdf(selected_files, output_pdf)

        set_status(f"Saved: {output_pdf}")
        messagebox.showinfo("Done", f"Saved:\n{output_pdf}")
    except Exception as error:
        # Show any scanner/OCR/PDF error in a friendly popup.
        set_status("Failed.")
        messagebox.showerror("Error", str(error))

# Build the window.
root.title("Document Scanner")

status_var = tk.StringVar(value="Choose image files to scan.")

# adds the background color to the window
root.configure(bg=DARK_GRAY)

# adds the main canvas for miku, buttons, status, and leeks
main_canvas = make_main_canvas(root)
main_canvas.pack(fill="both", expand=True)

# edits the status text
status_img = make_status_image(status_var.get())
status_label = main_canvas.create_image(
    WINDOW_WIDTH // 2,
    438,
    image=status_img,
    anchor="center",
)
main_canvas.status_img = status_img

# Add three simple widgets: two buttons and one status label.
choose_btn = draw_pixel_button(main_canvas, WINDOW_WIDTH // 2, 535, "Choose Images", choose_files)

scan_btn = draw_pixel_button(main_canvas, WINDOW_WIDTH // 2, 625, "Scan To PDF", scan_files)

# adds a little creator footer with profile links
draw_footer(main_canvas)

# starts the falling leeks after the ui is drawn so they float on top
start_leek_snow(main_canvas)

# starts the background music quietly
start_background_music()

# Start the GUI event loop.
root.mainloop()
