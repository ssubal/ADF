import io
import os
import sys 
import getopt
import string
import nltk
import re
import PyPDF2
import shutil
import math
import fitz
import pandas
import django
import numpy as np
import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

from io import StringIO
from os import read

from pymongo import MongoClient
from operator import itemgetter

from invoice2data import extract_data
from invoice2data.extract.loader import read_templates

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter,TextConverter,XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from nltk import tokenize
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer

client = MongoClient('mongodb://localhost:27017/')
#..............#
def upload(request):
    return render(request, 'upload/upload.html')

#.............#
def comp(s):
    tmp = int(s[7:])
    return tmp

#.............#
def script(current_folder,url,name,doctype):
    #print("Script working ??")
    client = MongoClient('mongodb://localhost:27017/')
    def extract_email_info(text):
        fh = text
        mydict = {}

        # TO: extraction
        index_num = fh.find('To:')
        if(index_num!=-1):
            begore_to = fh[ : index_num]
            after_to = fh[index_num : ]
            index_num = after_to.find('\n\n')
            emails_to = after_to[ : index_num]
            to = emails_to.replace('\n'," ")
            x = re.findall("To:.*", to)
            y = x[0][4:]
            res = y.replace(", ", " ").split()
            mydict['To'] = res

        # #  From:
        match = re.findall("Forwarded message.*", fh)
        #print(match)
        flag = 1
        if(len(match)==0):
            flag = 0

        from_list = []
        # chunks = fh.split('\n')
        # valueToBeRemoved = ''
        # myList = [value for value in chunks if value != valueToBeRemoved]
        # from_list.append(myList[2])
        #print(from_list)
        match = re.findall("<\w\S*@*.\w>", fh)
        # match[1]
        from_list.extend(match)
        
        if(flag):    # implies message is foorwarded
            for line in re.findall("From:.*", fh):
                from_list.append(line[6:])
                
        from_list = list(dict.fromkeys(from_list))
        for item in from_list:
            target_string_lower = item[1:len(item)-1]
            #print(target_string_lower,item)
            is_target_in_list = target_string_lower in (string.lower() for string in res)
            temp = item in (string.lower() for string in res)
            #print(is_target_in_list,temp)
            if(is_target_in_list):
                from_list.remove("<" + target_string_lower + ">")
            if(temp):
                from_list.remove(item)
        mydict['From'] = from_list

        # # Recieved timestamp
        temp = re.findall('(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),[\s-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s-]\d{2,4},[\s-]\d{4}', fh)
        date = datetime.datetime.strptime(temp[0], '%a, %b %d, %Y')
        mydict['date'] =  date

        # # Subject
        chunks = fh.split('\n')
        valueToBeRemoved = ''
        myList = [value for value in chunks if value != valueToBeRemoved]
        #mydict['Subject'] = chunks[2]
        match = re.findall("<\w\S*@*.\w>", myList[2])
        if(len(match)):
            sub = myList[3]
        else:
            sub = myList[2]
        mydict['Subject'] = sub

        # # Attachments
        index_num = fh.find('attachments')
        begore_attachments = fh[ : index_num]
        after_attachments = fh[index_num : ]

        attachments = []
        pdfs = re.findall('\S+.pdf', after_attachments)
        docx = re.findall('\S+.docx', after_attachments)
        pptx = re.findall('\S+.pptx', after_attachments)
        jpg = re.findall('\S+.jpg', after_attachments)
        png = re.findall('\S+.png', after_attachments)
        zips = re.findall('\S+.zip', after_attachments)
        txt = re.findall('\S+.txt', after_attachments)
        json = re.findall('\S+.json', after_attachments)
        ics = re.findall('\S+.ics', after_attachments)
        attachments +=pdfs+docx+jpg+png+zips+txt+json+ics
        mydict['Attachments'] = attachments

        # Body
        index_num = fh.find(temp[0])
        after_date = fh[index_num : ]
        index_num = after_date.find('attachments')
        before = after_date[:index_num]
        chunks = before.split('\n')
        valueToBeRemoved = ''
        myList = [value for value in chunks if value != valueToBeRemoved]
        body = myList
        body_str = ""
        len(body)
        type(body[1])
        for i in range(1,len(body)):
            body_str = body_str+body[i]
        body_str = " ".join(body_str.split())
        mydict['Body'] = body_str
        
        return mydict

    def extract_header_para_keywords(file_path):
    
        doc = fitz.open(file_path)

        def fonts(doc):

            styles = {}
            font_counts = {}
            idx = 0
            for page in doc:
                blocks = page.getText("dict")["blocks"]
                idx += 1
                for b in blocks:  # iterate through the text blocks
                    if b['type'] == 0:  # block contains text
                        for l in b["lines"]:  # iterate through the text lines
                            for s in l["spans"]:  # iterate through the text span
                                identifier = "{0}".format(s['size'])
                                styles[identifier] = {'size': s['size'], 'font': s['font']}
                                font_counts[identifier] = font_counts.get(identifier, 0) + 1  
                
            font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

            if len(font_counts) < 1:
                raise ValueError("Zero discriminating fonts found!")

            return font_counts, styles


        # if granularity = False, then headers will be extracted on the basis of font and size
        font_counts, styles = fonts(doc)

        def font_tags(font_counts, styles):

            p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
            p_size = p_style['size']  # get the paragraph's size
            
            # sorting the font sizes high to low, so that we can append the right integer to each tag 
            font_sizes = []
            for (font_size, count) in font_counts:
                font_sizes.append(float(font_size))
            font_sizes.sort(reverse=True)

            # aggregating the tags for each font size
            size_tag = {}
            for size in font_sizes:
                if size == p_size:
                    size_tag[size] = '<p>'
                if size > p_size:
                    size_tag[size] = '<h>'
                elif size < p_size:
                    size_tag[size] = '<s>'

            return size_tag




        size_tag = font_tags(font_counts, styles)
        #print(size_tag)


        # Extracting headers, paragraphs and subscripts 



        def headers_para(doc, size_tag):
            first = True  # boolean operator for first header
            previous_s = {}  # previous span
            res = {}
            k = 1
            for page in doc:
                header_para = []  # list with headers and paragraphs
                blocks = page.getText("dict")["blocks"]
                #print(blocks)
                for b in blocks:  # iterate through the text blocks
                    if b['type'] == 0:  # this block contains text

                        # REMEMBER: multiple fonts and sizes are possible IN one block

                        block_string = ""  # text found in block
                        for l in b["lines"]:  # iterate through the text lines
                            #print(l)
                            for s in l["spans"]:  # iterate through the text spans
                                #print(s)
                                if s['text'].strip():  # removing whitespaces:
                                    #print(s['text'])
                                    if s['font'].find('Bold') != -1 and s['font'].find('Italic') == -1:
                                        previous_s = s
                                        block_string = "<h>" + s['text']    
                                    elif first:
                                        previous_s = s
                                        first = False
                                        block_string = size_tag[s['size']] + s['text']
                                    else:
                                        if s['size'] == previous_s['size'] and s['font'] == previous_s['font']:

                                            if block_string and all((c == "|") for c in block_string):
                                                # block_string only contains pipes
                                                block_string = size_tag[s['size']] + s['text']
                                            if block_string == "":
                                                # new block has started, so append size tag
                                                block_string = size_tag[s['size']] + s['text']
                                            else:  # in the same block, so concatenate strings
                                                block_string += " " + s['text']

                                        else:
                                            header_para.append(block_string)
                                            block_string = size_tag[s['size']] + s['text']

                                        previous_s = s

                        # new block started, indicating with a pipe
                        # block_string += "|"
                        header_para.append(block_string)
                key = []
                value = []
                for i in header_para:
                    if i == '':
                        continue
                    else:
                        flag = 1
                        s=""
                        t=""
                        for j in i:
                            if flag:
                                s = s + j
                            else:
                                t = t + j
                            if j == '>':
                                flag=0
                        key.append(s)
                        value.append(t)
                class Dictlist(dict):
                    def __setitem__(self, key, value):
                        try:
                            self[key]
                        except KeyError:
                            super(Dictlist, self).__setitem__(key, [])
                        self[key].append(value)
                d = Dictlist()
                i = 0
                while i < len(key):

                    d[key[i]]=value[i]
                    i+=1
                res[k] = d
                k = k+1  
            return res



        header_para = headers_para(doc, size_tag)
        #print(header_para)


        # Keywords from paragraphs and subscripts


        def clean_text(sentence, stopwords_list, punct):
            corpus=list()
            # remove punctuations
            sentence = re.sub('[^a-zA-Z]', ' ', sentence)
            
            # convert to lower case
            sentence = str(sentence).lower()
            
            # remove tags
            sentence = re.sub("&lt;/?.*?&gt;"," &lt;&gt; ",sentence)
            
            #remove special characters
            sentence = re.sub("(\\d|\\W)+"," ",sentence)

            # remove urls
            sentence = re.sub(r"http\S+", "", sentence)
            sentence = re.sub(r"www\S+", "", sentence)
            # stop words
            #stopwords_list = set(stopwords.words('english'))
            
            # convert from string to list
            #sentence = sentence.split()
            word_list = word_tokenize(sentence)
            # remove stop words
            word_list = [word for word in word_list if word not in stopwords_list]
            # remove very small words, length < 3 as they don't contribute any useful information
            word_list = [word for word in word_list if len(word) > 2]
            # remove punctuation
            word_list = [word for word in word_list if word not in punct]
            
            #stemming
            ps  = PorterStemmer()
            #word_list = [ps.stem(word) for word in word_list]
            
            # lemmatize
            lemma = WordNetLemmatizer()
            sentence = [lemma.lemmatize(word) for word in word_list if not word in stopwords_list]
            sentence = " ".join(word_list)
            corpus.append(sentence)
            return sentence
        # this function is returing list  



        #Most frequently occuring words
        def get_top_ngrams(corpus, n=None, N=1):
            vec = CountVectorizer(ngram_range=(N,N), max_features=500).fit(corpus)
            bag_of_words = vec.transform(corpus)
            sum_words = bag_of_words.sum(axis=0) 
            words_freq = [(word, sum_words[0, idx]) for word, idx in      
                        vec.vocabulary_.items()]
            words_freq =sorted(words_freq, key = lambda x: x[1], 
                            reverse=True)
            return words_freq[:n]


        def check_sent(word, sentences):
            final = [all([w in x for w in word]) for x in sentences]
            sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
            return int(len(sent_len))

        def get_top_n(dict_elem, n):
                result = dict(sorted(dict_elem.items(), key = itemgetter(1), reverse = True)[:n]) 
                return result    



        stopwords_list = set(stopwords.words('english'))
        punct = set(string.punctuation)
        d = {}
        text =""
        idx = 0
        for item in header_para:
            text = ""
            idx = idx + 1
            for key in header_para[item]:
                if key == '<p>':    
                    temp = ""
                    for i in header_para[item][key]:
                        temp += i 
                    corpus = clean_text(temp, stopwords_list = stopwords_list, punct = punct)
                    temp = "".join(corpus) 
                    header_para[item][key] = temp     
                    text += temp
                    #print(temp)
                elif key == '<s>':
                    temp = ""
                    for i in header_para[item][key]:
                        temp += i 
                    corpus = clean_text(temp, stopwords_list = stopwords_list, punct = punct)
                    temp = "".join(corpus)
                    header_para[item][key] = temp
                    text += temp
                #print(temp)
            doc = text
                
            total_words = doc.split()
            total_word_length = len(total_words)

            total_sentences = tokenize.sent_tokenize(doc)
            total_sent_len = len(total_sentences)

            tf_score = {}
            for each_word in total_words:
                each_word = each_word.replace('.', '')
                if each_word not in stopwords_list:
                    if each_word in tf_score:
                        tf_score[each_word] += 1
                    else:
                        tf_score[each_word] = 1
            tf_score.update((x, y/int(total_word_length)) for x, y in tf_score.items())

            idf_score = {}
            for each_word in total_words:
                each_word = each_word.replace('.','')
                if each_word not in stopwords_list:
                    if each_word in idf_score:
                        idf_score[each_word] = check_sent(each_word, total_sentences)
                    else:
                        idf_score[each_word] = 1


                # Performing a log and divide
            idf_score.update((x, math.log(int(total_sent_len)/y)) for x, y in idf_score.items())
                
            tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}   

            lst = []
            for key in get_top_n(tf_idf_score, 10):
                if(len(key)>2):
                    lst.append(key)
                    lst  
            d[idx] = lst
    
        idx = 1
        temp = {}
        for item in header_para:
            if idx in d:
                temp['keywords'] = d[idx]
                header_para[item].update(temp)
                temp.clear()
            else:
                temp['keywords'] = []  
                header_para[item].update(temp)
                temp.clear()
            idx = idx + 1  
        return header_para


    def convert(file_path, file_name,doc_type,header_para_key, pages=None,):

        if(doc_type=="Email"):
            def convert(fname, pages=None):
                if not pages: pagenums = set()
                else:         pagenums = set(pages);      
                manager = PDFResourceManager() 
                codec = 'utf-8'
                caching = True
                output = io.StringIO()
                converter = TextConverter(manager, output,  laparams=LAParams()) 
    
                interpreter = PDFPageInterpreter(manager, converter)   
                infile = open(fname, 'rb')
                i = 1
                for page in PDFPage.get_pages(infile, pagenums,caching=caching, check_extractable=True):
                    #print("***page no.***",i)
                    i+=1
                    interpreter.process_page(page)
                    #print(output.getvalue())

                convertedPDF = output.getvalue()

                infile.close(); converter.close(); output.close()
                return convertedPDF
            text = convert(file_path)
            content_text = " ".join(text.split())
            mydict = {"doc_type":"Email", "file_name": file_name, "file_path": current_folder,"content_text": content_text}

            header_lst = []
            sub_lst = []
            para = ""
            keyword_lst = []
            for i in range(1,len(header_para_key)+1):
                #print(i)
                temp_dict = header_para_key[i]
                if(len(temp_dict['<p>'])!=0):
                    para = para + temp_dict['<p>'][len(temp_dict['<p>'])-1]
                if(len(temp_dict['<h>'])!=0):
                    header_lst = header_lst + temp_dict['<h>']
                if(len(temp_dict['<s>'])!=0):
                    sub_lst = sub_lst + temp_dict['<s>']
                if(len(temp_dict['keywords'])!=0):
                    keyword_lst = keyword_lst + temp_dict['keywords']
                
            mydict['headers'] = header_lst
            mydict['paragraphs'] = para
            mydict['subscripts'] = sub_lst
            mydict['keywords'] = keyword_lst
            email_dict = extract_email_info(text)
            mydict = {**mydict,**email_dict}
            client.adf_main.adf_frontend.insert(mydict)

        else:

            if not pages: pagenums = set()
            else:         pagenums = set(pages)
            manager = PDFResourceManager()
            codec = 'utf-8'
            caching = True

            output = io.StringIO()
            converter = TextConverter(manager, output,  laparams=LAParams())

            interpreter = PDFPageInterpreter(manager, converter)
            infile = open(file_path, 'rb')
            page_no = 0
            for pageNumber , page in enumerate(PDFPage.get_pages(infile, pagenums,caching=caching, check_extractable=True)):
                
                if pageNumber == page_no:
                    interpreter.process_page(page)

                    text = output.getvalue()
                    content_text = " ".join(text.split())
                    mydict = {"doc_type":"Others", "file_name": file_name, "file_path": current_folder,"content_text": content_text, "page_number": page_no+1}
                    temp_dict = header_para_key[page_no+1]

                    key = '<h>'
                    if key in temp_dict.keys():
                        mydict['headers'] = temp_dict['<h>']
                    else:
                        mydict['headers'] = []
                    key = '<p>'
                    if key in temp_dict.keys():
                        mydict['paragraphs'] = temp_dict['<p>'][len(temp_dict['<p>'])-1]
                    else:
                        mydict['paragraphs'] = []
                    key = 'keywords'
                    if key in temp_dict.keys():
                        mydict['keywords'] = temp_dict['keywords']
                    else:
                        mydict['keywords'] = []
                    key = '<s>'
                    if key in temp_dict.keys():
                        mydict['subscripts'] = temp_dict['<s>']
                    else:
                        mydict['subscripts'] = []
                    
                    #print(mydict)
                    # inserts document in mongoDB database
                    client.adf_main.adf_frontend.insert(mydict)
                    text = ''
                    output.truncate(0)
                    output.seek(0)
                page_no += 1
            

    file_path = url
    doc_type = doctype
    header_para_key = extract_header_para_keywords(file_path)
    convert(file_path,name,doc_type,header_para_key)



