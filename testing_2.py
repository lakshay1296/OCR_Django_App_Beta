import os
from pdf2image import convert_from_path
import re

# For importing PyTesseract
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

'''
    Function for processing OCR of Single Image File
'''
def multi_file_tesseract(path, folder_path, single_image):

    print(path)

    # Regex for extracting File Names Only.
    matchObj = re.search(r'(.*).png', single_image, re.I|re.M)
    if matchObj: file_name = matchObj.group(1)
    else: file_name = "No Match"

    image_format = '.png'

    if image_format in path:
        # Simple image to string
        ocr_text = (pytesseract.image_to_string(Image.open(path)))
    else:
        ocr_text = "File not supported."

    # Creating TXT Files
    text_file = open(folder_path + "\\" + file_name + ".txt", "w")
    text_file.write(str(ocr_text))

    return ocr_text

'''
    For OCR'ing a single file and saving it in same directory
'''
def single_file_tesseract(path):
    print(path)

    image_formats = ['.png', '.jpg', '.jpeg']

    for format in image_formats:
        if format in path:
            # Simple image to string
            ocr_text = (pytesseract.image_to_string(Image.open(path)))
        else:
            ocr_text = "File not supported."

        # Creating TXT Files
        text_file = open(path + ".txt", "w")
        text_file.write(str(ocr_text))
        print ocr_text

        return ocr_text

'''
    Function for converting PDF to image
'''
def pdf_to_image(file_path):
    pages = convert_from_path(file_path, 300)
    pdf_file = file_path[:-4]

    # For getting file name of the PDF
    newFile = str(file_path).split("\\")
    file_name = str(newFile[len(newFile)-1])
    file_name_proper = file_name[:-4]

    # Replacing file name in path to create PNG folder.
    new_pdf_path = str(pdf_file).replace(file_name_proper, "")

    # New path for placing PNG's.
    create_folder = new_pdf_path + "\\PNG\\" + file_name
    print "This is the path that I need to pick up: " + create_folder
    if not os.path.exists(create_folder):
        os.makedirs(create_folder)
    else:
        print "Folder Already Exists."

    # To save PNG's in same folder as name.
    new_png_path = create_folder + "\\" + file_name
    for page in pages:
        page.save("%s-page%d.png" % (new_png_path, pages.index(page)), "PNG")

    alert = "JPEG has been created."

    return create_folder