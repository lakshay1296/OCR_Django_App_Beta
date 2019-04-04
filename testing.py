# # file_path = "C:\Data\sample.pdf"
# #
# # path = file_path.split("\\")
# #
# # filename = path[len(path)-1]
# #
# # print filename
# #
# # comman_for_git = "git pull origin master"
#
# import os
# import numpy as np
# try:
#     from PIL import Image
# except ImportError:
#     import Image
#
# # path = raw_input("Enter the path of directory: ")
# # for root, dir, files in os.walk(path):
# #     for singFile in files:
# #         if str(singFile).endswith(".pdf"):
# #             print singFile
# #             os.system("pypdfocr " + singFile)
# #
# #         else:
# #             pass
# #
# # singFile = "0681Q00000FqEFYQA3.pdf"
# # os.system("pypdfocr " + singFile)
#
# path = raw_input("Enter the path of directory: ")
# list_im = []
# for root , dir, files in os.walk(path):
#     for singFile in files:
#         if str(singFile).endswith(".png"):
#             new_path = path+"\\"+singFile
#             list_im.append(new_path)
#
# # Getting current folder name
# folder_name = str(os.path.basename(path))
# # Creating PNG Name through folder name
# file_name = folder_name[:-4]
#
# imgs = [Image.open(i) for i in list_im]
# min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
#
# # for a vertical stacking it is simple: use vstack
# imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
# imgs_comb = Image.fromarray( imgs_comb)
# imgs_comb.save(path + "\\" + file_name + '.png', 'PNG')
#
# # For removing PDF's Page PNG's
# for image in list_im:
#     os.remove(image)
#     print "File: " + str(image) + " removed."
