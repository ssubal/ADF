from django.shortcuts import render
from pymongo import MongoClient
import datetime


def search(request):
    if request.method == 'POST':
        client =  MongoClient('mongodb://localhost:27017/')
        if request.POST["doc_type"] == 'Others':
            is_header = request.POST.get('header',False)
            is_para = request.POST.get('paragraph',False)
            if is_header:
                print("header selected")
            if is_para:
                print("Para selected")
            key_string = request.POST["keyword"]
            temp = '*'
            current = ""
            and_list=[]
            not_list=[]
            or_list=[]
            for i in key_string:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_list.append(current)
                    elif(temp=='-'):
                        not_list.append(current)
                    elif(temp=='|'):
                        or_list.append(current)

                    temp = i
                    current= ""

                else:
                    current+=i
            if(temp=='+'):
                and_list.append(current)
            elif(temp=='-'):
                not_list.append(current)
            elif(temp=='|'):
                or_list.append(current)
           
            #print([and_list,not_list,inc_list,dec_list])

            client = MongoClient('mongodb://localhost:27017/')
            docs=[]
            # ********************header selected************
            if is_header:
                dic={}
                dic['doc_type'] = 'Others'

                list1=[]#******list for and(+)***********
                dic1=dic
                if len(and_list):
                    for word in and_list:
                        list1.append({'headers': { '$regex': word, '$options': 'i' } })
                    dic1 = {'$and':[dic,{ '$and': list1}]}

                list2=[]#******list for not(-)***********
                dic2=dic
                if len(not_list):
                    for word in not_list:
                        list2.append({'headers': { '$regex': word, '$options': 'i' } })
                    dic2 = {'$and':[dic,{'$nor': list2}]}

                list3=[]#******list for or(|)***********
                dic3=dic
                if len(or_list):
                    for word in or_list:
                        list3.append({'headers': { '$regex': word, '$options': 'i' } })
                    dic3 = {'$and':[dic,{'$or': list3}]}

                list4=[]#******list for or(|)---doc. do not contain or_list keywords***********
                dic4=dic
                if len(or_list):
                    for word in or_list:
                        list4.append({'headers': { '$regex': word, '$options': 'i' } })
                    dic4 = {'$and':[dic,{'$nor': list4}]}

                doc1= client.adf_main.adf_frontend.find({'$and':[dic1,dic2,dic3]} )
                doc2= client.adf_main.adf_frontend.find({'$and':[dic1,dic2,dic4]} )
                
                #print(doc1.count())
                #print(doc2.count())
                if len(or_list):
                    docs.append(doc1)
                    docs.append(doc2)
                else:
                    docs.append(doc1)
