import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import smtplib
import mysql.connector


def scrap(URL, target, email):

    #Selenium to render JS
    driver = webdriver.Chrome("chromedriver.exe")
    #URL = 'https://www.amazon.com/gp/product/B07N6S4SY1/r'
    driver.get(URL)

      
    content = driver.page_source.encode('utf-8').strip()
    driver.quit()

    soup = BeautifulSoup(content, 'html.parser')
    title = soup.find(id="productTitle").get_text().strip().replace('”','"')
    price = soup.find(id="priceblock_ourprice").get_text()
    shipping_price = soup.find(class_="a-size-base a-color-secondary").get_text()
    

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
    print(title)
    print(converted_price)
    print(converted_shipping)

    if (converted_price+converted_shipping <target):
        send_mail(title, converted_price, converted_shipping, email)
        
    


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
URL_list = []
price_target = []
for i in range(numLinks):
    URL_list.append(input("Enter URL Link for website #" + str(i+1)+ ": "))
    price_target.append(float(input("Enter price target for this product: ")))

while (True):
    for i in range(numLinks):
        scrap(URL_list[i],price_target[i], email)
    time.sleep(60*60*2)

