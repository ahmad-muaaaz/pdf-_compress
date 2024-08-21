import fitz  # PyMuPDF
import os
from PIL import Image
from io import BytesIO
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox

def compress_pdf(input_pdf_path, output_pdf_path, max_size_kb=1000, zoom_factor=0.5, quality=75):
    
    doc = fitz.open(input_pdf_path)
    new_pdf = fitz.open()

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
        img_bytes = pix.tobytes("jpeg")
        img_stream = BytesIO(img_bytes)
        image = Image.open(img_stream)
        compressed_img_stream = BytesIO()
        image.save(compressed_img_stream, format='JPEG', quality=quality)
        new_page = new_pdf.new_page(width=pix.width, height=pix.height)
        new_page.insert_image(new_page.rect, stream=compressed_img_stream.getvalue())

    new_pdf.save(output_pdf_path)
    new_pdf.close()

    file_size_kb = os.path.getsize(output_pdf_path) / 1024
    if file_size_kb > max_size_kb:
        print(f"Compressed PDF is still larger than {max_size_kb} KB. Retrying with lower quality...")
        compress_pdf(input_pdf_path, output_pdf_path, max_size_kb, zoom_factor, quality=quality-10)

    print(f"Compressed PDF saved at {output_pdf_path}, Size: {file_size_kb:.2f} KB")

def select_input_file():
    global input_pdf_path
    input_pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if input_pdf_path:
        input_file_label.config(text=f"Selected: {input_pdf_path}")

def start_compression():
    if not input_pdf_path:
        messagebox.showerror("Error", "Please select an input PDF file.")
        return

    max_size_str = max_size_entry.get()
    if not max_size_str:
        messagebox.showerror("Error", "Please enter a maximum size in KB.")
        return

    try:
        max_size_kb = float(max_size_str)
    except ValueError:
        messagebox.showerror("Error", "Invalid maximum size. Please enter a valid number.")
        return

    output_pdf_path = output_name_entry.get()
    if not output_pdf_path:
        messagebox.showerror("Error", "Please enter an output file name.")
        return

    if not output_pdf_path.endswith(".pdf"):
        output_pdf_path += ".pdf"

    compress_pdf(input_pdf_path, output_pdf_path, max_size_kb)
    messagebox.showinfo("Success", f"Compressed PDF saved at {output_pdf_path}")

root = Tk()
root.title("PDF Compressor")

Label(root, text="Select PDF file:").grid(row=0, column=0, padx=10, pady=10)
Button(root, text="Browse", command=select_input_file).grid(row=0, column=1, padx=10, pady=10)
input_file_label = Label(root, text="No file selected")
input_file_label.grid(row=0, column=2, padx=10, pady=10)

Label(root, text="Max size (KB):").grid(row=1, column=0, padx=10, pady=10)
max_size_entry = Entry(root)
max_size_entry.grid(row=1, column=1, padx=10, pady=10)

Label(root, text="Output file name:").grid(row=2, column=0, padx=10, pady=10)
output_name_entry = Entry(root)
output_name_entry.grid(row=2, column=1, padx=10, pady=10)

Button(root, text="Compress PDF", command=start_compression).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()