# ********************paragraph selected************
            if is_para:
                dic={}
                dic['doc_type'] = 'Others'

                list1=[]#******list for and(+)***********
                dic1=dic
                if len(and_list):
                    for word in and_list:
                        list1.append({'paragraphs': { '$regex': word, '$options': 'i' } })
                    dic1 = {'$and':[dic,{ '$and': list1}]}

                list2=[]#******list for not(-)***********
                dic2=dic
                if len(not_list):
                    for word in not_list:
                        list2.append({'paragraphs': { '$regex': word, '$options': 'i' } })
                    dic2 = {'$and':[dic,{'$nor': list2}]}

                list3=[]#******list for or(|)***********
                dic3=dic
                if len(or_list):
                    for word in or_list:
                        list3.append({'paragraphs': { '$regex': word, '$options': 'i' } })
                    dic3 = {'$and':[dic,{'$or': list3}]}

                list4=[]#******list for or(|)---doc. do not contain or_list keywords***********
                dic4=dic
                if len(or_list):
                    for word in or_list:
                        list4.append({'paragraphs': { '$regex': word, '$options': 'i' } })
                    dic4 = {'$and':[dic,{'$nor': list4}]}

                doc1= client.adf_main.adf_frontend.find({'$and':[dic1,dic2,dic3]} )
                doc2= client.adf_main.adf_frontend.find({'$and':[dic1,dic2,dic4]} )
                
                if len(or_list):
                    docs.append(doc1)
                    docs.append(doc2)
                else:
                    docs.append(doc1)
                
            return render(request, 'search/others_search.html', {'docs':docs})

        elif request.POST["doc_type"] == 'Email':
            df = client.adf_main.adf_frontend
            docs=[]
            in_start_date = request.POST["Start_Date"]
            in_end_date = request.POST["End_Date"]
            #print(in_date,type(in_date))
            if(in_start_date):
                in_start_date = datetime.datetime.strptime(in_start_date, '%Y-%m-%d')
            else:
                in_start_date = datetime.datetime(1500, 5, 17)
            #print(in_date,type(in_date))
            if(in_end_date):
                in_end_date = datetime.datetime.strptime(in_end_date, '%Y-%m-%d')
            else:
                in_end_date = datetime.datetime.now()

            
            to_string = request.POST["To"]   # psenwar@gmail.com+satyamprakashiitk2022@gmail.com
            #print(to_string)
            #or_lst = to_str.split('+')
            and_to_list = []
            not_to_list = []
            or_to_list = []
            temp = '*'
            current = ""
            for i in to_string:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_to_list.append(current)
                    elif(temp=='-'):
                        not_to_list.append(current)
                    elif(temp=='|'):
                        or_to_list.append(current)

                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_to_list.append(current)
            elif(temp=='-'):
                not_to_list.append(current)
            elif(temp=='|'):
                or_to_list.append(current)

            dic={}
            dic['doc_type'] = 'Email'
            main_dic = []
            list1=[]
            dic1=dic
            if len(and_to_list):
                for word in and_to_list:
                    list1.append({'To': { '$regex': word, '$options': 'i' } })
                dic1 = {'$and':[dic,{ '$and': list1}]}
            main_dic.append(dic1)
            list2=[]
            dic2=dic
            if len(not_to_list):
                for word in not_to_list:
                    list2.append({'To': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)
            
            dic_date = {'$and':[{'date':{'$gt':in_start_date}},{'date':{'$lt':in_end_date}}]}
            main_dic.append(dic_date)

#  ******* -------  FROM: -----*******
            from_string = request.POST["From"]   # psenwar@gmail.com+satyamprakashiitk2022@gmail.com
            #print(from_string)
            #or_lst = to_str.split('+')
            and_from_list = []
            not_from_list = []
            or_from_list = []
            temp = '*'
            current = ""
            for i in from_string:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_from_list.append(current)
                    elif(temp=='-'):
                        not_from_list.append(current)
                    elif(temp=='|'):
                        or_from_list.append(current)
                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_from_list.append(current)
            elif(temp=='-'):
                not_from_list.append(current)
            elif(temp=='|'):
                or_from_list.append(current)


            list1=[]
            dic1=dic
            if len(and_from_list):
                for word in and_from_list:
                    list1.append({'From': { '$regex': word, '$options': 'i' } })
                #print(list1)
                dic1 = {'$and':[dic,{ '$and': list1}]}
                #print(dic1)
            main_dic.append(dic1)

            list2=[]
            dic2=dic
            if len(not_from_list):
                for word in not_from_list:
                    list2.append({'From': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)

          # ***** -----  BODY search ----- *******
            body_string = request.POST["Body"]   # psenwar@gmail.com+satyamprakashiitk2022@gmail.com
            #print(body_string)
            #or_lst = to_str.split('+')
            and_from_list = []
            not_from_list = []
            or_from_list = []
            temp = '*'
            current = ""
            for i in body_string:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_from_list.append(current)
                    elif(temp=='-'):
                        not_from_list.append(current)
                    elif(temp=='|'):
                        or_from_list.append(current)
                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_from_list.append(current)
            elif(temp=='-'):
                not_from_list.append(current)
            elif(temp=='|'):
                or_from_list.append(current)


            list1=[]
            dic1=dic
            if len(and_from_list):
                for word in and_from_list:
                    list1.append({'Body': { '$regex': word, '$options': 'i' } })
                dic1 = {'$and':[dic,{ '$and': list1}]}
            main_dic.append(dic1)

            list2=[]
            dic2=dic
            if len(not_from_list):
                for word in not_from_list:
                    list2.append({'Body': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)

            #****** ---- Subject ----*****
            sub_string = request.POST["Subject"]   # psenwar@gmail.com+satyamprakashiitk2022@gmail.com
            #print(sub_string)
            #or_lst = to_str.split('+')
            and_from_list = []
            not_from_list = []
            or_from_list = []
            temp = '*'
            current = ""
            for i in sub_string:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_from_list.append(current)
                    elif(temp=='-'):
                        not_from_list.append(current)
                    elif(temp=='|'):
                        or_from_list.append(current)
                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_from_list.append(current)
            elif(temp=='-'):
                not_from_list.append(current)
            elif(temp=='|'):
                or_from_list.append(current)


            list1=[]
            dic1=dic
            if len(and_from_list):
                for word in and_from_list:
                    list1.append({'Subject': { '$regex': word, '$options': 'i' } })
                dic1 = {'$and':[dic,{ '$and': list1}]}
            main_dic.append(dic1)

            list2=[]
            dic2=dic
            if len(not_from_list):
                for word in not_from_list:
                    list2.append({'Subject': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)
            # ******** - mongoDB queries ****** ---- 
            
            doc1= df.find({'$and':main_dic} )
            docs = doc1
            #print("docs", docs)
            
            #docs = db.find({'doc_type':'Email'})   
            return render(request , 'search/email_search.html', {'docs':docs})

        elif request.POST["doc_type"] == 'Invoice':
            df = client.adf_main.adf_frontend
            docs=[]
            in_start_date = request.POST['date1']
            in_end_date = request.POST['date2']
            if(in_start_date):
                in_start_date = datetime.datetime.strptime(in_start_date, '%Y-%m-%d')
            else:
                in_start_date = datetime.datetime(1500, 5, 17)
            #print(in_date,type(in_date))
            if(in_end_date):
                in_end_date = datetime.datetime.strptime(in_end_date, '%Y-%m-%d')
            else:
                in_end_date = datetime.datetime.now()
            dic={}
            dic['doc_type'] = 'Invoice'
            main_dic = []
            dic_date = {'$and':[{'date':{'$gt':in_start_date}},{'date':{'$lt':in_end_date}}]}
            main_dic.append(dic_date)
            company = request.POST['com']
            and_to_list = []
            not_to_list = []
            or_to_list = []
            temp = '*'
            current = ""
            for i in company:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_to_list.append(current)
                    elif(temp=='-'):
                        not_to_list.append(current)
                    elif(temp=='|'):
                        or_to_list.append(current)

                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_to_list.append(current)
            elif(temp=='-'):
                not_to_list.append(current)
            elif(temp=='|'):
                or_to_list.append(current)
            list1 = []
            dic1 = dic
            if len(and_to_list):
                for word in and_to_list:
                    list1.append({'issuer': { '$regex': word, '$options': 'i' } })
                dic1 = {'$and':[dic,{ '$and': list1}]}
            main_dic.append(dic1)
            list2=[]
            dic2=dic
            if len(not_to_list):
                for word in not_to_list:
                    list2.append({'issuer': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)
            amount = request.POST['amount']
            if(amount):
                tmp = amount.split('-')
                low = int(tmp[0])
                high = int(tmp[1])
                dic_amt = {'$and':[{'amount':{'$gt':low,'$lt':high}}]}
                main_dic.append(dic_amt)
            full = request.POST['full']
            and_to_list = []
            not_to_list = []
            or_to_list = []
            temp = '*'
            current = ""
            for i in full:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_to_list.append(current)
                    elif(temp=='-'):
                        not_to_list.append(current)
                    elif(temp=='|'):
                        or_to_list.append(current)

                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_to_list.append(current)
            elif(temp=='-'):
                not_to_list.append(current)
            elif(temp=='|'):
                or_to_list.append(current)
            list1 = []
            dic1 = dic
            if len(and_to_list):
                for word in and_to_list:
                    list1.append({'content': { '$regex': word, '$options': 'i' } })
                dic1 = {'$and':[dic,{ '$and': list1}]}
            main_dic.append(dic1)
            list2=[]
            dic2=dic
            if len(not_to_list):
                for word in not_to_list:
                    list2.append({'content': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)
            doc1 = df.find({'$and':main_dic})
            docs = doc1
            return render(request, 'search/invoice_search.html', {'docs': docs})
        
        elif request.POST["doc_type"] == 'All':
            df = client.adf_main.adf_frontend
            to_string = request.POST["content_text"]   
            print(to_string)
            and_to_list = []
            not_to_list = []
            or_to_list = []
            temp = '*'
            current = ""
            for i in to_string:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_to_list.append(current)
                    elif(temp=='-'):
                        not_to_list.append(current)
                    elif(temp=='|'):
                        or_to_list.append(current)

                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_to_list.append(current)
            elif(temp=='-'):
                not_to_list.append(current)
            elif(temp=='|'):
                or_to_list.append(current)

            dic={}
            #dic['doc_type'] = 'Email'
            dic = { "doc_type": { "$in": ["Email","Others","Invoice"] } }
            main_dic = []
            list1=[]
            dic1=dic
            dic1 = {}
            if len(and_to_list):
                for word in and_to_list:
                    list1.append({'content_text': { '$regex': word, '$options': 'i' } })
                dic1 = {'$and':[dic,{ '$and': list1}]}
            main_dic.append(dic1)
            list2=[]
            dic2=dic
            dic2 = {}
            if len(not_to_list):
                for word in not_to_list:
                    list2.append({'content_text': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)

            #---** ---- searching in file_name ---**  

            to_string = request.POST["file_name"]   
            and_to_list = []
            not_to_list = []
            or_to_list = []
            temp = '*'
            current = ""
            for i in to_string:
                if(i=='+' or i=='-' or i=='|'):
                    if(temp=='+'):
                        and_to_list.append(current)
                    elif(temp=='-'):
                        not_to_list.append(current)
                    elif(temp=='|'):
                        or_to_list.append(current)

                    temp = i
                    current= ""
                else:
                    current+=i

            if(temp=='+'):
                and_to_list.append(current)
            elif(temp=='-'):
                not_to_list.append(current)
            elif(temp=='|'):
                or_to_list.append(current)

            list1=[]
            dic1=dic
            if len(and_to_list):
                for word in and_to_list:
                    list1.append({'file_name': { '$regex': word, '$options': 'i' } })
                dic1 = {'$and':[dic,{ '$and': list1}]}
            main_dic.append(dic1)
            list2=[]
            dic2=dic
            if len(not_to_list):
                for word in not_to_list:
                    list2.append({'file_name': { '$regex': word, '$options': 'i' } })
                dic2 = {'$and':[dic,{'$nor': list2}]}
            main_dic.append(dic2)

            doc1= df.find({'$and':main_dic} )
            docs = doc1
            return render(request , 'search/all_search.html', {'docs':docs})
            

    else:
        dic={}
        try:
            dic['type']=request.GET['type']
            
        except:
            pass
        # print(dic)
        return render(request, 'search/search.html',dic)