PRAGMA foreign_keys = ON;
CREATE TABLE `Products` (
`product_id` INTEGER PRIMARY KEY,
`product_type_code` VARCHAR(15),
`product_name` VARCHAR(80),
`product_price` DOUBLE NULL
);

CREATE TABLE `Addresses` (
`address_id` INTEGER PRIMARY KEY,
`address_details` VARCHAR(255)
);

CREATE TABLE `Customers` (
`customer_id` INTEGER PRIMARY KEY,
`address_id` INTEGER NOT NULL,
`payment_method_code` VARCHAR(15),
`customer_number` VARCHAR(20),
`customer_name` VARCHAR(80),
`customer_address` VARCHAR(255),
`customer_phone` VARCHAR(80),
`customer_email` VARCHAR(80)
);
CREATE TABLE `Customer_Orders` (
`order_id` INTEGER PRIMARY KEY,
`customer_id` INTEGER NOT NULL,
`order_date` DATETIME NOT NULL,
`order_status_code` VARCHAR(15),
FOREIGN KEY (`customer_id` ) REFERENCES `Customers`(`customer_id` )
);
CREATE TABLE `Order_Items` (
`order_item_id` INTEGER NOT NULL ,
`order_id` INTEGER NOT NULL,
`product_id` INTEGER NOT NULL,
`order_quantity` VARCHAR(80),
FOREIGN KEY (`order_id` ) REFERENCES `Customer_Orders`(`order_id` ),
FOREIGN KEY (`product_id` ) REFERENCES `Products`(`product_id` )
);

