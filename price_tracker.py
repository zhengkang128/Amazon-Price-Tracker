import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import smtplib
from datetime import datetime
import mysql.connector

def scrap(URL, target, email):
    connection = mysql.connector.connect(host='localhost',
                                        database='price_trackerdb',
                                        user='root',
                                        password='30082010')
    mycursor = connection.cursor()



    #Selenium to render JS and obtain content
    driver = webdriver.Chrome("chromedriver.exe")
    driver.get(URL) 
    content = driver.page_source.encode('utf-8').strip()
    driver.quit()

    #Scrape content
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.find(id="productTitle").get_text().strip().replace('”',' inch').replace('"',' inch')
    price = soup.find(id="priceblock_ourprice").get_text()
    shipping_price = soup.find(class_="a-size-base a-color-secondary").get_text()
    
    #float conversion
    converted_price = ""
    converted_shipping = ""
    for i in price:
        if (i.isdigit() or i=="."):
            converted_price = converted_price + i
    for i in shipping_price:
        if (i.isdigit() or i=="."):
            converted_shipping = converted_shipping + i
            
    converted_price = float(converted_price)
    converted_shipping = float(converted_shipping)
    total_price = converted_price + converted_shipping

    #To Check Successful Scrape
    print(title)
    print(converted_price)
    print(converted_shipping)
    print(total_price)

    #Send mail
    if (converted_price+converted_shipping <target):
        send_mail(title, converted_price, converted_shipping, email)
        
    #mycursor.execute("SELECT * FROM price_information WHERE product_name = " + str(title) + " ORDER BY id DESC LIMIT 1;")
    mycursor.execute("SELECT * FROM price_information WHERE product_name = " + "\"" +  str(title) + "\"" + " ORDER BY id DESC LIMIT 1;")  
    myresult = mycursor.fetchall()

    if (len(myresult)==0 or myresult[0][3]!=total_price): #no results
        query = "INSERT INTO price_information (product_name, date_retrieved, total_price, product_price, shipping_price) VALUES (%s, %s, %s, %s, %s);"
        now = datetime.now()
        d1 = now.strftime('%Y-%m-%d %H:%M:%S')
        arg = (title, d1, total_price, converted_price, converted_shipping)
        mycursor.execute(query,arg)
        connection.commit()
        print("Updated Database")
    else:
        print("no updates")

def send_mail(title, price, shipping, email):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('webscrapper101@gmail.com', "300810d0t.+")


    total = price + shipping
    subject = 'Price fell down below target'
    body1 = 'Product: $' + title
    body2 = 'Total Price: $' + str(total)
    body3 = 'Product Price: $' + str(price)
    body4 = 'Shipping Price: $' + str(shipping)
    body5 = 'https://www.amazon.com/gp/product/B07N6S4SY1/r'


    
    msg = f"Subject: {subject}\n\n{body1}\n\n{body2}\n{body3}\n{body4}\n\n{body5}"

    server.sendmail(
        'webscrapper101@gmail.com',
        email,
        msg
        )
    print("Mail sent")
    server.quit()

email = input("Please enter your email address: ")
numLinks = int(input("Enter number of websites for scraping (max 10): "))

#email = "chuazhengkang123@gmail.com" #default
#numLinks = 2 #default
#URL_list = ["https://www.amazon.com/gp/product/B07N6S4SY1/r", "https://www.amazon.com/gp/product/B086KKKT15/"]
#price_target = [10000, 100000] #default

for i in range(numLinks):
    URL_list.append(input("Enter URL Link for website #" + str(i+1)+ ": "))
    price_target.append(float(input("Enter price target for this product: ")))
    
print("Notification will be sent to " + email)
print("Scraping price information from: ")
for i in range(numLinks):
    print(URL_list[i])
    print("Target: " + str(price_target[i]))

start = int(round(time.time()))

    #Execute one time
for i in range(numLinks):
    scrap(URL_list[i],price_target[i], email)
    start = int(round(time.time()))
    
while (True):
        
    if (int(round(time.time())) - start >= (60*60*2)):
        for i in range(numLinks):
            scrap(URL_list[i],price_target[i], email)
        start = int(round(time.time()))
        
    

