CREATE SCHEMA `tracker_db` ;

USE tracker_db;
CREATE TABLE `tracker_db`.`price_information` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `product_name` VARCHAR(1000) NOT NULL,
  `date_retrieved` DATETIME NOT NULL,
  `total_price` FLOAT,
  `product_price` FLOAT,
  `shipping_price` FLOAT,
  PRIMARY KEY (`id`));
  
CREATE TABLE `tracker_db`.`products` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `product_name` VARCHAR(1000) NOT NULL,
  `comments` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`id`));