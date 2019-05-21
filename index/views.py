# -*- coding: utf-8 -*-
from __future__ import division
from django.http import HttpResponse
from django.shortcuts import render
from .FileName import FileName
from .source import utils as UT
from django.views import generic
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from threading import *
import os
import re
import sys
import time
import numpy as np
import csv
import datetime
# For Text Similarity
from gensim.models.keyedvectors import KeyedVectors
from DocSim import DocSim
# Importing Queue according to python version
try:
    import Queue
except:
    import queue as Queue

# Set default encoding to 'UTF-8'
reload(sys)
sys.setdefaultencoding('utf-8')

''' GLOBAL REGEX PATTERNS: '''
# Regex for detecting if a single file is selected or a directory.
singleFile = r'[/\\](.*)[/\\].(?:(png))'
# For checking a valid directory.
validDirec = r'[A-Za-z]:[/\\](.*)'

''' GLOBAL PATHS: '''
# Using the pre-trained word2vec model trained using Google news corpus of 3 billion running words.
googlenews_model_path = "C:\\Users\\lakshay.s\\Desktop\\document-similarity-master\\data\\GoogleNews-vectors-negative300.bin"
stopwords_path = "C:\\Users\\lakshay.s\\Desktop\\document-similarity-master\\data\\stopwords_en.txt"

'''GLOBAL QUEUES'''
per_sent_queue = Queue.Queue()

'''GLOBAL LISTS'''
total_file_listing = []
processed_file_list = []
full_path_list = []
files_to_be_processed = []
four_file_group = []

# Main Home Page
def index(request):
    file_name = FileName.objects.all()
    context = {'file_name': file_name}
    return render(request, "index/index.html", context)

# Experimental
def details(request, album_id):
    return HttpResponse('<h1> The entered Id is: ' + album_id + '</h1>')

# PNG_OCR Page
def home(request):
    file_name = FileName.objects.all()
    context = {'file_name': file_name}
    return render(request, "home/home.html", context)

# Getting file path for processing the PNG
def ocr_file_path(request):

    # Getting Value of file path
    file_path = request.POST.get('fname')
    print (str(file_path))

    # Starting of OCR Code.
    # Pattern for checking if a file path is is being uploaded or folder path.
    #matchObj = re.search(singleFile, file_path, re.I|re.M)

    if str(file_path).endswith(".png"):
        # Single Files
        process = path_exception_handling(file_path)
        output = process[0]
        emptyField = process[1]
        alert = "Fully Executed"
        print output

    elif (str(file_path).endswith("\\")) or (str(file_path).endswith("/")):
        # Creating a TXT folder in the parent location as the images.
        folder_path = str(os.path.abspath(os.path.join(file_path, os.pardir))) + "\\TXT"
        print "Folder Path:" + folder_path
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        else:
            print "Folder Already Exists."

        # # Multiple Files
        # for root, dir, files in os.walk(file_path):
        #     for single_image in files:
        #         image_path = os.path.join(root, single_image)
        # process = multi_path_exception_handling(file_path, image_path, folder_path, single_image)
        process = multi_path_exception_handling(file_path, folder_path)
        output = process[0]
        emptyField = process[1]
        print output
        alert = "Fully Executed"

    else:
        output = "Not Valid Path"
        emptyField = "Not Valid Path"
        alert = "Not Executed"

    print (alert)

    context = {'file_path': file_path,
               'output' : output,
               'alert' : alert,
               'error' : emptyField}

    return render(request, "home/home.html", context)

# PDF_to_Image Home Screen
def pdf_home(request):
    file_name = FileName.objects.all()
    context = {'file_name': file_name}
    return render(request, "pdf_home/pdf_home.html", context)

# Getting file path for processing the PDF
def pdf_file_path(request):

    # Getting Value of file path
    file_path = request.POST.get('fname')
    print (file_path)

    if str(file_path).endswith(".pdf"):
        # For conversion of single file
        process = pdf_exception_handling(file_path)
        output = process[0]
        emptyField = process[1]

    elif (str(file_path).endswith("\\")) or (str(file_path).endswith("/")):
        # For multiple PDF files
        for root, dir, files in os.walk(file_path):
            for single_pdf in files:
                if single_pdf.endswith(".pdf"):
                    single_pdf_path = file_path + "\\" + single_pdf
                    process = pdf_exception_handling(single_pdf_path)
                    output = process[0]
                    emptyField = process[1]

    else:
        output = "Not Valid Path"
        emptyField = "Not Valid Path"

    alert = "Fully Executed"
    print (alert)

    context = {'file_path': file_path,
               'output' : output,
               'alert' : alert,
               'error' : emptyField}

    return render(request, "pdf_home/pdf_home.html", context)

