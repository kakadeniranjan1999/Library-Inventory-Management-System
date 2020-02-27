# -*- coding: utf-8 -*-
import pymongo
import datetime
import re
from dateutil.relativedelta import relativedelta
import smtplib
myclient=pymongo.MongoClient("")
my_data_base=myclient['MESA_Library']

def change_availibility_status(change_availibilty):
    b=0
    database_object=my_data_base['Available Books Record']
    count=(database_object.find(change_availibilty))
    for p in count:
        b=b+1
    if(b>0):
#        a=database_object.find_one(change_availibilty)
        a=database_object.find_one_and_update(change_availibilty,{"$set":{'Availability Status':'Unavailable'}})
        return a['Book id']
    else:
        return 0

def send_issue_mail(email,name,book_name,author_name,date,deadline):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("MAIL_ID", "PASSWORD")
    message ='''Subject: BOOK ISSUED:MESA Library \n
Regards '''+name+''',
        
This mail is to inform you that you have issued a book from MESA Library whose details are as follows: 

Book Details:-

Book Name: '''+book_name+'''
        
Author Name: '''+author_name+'''

Donate Date: '''+str(date)+''' (YYYY/MM/DD).

Deadline: '''+ str(deadline) +''' (YYYY/MM/DD).

Kindly remember the deadline, after which fine may be charged (Rs.2 per day for 10 days and Rs.10 per day beyond.)
    
In case of any issues contact MESA Library.
        
Thank you for being a part of the library.

This is a system generated mail.Kindly do not reply.
    
Team MESA Library.'''
    s.sendmail("mesalibrary19@gmail.com",email,message)
    print('Mail sent to '+name)
    s.quit()
    print(end='\n')

def send_donate_mail(email,name,book_name,author_name,date):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("MAIL_ID", "PASSWORD")
    message ='''Subject: GRATITUDE:MESA Library Donation \n
Regards '''+name+''',
        
MESA Library is grateful to your contribution towards the library.

This mail is to thank you for donating a book to MESA Library which will surely benefit the enthusiasts. 

Book Details:-

Book Name: '''+book_name+'''
        
Author Name: '''+author_name+'''

Donate Date: '''+str(date)+''' (YYYY/MM/DD).
        
In case of any issues contact MESA Library.
        
Thank you for being a part of the library.

This is a system generated mail.Kindly do not reply.
    
Team MESA Library.'''
    s.sendmail("mesalibrary19@gmail.com",email,message)
    print('Mail sent to '+name)
    s.quit()
    print(end='\n')

def new_book_entry():
    database_object=my_data_base['Available Books Record']
    n=int(input('Enter the number of new book entries:-'))
    for l in range(0,n):
        count=database_object.count_documents({})
        book_id='MESA'+str(count+1)
        book=input('Enter book name:')
        author=input('Enter author name:')
        category=input('Enter book category:')
        doner=input('Enter doner name:')
        doner_mail=input('Enter doner Email:')
        date=str(datetime.datetime.now().date())
        time=str(datetime.datetime.now().time())
        avail='Available'
        add_new_book={'Book id':book_id,'Book Name':book,'Doner Name':doner,'Doner Email':doner_mail,'Author Name':author,'Book Category':category,'Date (YYYY/MM/DD)':date,'Time (HH:MM:SS)':time,'Availability Status':avail}
        database_object.insert_one(add_new_book)
        print('New Book Entry Added')
        print(end='\n')
        send_donate_mail(doner_mail,doner,book,author,date)

def issue_book():
    database_object=my_data_base['Book Given']
    n=int(input('Enter the number of book issue entries:-'))
    for m in range(0,n):
        book=input('Enter book name:')
        author=input('Enter author name:')
        category=input('Enter book category:')
        c=change_availibility_status({'Book Name':re.compile(book, re.IGNORECASE),'Author Name':re.compile(author, re.IGNORECASE),'Book Category':re.compile(category, re.IGNORECASE),'Availability Status':'Available'})
        if c!=0:
            issuer=input("Enter issuer's name:")
            issuer_mail=input('Enter doner Email:')
            date=str(datetime.datetime.now().date())
            time=str(datetime.datetime.now().time())
            fine=0
            pay='Paid'
            return_status='Not Returned'
            deadline=str(datetime.datetime.now().date()+ relativedelta(days=30))
            add_new_book={'Book id':c,'Book Name':book,'Issuer Name':issuer,'Issuer Email':issuer_mail,'Author Name':author,'Book Category':category,'Date (YYYY/MM/DD)':date,'Time (HH:MM:SS)':time,'Deadline (YYYY/MM/DD)':deadline,'Fine':fine,'Pay Status':pay,'Return Status':return_status}
            database_object.insert_one(add_new_book)
            print('Issue Book Entry Added')
            print(end='\n')
            send_issue_mail(issuer_mail,issuer,book,author,date,deadline)
        else:
            print('No book available.')
            print(end='\n')

