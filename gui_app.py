import tkinter as tk
from tkinter import filedialog, messagebox

from ocr_pdf import images_to_searchable_pdf

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
    status_var.set(f"Selected {len(selected_files)} file(s).")


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
        status_var.set("Scanning and running OCR...")
        root.update_idletasks()

        # Run the real scanner/OCR/PDF pipeline.
        images_to_searchable_pdf(selected_files, output_pdf)

        status_var.set(f"Saved: {output_pdf}")
        messagebox.showinfo("Done", f"Saved:\n{output_pdf}")
    except Exception as error:
        # Show any scanner/OCR/PDF error in a friendly popup.
        status_var.set("Failed.")
        messagebox.showerror("Error", str(error))

# Build the window.
root = tk.Tk()
root.title("Document Scanner")

status_var = tk.StringVar(value="Choose image files to scan.")

# Add three simple widgets: two buttons and one status label.
tk.Button(root, text="Choose Images", command=choose_files).pack(padx=16, pady=8)
tk.Button(root, text="Scan To PDF", command=scan_files).pack(padx=16, pady=8)
tk.Label(root, textvariable=status_var, wraplength=420).pack(padx=16, pady=8)

# Start the GUI event loop.
root.mainloop()