# PDF to PDF Home Screen
def pdf2pdf_home(request):
    file_name = FileName.objects.all()
    context = {'file_name': file_name}
    return render(request, "pdf2pdf/pdf2pdf_home.html", context)

# Function for conversion of PDF to searchable PDF
def pypdfocr(file_path, oldest_path):
    os.system("python pypdfocr.py " + file_path)
    os.rename(file_path, oldest_path)
    emptyField = "Fully Executed"
    return emptyField

# Exception handing for logic of PDF2PDF Converter
def pdf2pdf_exception_handling(file_path, oldest_path):
    try:
        output = pypdfocr(file_path, oldest_path)
        emptyField = "Fully Executed"
    except Exception as e:

        # Check if path is empty or directory is invalid.
        pathObj = re.search(validDirec, file_path, re.I | re.M)
        if file_path == "":
            emptyField = "Enter Path!"
            output = "Enter Path"

        elif not pathObj:
            emptyField = "Not Valid Path"
            output = "Not Valid Path"

        else:
            emptyField = "Some Error"
            output = e

    return output, emptyField

def pdf2pdf_process(path):
    
    path_split = str(path).split("\\")
    old_file_name = path_split[len(path_split)-1]
    oldest_path = path

    if "-" in old_file_name:
        newFile = old_file_name.split("-")
        file_name = newFile[0] + ".pdf"

    else:
        file_name = old_file_name

    old_path = path
    new_path = str(path).replace(old_file_name, file_name)
    os.rename(old_path, new_path)
    print (old_file_name)
    print ("python pypdfocr.py " + new_path)
    os.system("python pypdfocr.py " + new_path)
    os.rename(new_path, oldest_path)

def pdf2pdf_threading(path):

    count = 0

    f = open("D:\\File_list.csv")
    reader = csv.DictReader(f)

    for row in reader:
        processed_file_list.append(str(row["Path"]))

    # Getting all the file list available in given path
    for root, dir, files in os.walk(path):
        for singFile in files:

            if str(singFile).endswith(".pdf"):
                total_file_listing.append(singFile)

                full_path = root + "\\" + singFile

                if "/" in full_path:
                    full_path.replace("/", "\\")
                else:
                    pass

                full_path_list.append(full_path)

    # Checking if file is already processed or not
    for i in total_file_listing:
        if i not in processed_file_list:
            index = total_file_listing.index(i)
            element = full_path_list[index]

            # Appending to list in which contains files to be processed.
            files_to_be_processed.append(element)

    # Creating Groups
    item = 0
    while item < len(files_to_be_processed):
        four_file_group.append(files_to_be_processed[item:(item+4)])
        item = item + 4

    # Creating 4 threads per 4 files
    for group in four_file_group:
        count = count + 4

        # Threading starts
        t1 = Thread(target=pdf2pdf_process, args=(group[0],))
        t1.start()
        try:
            t2 = Thread(target=pdf2pdf_process, args=(group[1],))
            t2.start()
        except:
            pass

        try:
            t3 = Thread(target=pdf2pdf_process, args=(group[2],))
            t3.start()
        except:
            pass

        try:
            t4 = Thread(target=pdf2pdf_process, args=(group[3],))
            t4.start()
        except:
            pass

        # Wait for threads to complete
        t1.join()
        t2.join()
        t3.join()
        t4.join()

        print (str(count) + ":" + " files has been OCR'd")
    emptyField = "Fully Executed"
    output = "Don't Know"
    return emptyField, output

# Performs all the logic for conversion of PDF to searchable PDF

