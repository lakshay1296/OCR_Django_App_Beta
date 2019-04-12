import os

from pdf2image import convert_from_path
import  numpy as np
from pytesseract import Output

# For importing PyTesseract
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

'''
    Function for merging PNG's
'''
def merge_pdf (folder_path):
    list_im = []
    for root, dir, files in os.walk(folder_path):
        for singFile in files:
            if str(singFile).endswith(".png"):
                new_path = folder_path + "\\" + singFile
                list_im.append(new_path)

    # Getting current folder name
    folder_name = str(os.path.basename(folder_path))
    # Creating PNG Name through folder name
    file_name = folder_name[:-4]

    imgs = [Image.open(i) for i in list_im]
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]

    # for a vertical stacking it is simple: use vstack
    imgs_comb = np.vstack((np.asarray(i.resize(min_shape)) for i in imgs))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save(folder_path + "\\" + file_name + '.png', 'PNG')

    # For removing PDF's Page PNG's
    for image in list_im:
        os.remove(image)
        print "File: " + str(image) + " removed."

'''
    Function for processing OCR of Single Image File
'''
# def multi_file_tesseract(path, folder_path, single_image):
def multi_file_tesseract(path, folder_path):

    for root, dir, files in os.walk(path):
        for Singfile in files:
            print Singfile
            if str(Singfile).endswith(".png"):

                file_path = (root + "\\" + Singfile)
                print "this: " + file_path

                file_name = Singfile.split(".pdf")
                final_name = file_name[0]
                # Simple image to string
                ocr_text = (pytesseract.image_to_string(Image.open(file_path)))

                # Creating TXT Files
                text_file = open(folder_path + "\\" + str(final_name) + ".txt", "a")
                text_file.write(str(ocr_text))
                text_file.close()

        #return ocr_text


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
        text_file = open(path + ".txt", "a")
        text_file.write(str(ocr_text))
        #print ocr_text

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

    #merge_pdf(create_folder)

    return create_folder

'''
    Function for creating tooltip on image
'''

def tesseract_data(path):
    print(path)

    # Image
    img = Image.open(path)

    image_formats = ['.png', '.jpg', '.jpeg']

    for format in image_formats:
        if format in path:
            # Simple image to string
            image_data = pytesseract.image_to_data(img, output_type=Output.DICT)
        else:
            image_data = "File not supported."

        return img, image_data