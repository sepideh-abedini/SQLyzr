PRAGMA foreign_keys = ON;

CREATE TABLE Staff (
staff_id INTEGER NOT NULL,
staff_details VARCHAR(255) NOT NULL,
PRIMARY KEY (staff_id)
);
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (3, 'Mrs. Aniya Klocko Sr.');
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (26, 'Prof. Pietro Hudson');
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (52, 'Mr. Sid Hessel');
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (66, 'Rosie Conn');
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (67, 'Jade O''Connell III');
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (76, 'Santina Cronin');
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (93, 'Bella Hilll DDS');
INSERT INTO Staff (`staff_id`, `staff_details`) VALUES (100, 'Prof. Porter Dickinson Sr.');


CREATE TABLE Ref_Staff_Roles (
staff_role_code CHAR(15) NOT NULL,
staff_role_description VARCHAR(255) NOT NULL,
PRIMARY KEY (staff_role_code)
);
INSERT INTO Ref_Staff_Roles (`staff_role_code`, `staff_role_description`) VALUES ('MG', 'Manager');
INSERT INTO Ref_Staff_Roles (`staff_role_code`, `staff_role_description`) VALUES ('ED', 'Editor');
INSERT INTO Ref_Staff_Roles (`staff_role_code`, `staff_role_description`) VALUES ('PT', 'Photo');
INSERT INTO Ref_Staff_Roles (`staff_role_code`, `staff_role_description`) VALUES ('PR', 'Proof Reader');
INSERT INTO Ref_Staff_Roles (`staff_role_code`, `staff_role_description`) VALUES ('HR', 'Human Resource');


CREATE TABLE Process_Outcomes (
process_outcome_code CHAR(15) NOT NULL,
process_outcome_description VARCHAR(255) NOT NULL,
PRIMARY KEY (process_outcome_code)
);
CREATE TABLE Process_Status (
process_status_code CHAR(15) NOT NULL,
process_status_description VARCHAR(255) NOT NULL,
PRIMARY KEY (process_status_code)
);
INSERT INTO Process_Outcomes (`process_outcome_code`, `process_outcome_description`) VALUES ('working', 'working on');
INSERT INTO Process_Outcomes (`process_outcome_code`, `process_outcome_description`) VALUES ('finish', 'finish');
INSERT INTO Process_Outcomes (`process_outcome_code`, `process_outcome_description`) VALUES ('start', 'starting soon');
INSERT INTO Process_Status (`process_status_code`, `process_status_description`) VALUES ('ct', 'continue');
INSERT INTO Process_Status (`process_status_code`, `process_status_description`) VALUES ('pp', 'postpone');



CREATE TABLE Authors (
author_name VARCHAR(255) NOT NULL,
other_details VARCHAR(255) NOT NULL,
PRIMARY KEY (author_name)
);

INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Addison Denesik', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Adeline Wolff', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Antwon Krajcik V', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Beverly Bergnaum MD', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Bianka Cummings', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Dr. Dario Hermiston', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Dr. Shad Lowe', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Era Kerluke', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Eveline Bahringer', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Fiona Sipes DVM', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Jameson Konopelski', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Katharina Koepp', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Malvina Metz', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Marjolaine Paucek', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Mr. Joaquin Sanford', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Prof. Baron Heller II', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Shanie Skiles', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Telly Pfannerstill', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Tevin Weber', '');
INSERT INTO Authors (`author_name`, `other_details`) VALUES ('Vidal Sanford', '');