def pdf2pdf_file_path(request):
    # Getting Value of file path
    file_path = request.POST.get('fname')
    print (file_path)

    if str(file_path).endswith(".pdf"):
        # For conversion of single file
        filen = str(file_path).split("\\")
        singFile = filen[len(filen)-1]
        old_file = str(singFile)

        root = str(file_path).replace(singFile,"")
        oldest_path = root + old_file

        if "-" in singFile:
            newFile = singFile.split("-")
            file_name = newFile[0] + ".pdf"

        else:
            file_name = singFile

        old_path = root + singFile
        print "old Path: ", old_path
        new_path = root + file_name
        print "new Path: ", new_path
        os.rename(old_path, new_path)
        print singFile
        process = pdf2pdf_exception_handling(new_path, oldest_path)
        output = process[0]
        emptyField = process[1]

    elif (str(file_path).endswith("\\")) or (str(file_path).endswith("/")):
        # For multiple PDF files
        # for root, dir, files in os.walk(file_path):
        #     for singFile in files:
        #         if str(singFile).endswith(".pdf"):

        #             old_file = singFile
        #             oldest_path = root + "\\" + old_file

        #             if "-" in singFile:
        #                 newFile = singFile.split("-")
        #                 file_name = newFile[0] + ".pdf"

        #             else:
        #                 file_name = singFile

        #             old_path = root + "\\" + singFile
        #             new_path = root + "\\" + file_name
        #             os.rename(old_path, new_path)
        #             print singFile
        #             process = pdf2pdf_exception_handling(new_path, oldest_path)

        #             output = process[0]
        #             emptyField = process[1]
        out = pdf2pdf_threading(file_path)
        output = out[0]
        emptyField = out[1]

    else:
        output = "Not Valid Path"
        emptyField = "Not Valid Path"

    alert = "Fully Executed"
    print (alert)

    context = {'file_path': file_path,
               'output': output,
               'alert': alert,
               'error': emptyField}

    return render(request, "pdf2pdf/pdf2pdf_home.html", context)

# Handles exception occurred in single_file_path
def path_exception_handling(file_path):
    try:
        output = UT.single_file_tesseract(file_path)
        emptyField = "Fully Executed"
    except Exception as e:

        # Check if path is empty or directory is invalid.
        pathObj = re.search(validDirec, file_path, re.I | re.M)
        if file_path == "":
            emptyField = "Enter Path!"
            output = "Enter Path"

        elif not pathObj:
            emptyField = "Not Valid Path"
            output = "Not Valid Path"

        else:
            emptyField = "Some Error"
            output = e

    return output, emptyField

# Handles exception occurred in multi_file_path
# def multi_path_exception_handling(file_path, image_path, folder_path, single_image):
def multi_path_exception_handling(file_path, folder_path):
    try:
        # output = UT.multi_file_tesseract(image_path, folder_path, single_image)
        output = UT.multi_file_tesseract(file_path, folder_path)
        emptyField = "Fully Executed"
    except Exception as e:

        # Check if path is empty or directory is invalid.
        pathObj = re.search(validDirec, file_path, re.I | re.M)
        if file_path == "":
            emptyField = "Enter Path!"
            output = "Enter Path"

        elif not pathObj:
            emptyField = "Not Valid Path"
            output = "Not Valid Path"

        else:
            emptyField = "Some Error"
            output = e

    return output, emptyField

# Handles exceptions in PDF file path.
def pdf_exception_handling(file_path):
    try:
        output = UT.pdf_to_image(file_path)
        emptyField = "Fully Executed"
    except Exception as e:

        # Check if path is empty or directory is invalid.
        pathObj = re.search(validDirec, file_path, re.I | re.M)
        if file_path == "":
            emptyField = "Enter Path!"
            output = "Enter Path"

        elif not pathObj:
            emptyField = "Not Valid Path"
            output = "Not Valid Path"

        else:
            emptyField = "Some Error"
            output = e

    return output, emptyField

# Function for the concept of Proof Reading
def proofread(request):
    file_name = FileName.objects.all()

    data = UT.tesseract_data("D:\NonOCR\PNG\\0681Q00000FqEFYQA3.pdf\\0681Q00000FqEFYQA3.pdf-page2.png")

    image = data[0]
    image_data = data[1]

    # Initializing empty lists
    X = []
    keysList = ["left", "top", "conf", "text"]

    for key in keysList:
        X.append(image_data[key])

    # Result of transpose matrix
    result = [[X[j][i] for j in range(len(X))] for i in range(1, len(X[0]))]

    newResult = []

    # For removing list elements with confidence score '-1', blanks and spaces.
    for i in result:
        if (i[2] == "-1") or (i[3] == "") or (i[3] == " "):
            pass
        else:
            newResult.append(i)

    # For increasing the top value by 20.
    conf_list = [] # List of confidence score
    for i in newResult:
        i[1] = (int(i[1]) + 20)
        # For calculating average confidence score of single page
        conf_list.append(i[2])
        
    # Total number of scores
    total_score = len(conf_list) * 100
    
    # Calculating sum of all scores
    total_sum = 0
    for i in conf_list:
        total_sum = total_sum + i
        
    # Calculating the percentage
    percentage = (total_sum/total_score) * 100

    # Passing thre content to the HTML Page.
    context = {'file_name': file_name,
               'result': newResult,
               'image': image,
               'percent': ("{0:.2f}".format(percentage)),
               }
    return render(request, "proofread/proofread.html", context)

