import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import smtplib
from datetime import datetime
import mysql.connector
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
from statistics import mean 



def scrap(URL, target, email):
    connection = mysql.connector.connect(host='localhost',
                                        database='tracker_db',
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
    price = soup.find(id="price_inside_buybox")
    if price is None:
        price = soup.find(id="newBuyBoxPrice")
        if price is None:
            price = soup.find(id="priceblock_dealprice")
            if price is None:
                price = "0"
            else:
                price=price.get_text()
        else:
            price=price.get_text()
    else:
        price=price.get_text()
    
    
    
    shipping_price = soup.find(class_="a-size-base a-color-secondary")
    if shipping_price is None:
        shipping_price = "0"
    else:
        shipping_price = shipping_price.get_text()    
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
    if (converted_shipping == ""):
        converted_shipping = 0
    converted_shipping = float(converted_shipping)
    total_price = converted_price + converted_shipping

    #To Check Successful Scrape
    print(title)
    print(converted_price)
    print(converted_shipping)
    print(total_price)

    #Send mail
    if (converted_price+converted_shipping <target):
        send_mail(title, converted_price, converted_shipping, email, URL)
        
    #mycursor.execute("SELECT * FROM price_information WHERE product_name = " + str(title) + " ORDER BY id DESC LIMIT 1;")
    mycursor.execute("SELECT * FROM price_information WHERE product_name = " + "\"" +  str(title) + "\"" + " ORDER BY id DESC LIMIT 1;")  
    myresult = mycursor.fetchall()

  
    query = "INSERT INTO price_information (product_name, date_retrieved, total_price, product_price, shipping_price) VALUES (%s, %s, %s, %s, %s);"
    now = datetime.now()
    d1 = now.strftime('%Y-%m-%d %H:%M:%S')
    arg = (title, d1, total_price, converted_price, converted_shipping)
    mycursor.execute(query,arg)
    connection.commit()
    print("Updated Database")
        
    if (len(myresult)!=0):
        if (abs(myresult[0][3]-total_price)>=0.01):
            send_mail_drop_price(title, converted_price, converted_shipping, email,URL)
            print("Change in price")
        else:
            print("No change in price")
    else:
        print("New item")

    query = "SELECT id FROM products WHERE product_name = " + "\"" +  str(title) + "\""
    mycursor.execute(query)
    result2 = mycursor.fetchall()

    if len(result2)==0:
        query = "INSERT INTO products (product_name, comments) VALUES (%s, %s);"
        arg = (title, URL)  
        mycursor.execute(query,arg)
        connection.commit()
        print("Updated Products Table")

    #Product graph
    query = "SELECT * FROM price_information pi JOIN products p ON p.product_name = pi.product_name WHERE pi.product_name = " + "\"" + title + "\" ORDER BY pi.date_retrieved"
    mycursor.execute(query)
    myresult = mycursor.fetchall()

    product_id = myresult[0][6]
    product_name = myresult[0][1]
    total_price = []
    product_price = []
    shipping_price = []
    date = []

    for rows in myresult:
        total_price.append(rows[3])
        product_price.append(rows[4])
        shipping_price.append(rows[5])
        date.append(rows[2])
    fig, ax = plt.subplots(figsize=(20, 15))

    mean_total = round(mean(total_price),2)
    mean_product = round(mean(product_price),2)
    mean_shipping = round(mean(shipping_price),2)

    ax.plot(date,
            total_price,
            color='purple', label = "Total Price (mean = $" + str(mean_total) + ")")

    ax.plot(date,
            product_price,
            color='blue', label = "Product Price (mean = $" + str(mean_product) + ")")

    ax.plot(date,
            shipping_price,
            color='red', label = "Shipping Price (mean = $" + str(mean_shipping) + ")")

    ax.set(xlabel="Date and Time",
           ylabel="Price (SGD)",
           title="Changes of Pricing for \n" + product_name + "\n")
    ax.legend()

    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    fig.autofmt_xdate()

    plt.savefig("results/product_num" + str(product_id) +'.png')





#Reached target
def send_mail(title, price, shipping, email, URL):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('webscrapper101@gmail.com', "300810d0t.+")


    total = price + shipping
    subject = 'Price fell down below target!'
    body1 = 'Product: $' + title
    body2 = 'Total Price: $' + str(total)
    body3 = 'Product Price: $' + str(price)
    body4 = 'Shipping Price: $' + str(shipping)
    body5 = URL


    
    msg = f"Subject: {subject}\n\n{body1}\n\n{body2}\n{body3}\n{body4}\n\n{body5}"

    server.sendmail(
        'webscrapper101@gmail.com',
        email,
        msg
        )
    print("Mail sent")
    server.quit()

def send_mail_drop_price(title, price, shipping, email, URL):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('webscrapper101@gmail.com', "300810d0t.+")


    total = price + shipping
    subject = 'There is a change in the price.'
    body1 = 'Product: $' + title
    body2 = 'Total Price: $' + str(total)
    body3 = 'Product Price: $' + str(price)
    body4 = 'Shipping Price: $' + str(shipping)
    body5 = URL


    
    msg = f"Subject: {subject}\n\n{body1}\n\n{body2}\n{body3}\n{body4}\n\n{body5}"

    server.sendmail(
        'webscrapper101@gmail.com',
        email,
        msg
        )
    print("Mail sent")
    server.quit()


    

# Using readlines() 
inputs = open('input.txt', 'r') 
Lines = inputs.readlines() 
URL_list = []
price_target = []

count = 0
# Strips the newline character 
for line in Lines:
    if count==0:
        email = line
    elif (count%2)==1:
        URL_list.append(line.rstrip("\n"))
    else:
        price_target.append(float(line))
    count = count + 1

numLinks = count//2
        
    
print("Notification will be sent to " + email)
print("Scraping price information from: ")
for i in range(numLinks):
    print(URL_list[i])
    print("Target: $" + str(price_target[i]))
print("")

start = int(round(time.time()))

    #Execute one time
for i in range(numLinks):
    scrap(URL_list[i],price_target[i], email)
    start = int(round(time.time()))
    
while (True):
        
    if (int(round(time.time())) - start >= (60*60)):
        for i in range(numLinks):
            scrap(URL_list[i],price_target[i], email)
        start = int(round(time.time()))
        
    