CREATE TABLE Documents (
document_id INTEGER NOT NULL,
author_name VARCHAR(255) NOT NULL,
document_name VARCHAR(255) NOT NULL,
document_description VARCHAR(255) NOT NULL,
other_details VARCHAR(255),
PRIMARY KEY (document_id),
FOREIGN KEY (author_name) REFERENCES Authors (author_name)
);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (0, 'Malvina Metz', 'Travel to Brazil', 'Nulla molestiae voluptas recusandae dolores explicabo et. Consequuntur ut autem velit eos aut.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (4, 'Telly Pfannerstill', 'Travel to China', 'Maiores suscipit earum sed iure. Quis voluptatem facilis doloremque nisi corrupti. Sed est repellendus et aut id. Nisi quis ex eligendi possimus ut ut unde.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (7, 'Malvina Metz', 'Travel to England', 'Dolores beatae omnis dolorem laudantium quaerat ut. Perspiciatis explicabo est ut vel porro omnis. Aut non occaecati aut quia ut non omnis. Quia quam ea consequuntur quo aliquam.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (24, 'Bianka Cummings', 'Travel to Egypt', 'Culpa voluptatibus alias quo amet dolore eum possimus. Qui placeat cumque non aperiam. Cupiditate pariatur dolorum sed ut.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (29, 'Bianka Cummings', 'Travel to Ireland', 'Cumque a ducimus perferendis sint. Quidem tempora recusandae accusamus possimus aut vitae quo. Omnis earum sint doloribus velit.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (52, 'Eveline Bahringer', 'How to cook chicken', 'Soluta vitae sed soluta. Aut eos omnis dolorem qui non recusandae neque. Atque enim inventore sint dolor sit.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (77, 'Marjolaine Paucek', 'How to cook pasta', 'Occaecati id consectetur amet. Fuga vel voluptate qui autem quisquam quis. Eos rerum et iste impedit vel facere.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (79, 'Tevin Weber', 'How to cook steak', 'Eius rerum rerum architecto optio reprehenderit rerum id. Voluptatem et atque expedita. Voluptatem sint qui aut nostrum voluptas.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (262, 'Addison Denesik', 'How to cook rice', 'Quo alias nam consectetur nostrum voluptatibus omnis occaecati. Perspiciatis assumenda sed ullam veritatis modi id. Animi praesentium tenetur hic reiciendis nihil hic aut.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (462, 'Adeline Wolff', 'Learning about flowers', 'Dolor ipsum sed cum aliquid eius enim exercitationem. Eius cupiditate magni sed et. Ex qui debitis sint aliquam illo eligendi magni praesentium. Et reiciendis sed in nostrum eius asperiores. Repellat et odio non qui mollitia.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (927, 'Tevin Weber', 'Learning about palm reading', 'Omnis perferendis voluptas ea animi ad eum voluptatibus. Tempora natus deleniti consequatur rerum id nisi fugit nihil. Labore repellendus porro consequatur qui.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (435463, 'Antwon Krajcik V', 'Learning about chess', 'Qui dolor et porro ut commodi error sed. Qui deserunt et est provident ut. Et quos libero iusto qui enim.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (461893, 'Era Kerluke', 'Learning about society', 'Magnam quos voluptatibus sit qui. Recusandae dignissimos repellendus et dolor sequi provident. Consectetur occaecati illum laboriosam id.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (782065904, 'Beverly Bergnaum MD', 'Learning about arts', 'Qui omnis sint eligendi adipisci perferendis. Quis id voluptatum nobis sed magnam animi quos. Consequatur voluptates voluptatum iure recusandae.', NULL);
INSERT INTO Documents (`document_id`, `author_name`, `document_name`, `document_description`, `other_details`) VALUES (948678383, 'Beverly Bergnaum MD', 'Learning about history', 'Corrupti porro nemo voluptas voluptatibus ipsam minus sed. Alias dolores voluptatibus reprehenderit sunt architecto mollitia incidunt molestiae.', NULL);


CREATE TABLE Business_Processes (
process_id INTEGER NOT NULL,
next_process_id INTEGER,
process_name VARCHAR(255) NOT NULL,
process_description VARCHAR(255) NOT NULL,
other_details VARCHAR(255),
PRIMARY KEY (process_id)
);
INSERT INTO Business_Processes (`process_id`, `next_process_id`, `process_name`, `process_description`, `other_details`) VALUES (9, 9, 'process', 'normal', NULL);



CREATE TABLE Documents_Processes (
document_id INTEGER NOT NULL,
process_id INTEGER NOT NULL,
process_outcome_code CHAR(15) NOT NULL,
process_status_code CHAR(15) NOT NULL,
PRIMARY KEY (document_id, process_id),
FOREIGN KEY (document_id) REFERENCES Documents (document_id),
FOREIGN KEY (process_id) REFERENCES Business_Processes (process_id),
FOREIGN KEY (process_outcome_code) REFERENCES Process_Outcomes (process_outcome_code),
FOREIGN KEY (process_status_code) REFERENCES Process_Status (process_status_code)
);
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (0, 9, 'finish', 'ct');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (4, 9, 'start', 'ct');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (7, 9, 'start', 'pp');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (24, 9, 'start', 'ct');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (52, 9, 'finish', 'pp');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (462, 9, 'working', 'ct');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (927, 9, 'working', 'pp');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (435463, 9, 'start', 'ct');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (461893, 9, 'finish', 'pp');
INSERT INTO Documents_Processes (`document_id`, `process_id`, `process_outcome_code`, `process_status_code`) VALUES (782065904, 9, 'working', 'ct');


CREATE TABLE Staff_in_Processes (
document_id INTEGER NOT NULL,
process_id INTEGER NOT NULL,
staff_id INTEGER NOT NULL,
staff_role_code CHAR(15) NOT NULL,
date_from DATETIME,
date_to DATETIME,
other_details VARCHAR(255),
PRIMARY KEY (document_id, process_id, staff_id),
FOREIGN KEY (staff_id) REFERENCES Staff (staff_id),
FOREIGN KEY (document_id, process_id) REFERENCES Documents_Processes (document_id,process_id),
FOREIGN KEY (staff_role_code) REFERENCES Ref_Staff_Roles (staff_role_code)
);

INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (0, 9, 3, 'MG', '1989-02-06 18:30:52', '2001-08-10 20:58:06', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (0, 9, 67, 'ED', '2015-01-01 06:43:57', '1982-01-11 19:27:20', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (4, 9, 3, 'HR', '1979-10-19 18:36:39', '1993-12-13 11:55:33', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (7, 9, 100, 'PT', '1988-06-20 01:13:16', '2000-06-15 03:03:57', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (24, 9, 26, 'PR', '1973-02-04 06:53:33', '2005-10-19 08:53:29', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (462, 9, 26, 'ED', '1988-08-05 21:55:02', '1995-03-09 06:54:14', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (462, 9, 76, 'ED', '2009-08-07 08:26:16', '1973-09-18 07:39:56', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (927, 9, 3, 'ED', '1998-09-05 17:52:04', '2014-05-24 01:12:43', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (435463, 9, 52, 'PT', '1972-04-24 05:45:56', '1974-08-02 01:37:15', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (461893, 9, 67, 'HR', '2000-06-10 21:41:38', '2007-02-12 17:11:51', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (461893, 9, 93, 'MG', '2010-05-08 11:30:36', '1973-02-25 01:08:20', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (782065904, 9, 52, 'ED', '2007-07-21 13:51:39', '1970-03-14 11:36:29', NULL);
INSERT INTO Staff_in_Processes (`document_id`, `process_id`, `staff_id`, `staff_role_code`, `date_from`, `date_to`, `other_details`) VALUES (782065904, 9, 66, 'MG', '1983-04-04 06:50:24', '1996-03-15 15:12:08', NULL);