# Class containing teh code for text comparison
# class text_similarity(request):

def similarity_calculator(source, target, model):

    with open(stopwords_path, 'r') as fh:
        stopwords = fh.read().split(",")
    ds = DocSim(model,stopwords=stopwords)

    source_doc = str(source)
    target_docs = str(target)

    print "Calculating the similarity score."
    # Result of similarity (returns score, source doc vector, target doc vectors)
    result = ds.calculate_similarity(source_doc, target_docs)
    
    sim_scores = result[0]
    # print str(sim_scores)
    print "Source Doc: " + source_doc + "\n"
    print "Target Doc: " + target_docs + "\n"
    
    if len(sim_scores) != 0:
        score = sim_scores[0]["score"]
        print("Similarity Score: " , score)
        percentage = score * 100
        print "Percentage: ", str(percentage)

    else:
        score = 0
        print("Similarity Score: " , score)
        percentage = score * 100
        print "Empty List"
        
    return (percentage)

def looper(result, model, src_ind, tar_ind, threshold):
    count = 0
    # List for containing similar sentences.
    tar_sent = []
    src_sent = []

    for i in result:
        source= str(i[src_ind])
        target= str(i[tar_ind])

        per = similarity_calculator(source, target, model)
        print "Sentence " + str(count) + " is compared. And percentage is " + str(per)

        if per >= threshold:
            new_tar_str = str(target)
            new_src_str = str(source)
            tar_sent.append(new_tar_str)
            src_sent.append(new_src_str)

    return tar_sent, src_sent

def thread_ripper(source, item, model):
    
    for j in source:
        per = similarity_calculator(j, item, model)
        per_sent_queue.put([per, str(j), item])

def each_line_checker(model, source, target1, threshold):
    # List for storing the sentence which will be returned for the output
    src_sent = []
    tar_sent = []
    lis = []

    # item = 0
    # while (item<len(target1)):
    #     lis.append(target1[item:item+4])
    #     item = item + 4

    # # Loop for checking 4 sentences at the same time in source document.
    # for i in lis:
    #     thread_list = []

    #     # Threading
    #     t1 = Thread(target= thread_ripper, args=(source,i[0], model,))
    #     t1.start()
    #     thread_list.append(t1)

    #     try:
    #         t2 = Thread(target= thread_ripper, args=(source,i[1], model,))
    #         t2.start()
    #         thread_list.append(t2)
    #     except:
    #         pass

    #     try:
    #         t3 = Thread(target= thread_ripper, args=(source,i[2], model,))
    #         t3.start()
    #         thread_list.append(t3)
    #     except:
    #         pass

    #     try:
    #         t4 = Thread(target= thread_ripper, args=(source,i[3], model,))
    #         t4.start()
    #         thread_list.append(t4)
    #     except:
    #         pass

    #     t1.join()
    #     t2.join()
    #     t3.join()
    #     t4.join()

    '''Calculate the percentage and store it in a list'''
    for i in target1:
        for j in source:
            per = similarity_calculator(j, i, model)
            per_sent_queue.put([per, str(j), i])

            # Queue converted to list in form [[per,atr],[percentage,string]]
            queue_list = list(per_sent_queue.queue)
            try:
                # Find out the index of greatest percentage.
                max_per_index = queue_list.index(max(queue_list))

                # Getting list which contains max percentage
                max_per_list = queue_list[max_per_index]

                # Final max percentage and corresponding sentence.
                final_percentage = max_per_list[0]
                final_src_sentence = max_per_list[1]
                final_tar_sentence = max_per_list[2]
            except Exception:
                final_percentage = 0
                final_src_sentence = ""
                final_tar_sentence = ""

            if final_percentage > threshold:
                src_sent.append(final_src_sentence)
                tar_sent.append(final_tar_sentence)

    return tar_sent, src_sent

