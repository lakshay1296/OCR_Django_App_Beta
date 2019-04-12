from django.conf.urls import url
from . import views

app_name = 'index'

urlpatterns = [
    # url: /index1/
    url(r'^$', views.index, name='index'),


    # url: /index1/index1/
    url(r'^home/$', views.home, name='home'),

    # url: /index1/123/
    url(r'^(?P<album_id>[0-9]+)/$', views.details, name='details'),

    # url: /index1/file_path
    url(r'^home/ocr_file_path/$', views.ocr_file_path, name='ocr_file_path'),

    # url: /index1/
    url(r'^pdf_home/$', views.pdf_home, name='pdf_home'),

    # url: /index1/file_path
    url(r'^pdf_home/pdf_file_path/$', views.pdf_file_path, name='pdf_file_path'),

    # url: /index1/file_path
    url(r'^pdf2pdf_home/$', views.pdf2pdf_home, name='pdf2pdf_home'),

    # url: /index1/file_path
    url(r'^pdf2pdf_home/pdf2pdf_file_path/$', views.pdf2pdf_file_path, name='pdf2pdf_file_path'),

    # url: /index1/file_path
    url(r'^proofread/$', views.proofread, name='proofread')

]