def check_fine():
    database_object=my_data_base['Book Given']
    return_status='Not Returned'
    print(end='\n')
    query={'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for s in searched:
        deadline=datetime.datetime.fromtimestamp(datetime.datetime.fromisoformat(s['Deadline (YYYY/MM/DD)']).timestamp()).date()
        today=datetime.datetime.now().date()
        day=(today-deadline).days
        if(day>0 and day<=15):
            amount=day*2
            database_object.find_one_and_update({'_id':s['_id']},{"$set":{'Pay Status':'Pending','Fine':amount}})
        elif(day>0 and day>15):
            amount=((day-15)*10)+30
            database_object.find_one_and_update({'_id':s['_id']},{"$set":{'Pay Status':'Pending','Fine':amount}})
        else:
            continue

def return_book():
    database_object=my_data_base['Book Given']
    database_object1=my_data_base['Available Books Record']
    check_fine()
    book_id=input('Enter book id:-')
    fine_check=database_object.find_one({'Book id':re.compile(book_id, re.IGNORECASE)})
    if(fine_check['Fine']>0):
        deadline=datetime.datetime.fromtimestamp(datetime.datetime.fromisoformat(fine_check['Deadline (YYYY/MM/DD)']).timestamp()).date()
        today=datetime.datetime.now().date()
        day=(today-deadline).days
        print('You are charged with a fine of '+str(fine_check['Fine'])+' for '+str(day))
        print('Has the issuer paid the fine?')
        status=input('Enter Yes or No:-')
        status=status.lower()
        if(status=='yes'):
            database_object.find_one_and_update(fine_check,{"$set":{'Pay Status':'Paid','Fine':0,'Return Status':'Returned'}})
            database_object1.find_one_and_update({'Book id':re.compile(book_id, re.IGNORECASE)},{"$set":{'Availability Status':'Available'}})
            print('Thank you!!!!')
            print(end='\n')
        else:
            print('Please pay fine!!!!!!!!!')
            print(end='\n')    
    
def send_fine_mail():
    check_fine()
    database_object_new=my_data_base['Book Given']
    query={'Pay Status': re.compile('Pending', re.IGNORECASE)}
    searched=database_object_new.find(query)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("mesalibrary19@gmail.com", "Library@2019")
    for x in searched:
        message ='''Subject: WARNING:MESA Library Fine \n
Regards '''+x['Issuer Name']+''',
        
This mail is to inform you that you have issued a book from MESA Library for which the deadline was 
'''+str(x['Deadline (YYYY/MM/DD)'])+''' (YYYY/MM/DD).
    
The deadline has been crossed and a fine of Rs.'''+str(x['Fine'])+''' has been charged to your account.

Book Details:-

Book Name: '''+str(x['Book Name'])+'''
        
Author Name: '''+str(x['Author Name'])+'''

Issue Date: '''+str(x['Date (YYYY/MM/DD)'])+''' (YYYY/MM/DD).
        
Kindly pay the fine and reissue the book or return it.
In case of any issues contact MESA Library.
        
This is a system generated mail.Kindly do not reply.
        
Thank You.
    
Team MESA Library.'''
        s.sendmail("mesalibrary19@gmail.com",x['Issuer Email'],message)
        print('Mail sent to '+str(x['Issuer Name']))
    s.quit()
    print(end='\n')


def book_availibility():
    a=0
    database_object_new=my_data_base['Available Books Record']
    check_name=input('Enter the name of the book:-')
    print(end='\n')
    query={'Book Name': re.compile(check_name, re.IGNORECASE),'Availability Status':'Available'}
    searched=database_object_new.find(query)
    for o in searched:
        print('Book Name:-'+o['Book Name'])
        print('Author Name:-'+o['Author Name'])
        print('Book Category:-'+o['Book Category'])
        print('Availability Status:-'+o['Availability Status'])
        print('-------------------------------------------------')
        a=a+1
    print('Total '+check_name+' books available:-',a)
    print(end='\n')

def search_by_issuer_name():
    database_object=my_data_base['Book Given']
    issuer_name=input('Enter the name of the issuer:-')
    pay_status=input('Enter pay status (Paid or Pending):-')
    return_status=input('Enter return status (Returned or Not Returned):-')
    print(end='\n')
    query={'Issuer Name': re.compile(issuer_name, re.IGNORECASE),'Pay Status':re.compile(pay_status, re.IGNORECASE),'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for i in searched:
        print('Book id:-'+i['Book id'])
        print('Issuer Name:-'+i['Issuer Name'])
        print('Book Name:-'+i['Book Name'])
        print('Author Name:-'+i['Author Name'])
        print('Book Category:-'+i['Book Category'])
        print('Issue Date (YYYY/MM/DD):-'+i['Date (YYYY/MM/DD)'])
        print('Issue Time (HH:MM:SS):-'+i['Time (HH:MM:SS)'])
        print('Fine:-'+str(i['Fine']))
        print('Pay Status:-'+i['Pay Status'])
        print('-------------------------------------------------')
        

def search_by_book_name():
    database_object=my_data_base['Book Given']
    book_name=input('Enter the name of the book:-')
    pay_status=input('Enter pay status (Paid or Pending):-')
    return_status=input('Enter return status (Returned or Not Returned):-')
    print(end='\n')
    query={'Book Name':re.compile(book_name, re.IGNORECASE),'Pay Status':re.compile(pay_status, re.IGNORECASE),'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for j in searched:
        print('Book id:-'+j['Book id'])
        print('Issuer Name:-'+j['Issuer Name'])
        print('Book Name:-'+j['Book Name'])
        print('Author Name:-'+j['Author Name'])
        print('Book Category:-'+j['Book Category'])
        print('Issue Date (YYYY/MM/DD):-'+j['Date (YYYY/MM/DD)'])
        print('Issue Time (HH:MM:SS):-'+j['Time (HH:MM:SS)'])
        print('Deadline Date (YYYY/MM/DD):-'+j['Deadline (YYYY/MM/DD)'])
        print('Fine:-'+str(j['Fine']))
        print('Pay Status:-'+j['Pay Status'])
        print('-------------------------------------------------')
    
def search_by_date():
    database_object=my_data_base['Book Given']
    issue_date=input('Enter the date of issue:-')
    pay_status=input('Enter pay status (Paid or Pending):-')
    return_status=input('Enter return status (Returned or Not Returned):-')
    print(end='\n')
    query={'Date (YYYY/MM/DD)':issue_date,'Pay Status':re.compile(pay_status, re.IGNORECASE),'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for k in searched:
        print('Book id:-'+k['Book id'])
        print('Issuer Name:-'+k['Issuer Name'])
        print('Book Name:-'+k['Book Name'])
        print('Author Name:-'+k['Author Name'])
        print('Book Category:-'+k['Book Category'])
        print('Issue Date (YYYY/MM/DD):-'+k['Date (YYYY/MM/DD)'])
        print('Issue Time (HH:MM:SS):-'+k['Time (HH:MM:SS)'])
        print('Deadline Date (YYYY/MM/DD):-'+k['Deadline (YYYY/MM/DD)'])
        print('Fine:-'+str(k['Fine']))
        print('Pay Status:-'+k['Pay Status'])
        print('-------------------------------------------------')

def search_by_deadline():
    database_object=my_data_base['Book Given']
    deadline_date=input('Enter the deadline date:-')
    pay_status=input('Enter pay status (Paid or Pending):-')
    return_status=input('Enter return status (Returned or Not Returned):-')
    print(end='\n')
    query={'Deadline (YYYY/MM/DD)':deadline_date,'Pay Status':re.compile(pay_status, re.IGNORECASE),'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for q in searched:
        print('Book id:-'+q['Book id'])
        print('Issuer Name:-'+q['Issuer Name'])
        print('Book Name:-'+q['Book Name'])
        print('Issue Date (YYYY/MM/DD):-'+q['Date (YYYY/MM/DD)'])
        print('Issue Time (HH:MM:SS):-'+q['Time (HH:MM:SS)'])
        print('Deadline Date (YYYY/MM/DD):-'+q['Deadline (YYYY/MM/DD)'])
        print('-------------------------------------------------')

def search_by_book_author():
    database_object=my_data_base['Book Given']
    author_name=input('Enter the name of the author:-')
    pay_status=input('Enter pay status (Paid or Pending):-')
    return_status=input('Enter return status (Returned or Not Returned):-')
    print(end='\n')
    query={'Author Name':re.compile(author_name, re.IGNORECASE),'Pay Status':re.compile(pay_status, re.IGNORECASE),'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for r in searched:
        print('Book id:-'+r['Book id'])
        print('Issuer Name:-'+r['Issuer Name'])
        print('Book Name:-'+r['Book Name'])
        print('Issue Date (YYYY/MM/DD):-'+r['Date (YYYY/MM/DD)'])
        print('Issue Time (HH:MM:SS):-'+r['Time (HH:MM:SS)'])
        print('Deadline Date (YYYY/MM/DD):-'+r['Deadline (YYYY/MM/DD)'])
        print('-------------------------------------------------')

def search_by_book_category():
    database_object=my_data_base['Book Given']
    book_category=input('Enter the name of the book category:-')
    pay_status=input('Enter pay status (Paid or Pending):-')
    return_status=input('Enter return status (Returned or Not Returned):-')
    print(end='\n')
    query={'Book Category':re.compile(book_category, re.IGNORECASE),'Pay Status':re.compile(pay_status, re.IGNORECASE),'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for s in searched:
        print('Book id:-'+s['Book id'])
        print('Issuer Name:-'+s['Issuer Name'])
        print('Book Name:-'+s['Book Name'])
        print('Issue Date (YYYY/MM/DD):-'+s['Date (YYYY/MM/DD)'])
        print('Issue Time (HH:MM:SS):-'+s['Time (HH:MM:SS)'])
        print('Deadline Date (YYYY/MM/DD):-'+s['Deadline (YYYY/MM/DD)'])
        print('-------------------------------------------------')

def search_by_book_id():
    database_object=my_data_base['Book Given']
    book_id=input('Enter the book id:-')
    pay_status=input('Enter pay status (Paid or Pending):-')
    return_status=input('Enter return status (Returned or Not Returned):-')
    print(end='\n')
    query={'Book id':re.compile(book_id, re.IGNORECASE),'Pay Status':re.compile(pay_status, re.IGNORECASE),'Return Status':re.compile(return_status, re.IGNORECASE)}
    searched=database_object.find(query)
    for v in searched:
        print('Book id:-'+v['Book id'])
        print('Issuer Name:-'+v['Issuer Name'])
        print('Book Name:-'+v['Book Name'])
        print('Issue Date (YYYY/MM/DD):-'+v['Date (YYYY/MM/DD)'])
        print('Issue Time (HH:MM:SS):-'+v['Time (HH:MM:SS)'])
        print('Deadline Date (YYYY/MM/DD):-'+v['Deadline (YYYY/MM/DD)'])
        print('-------------------------------------------------')

def search_entry():
    print('Select the field of search:-')
    print('1.Issuer Name')
    print('2.Book Name')
    print('3.Author Name')
    print('4.Book Category')
    print('5.Issue Date')
    print('6.Deadline')
    print('7.Book id')
    print('0.Exit Search Entry')
    operation=int(input('Operation Number:-'))
    if(operation==1):
        search_by_issuer_name()
    elif(operation==2):
        search_by_book_name()
    elif(operation==3):
        search_by_book_author()
    elif(operation==4):
        search_by_book_category()
    elif(operation==5):
        search_by_date()
    elif(operation==6):
        search_by_deadline()
    elif(operation==7):
        search_by_book_id()
    elif(operation==0):
        print('You have sucessfully logged out of search entry!!!!')
    else:
        print('Please enter valid number!!!!!')
        search_entry()

def start():
    print('Enter the number of the operation you want to perform:-')
    print('1.New Book Entry')
    print('2.Issue Book Entry')
    print('3.Search Entry')
    print('4.Book Availibility')
    print('5.Check Fine')
    print('6.Return Book')
    print('7.Send Fine Mail')
    print('0.Exit Software')
    operation=int(input('Operation Number:-'))
    print(end='\n')
    if(operation==1):
        new_book_entry()
        start()
    elif(operation==2):
        issue_book()
        start()
    elif(operation==3):
        search_entry()
        start()
    elif(operation==4):
        book_availibility()
        start()
    elif(operation==5):
        check_fine()
        start()
    elif(operation==6):
        return_book()
        start()
    elif(operation==7):
        send_fine_mail()
        start()
    elif(operation==0):
        print('You have successfully logged out of software.Thank You!!!!')
    else:
        print('Please enter valid number!!!!!')
        print(end='\n')
        start()


start()
