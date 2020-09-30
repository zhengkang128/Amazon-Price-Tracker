# Amazon-Price-Tracker

## Introduction
A simple application that sends email notification when the price of your products falls below a certain value.  
This application uses BeautifulSoup, a web scrapping library, to obtain price information of products.  
A MySQL database is used to record any real-time information of changes of prices.  

## How To Use  
### Requirements  
Python 3.6  
MySQL  
Chromedriver (Download at https://chromedriver.chromium.org/ and unzip the .exe file at the same directory as the python scripts)  

### Libraries  
requests  
bs4  
selenium  
time  
smtplib  
datetime  
mysql.connector  
matplotlib  

### Instructions  
1. Run create_price_tracker_db.sql to create database.  
2. Change the user and password in price_tracker.py to your connection for MySQL.  
3. Edit input.txt file in the following order:  
      <Your-Email-Address>   
      <URL #1>  
      <Target Price #1>  
      <URL #2>  
      <Target Price #2>  
           .  
           .  
           .  
      <URL #N>  
      <Target Price #N>  
 4. Run webscrapping script, price_tracker.py  
  

