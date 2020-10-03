# Amazon Price Tracker

## Introduction
A simple application that notifies you through email when the price of your targeted products falls below your desired value.  
This application uses BeautifulSoup, a web scrapping library, to obtain price information of products.  
A MySQL database is used to store all real-time information of products when there is a change of pricing.

## Requirements  
### Softwares
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

## How To Use  
1. Run create_price_tracker_db.sql to create database.  

2. Change the user and password in price_tracker.py to your connection for MySQL.  

3. Edit input.txt file in the following order:  
            <<mail@example.com>>  
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
 The script will scrape the product prices every hour. Intervals can be changed by editting the python script itself.
 Product information will be downloaded
 
 5. Visualize Results
 - If the price drops within target, a mail notification will be sent to the email you specified
 - You can view the bar graph (.png) of price comparision among products in the price_compare folder
 - You can view the graph (.png) that models the change of prices over time in the results folder
 - These graphs are updated and accessible after every web-scrapping process

## Visualize Results

### Comparison of Product Prices  
A bar graph is generated and saved to the price_compare folder to visualize the comparison of prices among all the products that were used as an input for price-tracking.  
Respective .png files will be produced for each individual products and saved in the price_compare/ folder after every web-scrapping process.  
An example is shown below:
![alt text](https://github.com/zhengkang128/Amazon-Price-Tracker/blob/master/price_compare/price_compare_2020-10-02_20_00_21.png?raw=true)  

### Changes of Price over Time  
The MySQL database records past information of prices that was obtained.  
This graph is produced by retrieving information from the database containing past results to visualize the change of prices over time.  
Respective .png files will be produced for each individual products and saved in the results/ folder after every web-scrapping process.  
An example is shown below:
![alt text](https://github.com/zhengkang128/Amazon-Price-Tracker/blob/master/results/product_num4.png?raw=true)  


