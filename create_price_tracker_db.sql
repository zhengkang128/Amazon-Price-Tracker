CREATE SCHEMA `price_trackerdb` ;

USE price_trackerdb;
CREATE TABLE `price_trackerdb`.`price_information` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `product_name` VARCHAR(1000) NOT NULL,
  `date_retrieved` DATETIME NOT NULL,
  `total_price` FLOAT,
  `product_price` FLOAT,
  `shipping_price` FLOAT,
  PRIMARY KEY (`id`));