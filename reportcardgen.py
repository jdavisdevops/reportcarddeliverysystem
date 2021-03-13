# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 02:01:13 2020

@author: josephdavis
"""

import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter
import uuid
import os
from IPython import get_ipython
import cx_Oracle


def extract_numbers(file_name):
    dsn_tns = cx_Oracle.makedsn(#insert Database credentials here)
    db = cx_Oracle.connect(user='#user', password='#password', dsn=dsn_tns)
    cursor = db.cursor()  # assign db operation to cursor variable
    filename = file_name  # assign input variable to pdf obj reader
    pdfFileObj = open(filename, 'rb')  # open allows you to read the file
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)  # The pdfReader variable is a readable object that will be parsed
    num_pages = pdfReader.numPages  # discerning the number of pages will allow us to parse through all the pages
    sql = '''UPDATE u_studentsuserfields u set u.ausd_hashkey = :hashid where u.studentsdcid = (SELECT s.dcid from 
    students s where s.dcid = u.studentsdcid and s.student_number = :stu_numid) '''
    count = 0
    a = "Student ID:"  # begin text search param
    b = "Teacher"  # end text search param
    text = ""  # instantiate variable to store student_number
    mergednums = []
    skipped = []
    for page in range(pdfReader.getNumPages()):
        while count < num_pages:  # The while loop will read each page
            pageObj = pdfReader.getPage(count)
            folder = 'finalcards'
            hash = str(uuid.uuid4())  # generate random hash key
            count += 1
            text += pageObj.extractText()
            if "ELD Report Card Emerging Level" in text:
                text = ""
                skipped.append(count-1)
                pass
            
            elif "School:" not in text and "Student ID:" not in text:
                text = ""
                pass
            
            elif "Teacher Signature" not in text and "Assigned to grade" not in text:
                stu_num = text.split(a)[-1].split(b)[0]
                stu_num = stu_num.replace("\n", "")
                stu_num = stu_num.strip()
                stu_num = str(stu_num)
                params = {'hashid':hash, 'stu_numid':stu_num}
                cursor.execute(sql, params)
                
                index = count
                page = pdfReader.getPage(index)
                pdf_writer = PdfFileWriter()
                pdf_writer.addPage(pageObj)
                pdf_writer.addPage(page)
                output_filename = '{}.pdf'.format(hash)

                with open(folder + '/' + output_filename, 'wb') as out:
                    pdf_writer.write(out)

                print('Created: {}'.format(output_filename))
                print("merged")
                text = ""
                mergednums.append(stu_num + ':')
                mergednums.append(hash)
            else:
                stu_num = text.split(a)[-1].split(b)[0]
                stu_num = stu_num.replace("\n", "")
                stu_num = stu_num.strip()
                stu_num = str(stu_num)
                params = {'hashid':hash, 'stu_numid':stu_num}
                cursor.execute(sql, params)
                
                pdf_writer = PdfFileWriter()
                pdf_writer.addPage(pageObj)
                output_filename = '{}.pdf'.format(hash)

                with open(folder + '/' + output_filename, 'wb') as out:
                    pdf_writer.write(out)

                print('Created: {}'.format(output_filename))
                text = ""          
    db.commit()
    cursor.close()
    db.close()
    
    with open("stunums.txt","w+") as f:
        for item in mergednums:
            f.write("%s\n" % item)
    with open("skipped.txt","w+") as f:
        for item in skipped:
            f.write("%s\n" % item)

def reportcards():
    directory = '.'
    for file_name in os.listdir(directory):
        if file_name.endswith(".pdf"):
            extract_numbers(file_name)
        else:
            continue
    get_ipython().magic('clear')
    print('Process Complete')


reportcards()