INSERT INTO Addresses (`address_id`, `address_details`) VALUES (1, '2632 Ofelia Stream Apt. 537
Rueckerborough, NV 78430-4096');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (2, '481 Tyrique Junction
West Kali, UT 16070-1379');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (3, '4363 Otilia Hill
Landenshire, ND 45637');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (4, '1734 Klocko Views Suite 840
Schusterfort, WY 34067-3366');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (5, '001 Eliza Ferry Suite 929
Schillerfurt, WI 60335-2125');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (6, '8013 O''Keefe Harbors
New Baronview, AR 57984');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (7, '50445 Gerhold Springs
Jaleelstad, IL 16333-3222');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (8, '13460 Rylee Green
South Domenicamouth, NM 36408-2902');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (9, '59479 Eladio Cliff
Wymanside, PA 69696-5826');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (10, '4959 Dixie Oval
North Timothyberg, OK 88659');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (11, '80770 Borer Square
Lillianaborough, NE 46012-9033');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (12, '83114 Vanessa Mountains Suite 788
North Kara, CA 25470-9357');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (13, '078 Jameson Avenue
Cyrusberg, MN 88459-2009');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (14, '0335 Ferne Dale
East Lura, AZ 62151-8685');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (15, '140 Norene Ford
Port Buddymouth, MA 08157-7414');


INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (1, 'Hardware', 'Monitor', '2084.944172129');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (2, 'Clothes', 'Topping', '26045678.098468');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (3, 'Clothes', 'Black Jeans', '7312007.4430563');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (4, 'Clothes', 'Blue Jeans', '473.92262166875');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (5, 'Clothes', 'Yellow Jeans', '34529451.515631');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (6, 'Clothes', 'Gray Jeans', '6897489.4162472');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (7, 'Hardware', 'Mouse', '196066792.36835');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (8, 'Clothes', 'White Topping', '705.9133468689');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (9, 'Hardware', 'Keyboard', '495.99319506948');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (10, 'Hardware', 'Drive', '37993003.400391');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (11, 'Clothes', 'Purple Topping', '7194641.5117043');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (12, 'Clothes', 'Black Topping', '201509245.10256');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (13, 'Clothes', 'Yellow Topping', '840.34678227843');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (14, 'Hardware', 'DVD', '870.50471411809');
INSERT INTO Products (`product_id`, `product_type_code`, `product_name`, `product_price`) VALUES (15, 'Clothes', 'Blue Topping', '2825.6814780336');

INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (1, 9, 'Credit Card', '601', 'Jeromy', '422 Bode Mount Apt. 688', '1-968-453-3485', 'everett.kautzer@example.com');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (2, 8, 'Credit Card', '920', 'Edmond', '0965 Dickens Springs', '+92(8)6677749570', 'maegan54@example.net');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (3, 3, 'Credit Card', '990', 'Twila', '878 Joy Fields Apt. 366', '(291)441-3432', 'dedric.bailey@example.org');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (4, 11, 'Credit Card', '037', 'Madelynn', '9128 Berry Mountains Suite 608', '1-909-419-5704x7658', 'white.barney@example.net');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (5, 7, 'Credit Card', '949', 'Nya', '689 Wilkinson Coves Apt. 107', '739-333-7916', 'eldred44@example.net');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (6, 1, 'Credit Card', '892', 'Kenna', '5425 Vern Rue Suite 490', '804-701-9307', 'thomas67@example.org');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (7, 10, 'Credit Card', '707', 'Katrina', '73546 Gaylord Harbors Suite 881', '239.351.4998x35742', 'hoyt80@example.org');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (8, 9, 'Credit Card', '979', 'Jaylan', '76957 Kohler Via Suite 315', '+10(8)9243074470', 'penelope.koepp@example.com');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (9, 7, 'Credit Card', '025', 'Jeremie', '97464 Greenholt Tunnel', '1-766-484-5984x4558', 'kuhn.mable@example.org');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (10, 9, 'Direct Debit', '319', 'Lenny', '869 Anastasia Knoll Apt. 100', '457.149.5849', 'brooks08@example.org');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (11, 2, 'Direct Debit', '102', 'Gunner', '44535 Lisette Valleys Apt. 520', '09657208451', 'katelynn81@example.net');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (12, 13, 'Credit Card', '759', 'Abe', '022 Turner Shore Suite 221', '+96(9)6593071847', 'floyd.boyer@example.net');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (13, 1, 'Direct Debit', '769', 'Kennith', '047 Lang Island Apt. 977', '100-037-1493x19148', 'tromp.maye@example.net');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (14, 2, 'Credit Card', '431', 'Mittie', '31742 Grant Plain Suite 093', '+22(4)3215644293', 'daniel.hilma@example.net');
INSERT INTO Customers (`customer_id`, `address_id`, `payment_method_code`, `customer_number`, `customer_name`, `customer_address`, `customer_phone`, `customer_email`) VALUES (15, 15, 'Direct Debit', '202', 'Alexandrine', '85441 Frieda Skyway', '183.800.7178x7079', 'marguerite93@example.net');

INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (1, 12, '2016-05-14 22:08:41', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (2, 3, '1991-02-26 11:32:39', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (3, 3, '2000-06-26 05:17:11', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (4, 1, '1987-06-28 09:12:32', 'Completed');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (5, 15, '1994-12-17 22:49:09', 'Completed');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (6, 13, '1978-09-08 23:31:23', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (7, 15, '2009-11-20 18:18:29', 'Completed');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (8, 9, '1994-02-07 07:27:57', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (9, 5, '2007-11-23 04:32:19', 'Completed');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (10, 14, '1986-01-30 15:27:58', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (11, 8, '2005-11-10 16:19:29', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (12, 13, '2016-03-01 07:51:02', 'Part');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (13, 4, '2016-02-19 18:07:06', 'Completed');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (14, 12, '2013-08-10 03:01:33', 'Completed');
INSERT INTO Customer_Orders (`order_id`, `customer_id`, `order_date`, `order_status_code`) VALUES (15, 14, '1993-11-03 13:47:02', 'Part');

INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (1, 8, 13, '2');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (2, 1, 10, '2');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (3, 13, 11, '4');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (4, 8, 1, '7');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (5, 2, 7, '7');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (6, 5, 5, '4');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (7, 14, 2, '1');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (8, 1, 1, '9');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (9, 2, 8, '7');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (10, 6, 4, '7');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (11, 12, 15, '7');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (12, 1, 12, '8');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (13, 8, 4, '5');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (14, 8, 15, '1');
INSERT INTO Order_Items (`order_item_id`, `order_id`, `product_id`, `order_quantity`) VALUES (15, 1, 12, '7');