def Update(request):
    #context={}
    if request.method == 'POST':
        BASE_DIR = '/home/suraj/Dev/trydjango/projects/adf_main/media/'
        list=os.listdir(BASE_DIR)
        list.sort(key=comp)
        current_folder = list[-1]
        dir_Path=os.path.join(BASE_DIR,current_folder)
        count = len(os.listdir(dir_Path))
        
        files = request.FILES.getlist('myfile')
        for uploaded_file in files:
            FileName = uploaded_file.name
        
            fs = FileSystemStorage()
            name = fs.save(FileName, uploaded_file)
            if(count>=2):
                count=0
                folder_no = int(current_folder[7:])
                current_folder='folder_{}'
                current_folder=current_folder.format(folder_no+1)
                dir_Path=os.path.join(BASE_DIR,current_folder)
                os.makedirs(dir_Path)
            
            url= shutil.move(BASE_DIR+name, dir_Path+'/'+name)
            count+=1
            #fname = url
            
            if request.POST["doc_type"] == "Invoice":
                doc = fitz.open(url)
                fh = ""
                for page in doc:
                    fh = fh + str(page.getText())
                if request.POST['Issuer'] == "Amazon":

                    # text = convert('text', filePDF, pages=None)
                    pagenums = set()
                    manager = PDFResourceManager()
                    codec = 'utf-8'
                    caching = True
                    output = io.StringIO()
                    converter = TextConverter(
                        manager, output,  laparams=LAParams())
                    interpreter = PDFPageInterpreter(manager, converter)
                    infile = open(url, 'rb')
                    i = 1
                    for page in PDFPage.get_pages(infile, pagenums, caching=caching, check_extractable=True):
                        #print("***page no.***",i)
                        i += 1
                        interpreter.process_page(page)

                    text = output.getvalue()

                    infile.close()
                    converter.close()
                    output.close()

                    import re
                    mydict1 = {}
                    match = re.findall("Invoice Date :.*", text)
                    mydict1['doc_type'] = "Invoice"
                    mydict1['file_name'] = name
                    mydict1['file_path'] = current_folder
                    tt = match[0][15:21]+match[0][23:]
                    # tt = tt[:7]+tt[9:]
                    tt = tt + " 00:00:00"
                    mydict1['date'] = datetime.datetime.strptime(tt, '%d.%m.%y %H:%M:%S')
                    match = re.findall("PAN No:.*", text)
                    mydict1['Pan No'] = match[0][8:]
                    match = re.findall("Order Date:.*", text)
                    tt = match[0][12:18]+match[0][20:]
                    # tt = tt[:7]+tt[9:]
                    tt = tt + " 00:00:00"
                    mydict1['Order Date'] = datetime.datetime.strptime(
                        tt, '%d.%m.%y %H:%M:%S')
                    match = re.findall("Invoice Number :.*", text)
                    mydict1['invoice_number'] = match[0][17:]
                    match = fh.find("TOTAL:")
                    amount = fh[match:].split()[2][1:]
                    s = amount.split(',')
                    amount = ""
                    for i in s:
                        amount = amount+i
                    mydict1['amount'] = float(amount)
                    index_num = text.find('Sl.\nNo')
                    after_date = text[index_num+7:]
                    index_num = after_date.find('Shipping Charges')
                    before = after_date[:index_num]
                    # mydict['Item'] = before
                    mydict1['content'] = " ".join(fh.split())
                    mydict1['issuer'] = 'Amazon'

                elif request.POST["Issuer"] == "Flipkart":
                    mydict1 = {}
                    templates = read_templates('templates/upload/flipkart_template')
                    tmp = extract_data(url, templates=templates)
                    mydict1=tmp
                    mydict1['doc_type'] = "Invoice"
                    mydict1['file_name'] = name
                    mydict1['file_path'] = current_folder
                    mydict1['content'] = " ".join(fh.split())

                elif request.POST["Issuer"] == "Oyo":
                    mydict1 = {}
                    templates = read_templates('templates/upload/oyo_template')
                    tmp = extract_data(url, templates=templates)
                    mydict1=tmp
                    mydict1['doc_type'] = "Invoice"
                    mydict1['file_name'] = name
                    mydict1['file_path'] = current_folder
                    mydict1['content'] = " ".join(fh.split())

                # print(mydict)

                client.adf_main.adf_frontend.insert(mydict1)

            elif request.POST["doc_type"] == "Email":
                script(current_folder,url,name,"Email")
            
            elif request.POST["doc_type"] == "Others":
                script(current_folder,url,name,"Others")

        return render(request, 'upload/upload.html')

    else:
        dic={}
        try:
            dic['type']=request.GET['type']
            
        except:
            pass
        return render(request, 'upload/upload.html',dic)