def main_function(request, source_file_name="", target_file_name="", threshold=0):

    timer = []

    # Start time of function
    start_time = datetime.datetime.now()
    timer.append(start_time)

    #Open files for checking similarities
    source_file_name = "C:\\Users\\Lakshay.s\\Desktop\\document-similarity-master\\docs\\77849-AFS(Fully-Executed_Contract)[t1_v1].txt"
    target_file_name = "C:\\Users\Lakshay.s\\Desktop\\document-similarity-master\\docs\\06836000003k8erAAA.txt"
    csv_file_name ="C:\\Users\Lakshay.s\\Desktop\\document-similarity-master\\Output\\List_Cmp.csv"
    file1 = open(source_file_name, "r+")
    file2 = open(target_file_name, "r+")
    file3 = open(csv_file_name, "w+")

    # Getting file names
    src_name_lis = source_file_name.split("\\")
    src_name = src_name_lis[len(src_name_lis)-1]

    tar_name_lis = target_file_name.split("\\")
    tar_name = tar_name_lis[len(tar_name_lis)-1]

    # Threshold value for testing purpose
    threshold = 60

    # Writer for CSV file
    w = csv.writer(file3, quoting=csv.QUOTE_ALL, delimiter=',')
    w.writerow(['Target', "Out_Str_Lis"])

    # Read the contents
    source = file1.read().split(". ")
    print "No. of sentences in source doc: ", str(len(source))
    target = file2.read().split(". ")
    print "No. of sentences in target doc: ", str(len(target))

    # Length of list of doc sentences.
    src_len = len(source)
    tar_len = len(target)

    if src_len < tar_len:
        X = [source, target]
        src_ind = 0
        tar_ind = 1
        greater = target
        smaller = source
        
    elif tar_len < src_len:
        X = [target, source]
        src_ind = 1
        tar_ind = 0
        greater = source
        smaller = target
        
    else:
        X = [source, target]
        src_ind = 0
        tar_ind = 1
        greater = source
        smaller = target

    # Result of transpose matrix
    result = [[X[j][i] for j in range(len(X))] for i in range(0, len(X[0]))]

    # Model
    model = KeyedVectors.load_word2vec_format(googlenews_model_path, binary=True)

    # Function for processing the similarity.
    # out_str_lis = looper(result, model, src_ind, tar_ind, threshold)

    out_str_lis = each_line_checker(model, greater, smaller, threshold)

    # Lists containing similar strings
    target_list = out_str_lis[0]
    source_list = out_str_lis[1]
    
    # Closing all the files.
    file1.close()
    file2.close()
    file3.close()

    source_file = open(source_file_name, "r+")

    context = {
        "source": source,
        "target": target,
        "target_list": target_list,
        "source_list": source_list,
        "src_name": src_name,
        "tar_name": tar_name,
    }

    # End Time
    end_time = datetime.datetime.now()
    timer.append(end_time)

    # # Length of lists
    # out_str_len = len(out_str_lis)
    # tar_len = len(target)

    # # Conditions for checking the smaller length list and appending blanks to it
    # if out_str_len < tar_len:
    #     diff = tar_len - out_str_len
    #     for i in range(diff):
    #         out_str_lis.append("")
        
    # elif tar_len < out_str_len:
    #     diff = out_str_len - tar_len
    #     for i in range(diff):
    #         target.append("")

    # else:
    #     pass

    # # List for containing the lists which we need to obtain in output
    # csv_write = [target, out_str_lis]

    # # Transpose Matrix
    # result1 = [[csv_write[j][i] for j in range(len(csv_write))] for i in range(0, len(csv_write[0]))]

    # for i in result1:
    #     w.writerow([i[0], i[1]])

    print "Task Completed"
    print "Start Time: " + str(timer[0])
    print "End Time: " + str(timer[1])

    return render(request, "text_sim/txt_sim.html", context)

class progress_view(generic.View):
    template_name = "progressbar/display_progress.html"

    def printer_func(self, request):
        var = "Hello World"

        context = {
            'var': var,
        }

        return render(request, template_name, context)

    # def main_function():
