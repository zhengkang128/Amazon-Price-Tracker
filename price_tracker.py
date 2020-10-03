import requests
from bs4 import BeautifulSoup
import time
import smtplib
from datetime import datetime
import mysql.connector
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
from statistics import mean 
import numpy as np

interval = 60 * 60 * 1 #seconds x minutes x hours. Change this value to adjust your interval to web scrape

def scrap(URL, target, email):
    connection = mysql.connector.connect(host='localhost',
                                        database='tracker_db',
                                        user='root', #change user
                                        password='30082010') #input your password here
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
    mycursor = connection.cursor()
    content = requests.get(URL, headers=headers).text


    #Scrape content
    soup = BeautifulSoup(content, 'lxml')
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
    if ("Shipping" not in shipping_price) and ("Import" not in shipping_price):
        shipping_price = "0"
    #float conversion
    converted_price = ""
    converted_shipping = ""
    for i in price:
        if (i.isdigit() or i=="."):
            converted_price = converted_price + i
    
    for i in shipping_price:
        if (i.isdigit() or i=="."):
            converted_shipping = converted_shipping + i            
            
    converted_price = round(float(converted_price),2)
    converted_shipping = round(float(converted_shipping),2)
    total_price = round(converted_price + converted_shipping,2)

    #To Check Successful Scrape
    print(title)
    print("Product Price: " + str(converted_price))
    print("Shipping Price: " + str(converted_shipping))
    print("Total Price: " + str(total_price))
    now = datetime.now()
    d1 = now.strftime('%Y-%m-%d %H:%M:%S')    
    #Send mail
    if total_price!= 0:
        if (converted_price+converted_shipping <target):
            send_mail(title, converted_price, converted_shipping, email, URL)
            
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
        print("")

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
        upper = 5 * round(max(total_price)/5)
        ax.set_ylim(ymin=0)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        fig.autofmt_xdate()
        ax.grid(which='minor', alpha=0.8)
        plt.grid()


        plt.savefig("results/product_num" + str(product_id) +'.png')
        plt.close()

    return [title.split(",")[0], converted_price, converted_shipping, d1]
    




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

def autolabel(rects1,rects2):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect1,rect2 in zip(rects1,rects2):
        height = round(rect1.get_height() + rect2.get_height(),2)
        if height == 0:
            label = "Item Unavailable"
        else:
            label = height
        ax.annotate('{}'.format(label),
                    xy=(rect1.get_x() + rect1.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    

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
print(numLinks)
        
    
print("Notification will be sent to " + email)
print("Scraping price information from: ")
for i in range(numLinks):
    print(URL_list[i])
    print("Target: $" + str(price_target[i]))
print("")

start = int(round(time.time()))

#Execute one time
print("")
print("Fetching results")
pricing_results = []
product_current = []
current_price = []
current_shipping = []
for i in range(numLinks):
    pricing_results = scrap(URL_list[i],price_target[i], email)

    product_current.append(pricing_results[0][0:10])
    current_price.append(pricing_results[1])
    current_shipping.append(pricing_results[2])
    timing = (pricing_results[3])
            
indexes = [z for z in range(numLinks)]
width = 0.15

fig, ax = plt.subplots(figsize=(20, 15))

rects1=ax.bar(indexes, current_price, width, color='b', align='center')
rects2=ax.bar(indexes, current_shipping, width, bottom=current_price, color='r', align='center')

ax.set_ylabel('Prices in SGD')
ax.set_title('Prices of Products retrieved at ' + timing)
plt.xticks(indexes, product_current, rotation = 90)


ax.legend(labels=['Product Price', 'Shipping Price'])
ax.grid(which='minor', alpha=0.8)

autolabel(rects1,rects2)


plt.grid()

plt.savefig("price_compare/price_compare" + "_" + timing.replace(" ","_").replace(":","_") + ".png")
plt.close()
start = int(round(time.time()))

    
while (True):

    pricing_results = []
    product_current = []
    current_price = []
    current_shipping = []
    if (int(round(time.time())) - start >= (interval)):
        print("")
        print("Fetching results")
        for i in range(numLinks):
            pricing_results = scrap(URL_list[i],price_target[i], email)
            
            product_current.append(pricing_results[0][0:10])
            current_price.append(pricing_results[1])
            current_shipping.append(pricing_results[2])
            timing = (pricing_results[3])
            
        indexes = [z for z in range(numLinks)]


        width = 0.15

        fig, ax = plt.subplots(figsize=(20, 15))

        ax.bar(indexes, current_price, width, color='b', align='center')
        ax.bar(indexes, current_shipping, width,bottom=current_price, color='r', align='center')

        ax.set_ylabel('Prices in SGD')
        ax.set_title('Prices of Products retrieved at ' + timing)
        plt.xticks(indexes, product_current, rotation = 90)
        upper = 5*round((max(current_price) + max(current_shipping))/5)


        ax.legend(labels=['Product Price', 'Shipping Price'])
        ax.grid(which='minor', alpha=0.8)
        autolabel(rects1,rects2)

        plt.grid()

        plt.savefig("price_compare/price_compare" + "_" + timing.replace(" ","_").replace(":","_") + ".png")
        plt.close()

        
        start = int(round(time.time()))
        
        
    

