PRAGMA foreign_keys = ON;

CREATE TABLE Students (
`student_id` INTEGER NOT NULL,
`bio_data` VARCHAR(255) NOT NULL,
`student_details` VARCHAR(255) NOT NULL,
PRIMARY KEY (`student_id`)
);
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (276, 'Camila', 'Suite 076');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (287, 'Dino', 'Suite 970');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (325, 'Pansy', 'Apt. 149');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (361, 'Louvenia', 'Suite 218');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (415, 'Leora', 'Apt. 748');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (435, 'Vanessa', 'Suite 684');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (471, 'Antone', 'Suite 303');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (567, 'Arturo', 'Apt. 491');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (648, 'Leonard', 'Suite 505');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (669, 'Brenden', 'Apt. 305');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (762, 'Edison', 'Apt. 763');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (777, 'Houston', 'Apt. 040');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (811, 'Felipa', 'Apt. 253');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (824, 'Stephon', 'Suite 839');
INSERT INTO Students (`student_id`, `bio_data`, `student_details`) VALUES (984, 'Keshawn', 'Suite 889');



/* ---------------------------------------------------------------------- */
/* Add table "Transcripts"                                                */
/* ---------------------------------------------------------------------- */
CREATE TABLE Transcripts (
`transcript_id` INTEGER NOT NULL,
`student_id` INTEGER NOT NULL,
`date_of_transcript` DATETIME(3),
`transcript_details` VARCHAR(255) NOT NULL,
PRIMARY KEY (`transcript_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id)
);


INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (131, 669, '1973-08-09 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (138, 824, '1973-11-05 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (145, 361, '2002-11-23 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (167, 276, '2017-03-17 00:00:00.000', 'Pass');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (177, 811, '2010-12-14 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (224, 567, '1973-05-05 00:00:00.000', 'Pass');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (264, 824, '2005-06-04 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (276, 415, '2002-02-26 00:00:00.000', 'Pass');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (283, 287, '1979-04-05 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (293, 276, '2017-10-31 00:00:00.000', 'Pass');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (307, 648, '1981-12-01 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (309, 777, '1979-02-07 00:00:00.000', 'Pass');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (325, 361, '2015-07-24 00:00:00.000', 'Good');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (330, 669, '2014-09-13 00:00:00.000', 'Pass');
INSERT INTO Transcripts (`transcript_id`, `student_id`, `date_of_transcript`, `transcript_details`) VALUES (377, 984, '1982-12-04 00:00:00.000', 'Pass');


/* ---------------------------------------------------------------------- */
/* Add table "Behaviour_Monitoring"                                       */
/* ---------------------------------------------------------------------- */
CREATE TABLE Behaviour_Monitoring (
`behaviour_monitoring_id` INTEGER NOT NULL,
`student_id` INTEGER NOT NULL,
`behaviour_monitoring_details` VARCHAR(255) NOT NULL,
PRIMARY KEY (`behaviour_monitoring_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id)
);
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (142, 435, 'A');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (220, 811, 'A');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (248, 567, 'A');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (265, 984, 'B');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (376, 648, 'B');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (434, 777, 'B');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (448, 567, 'C');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (477, 287, 'C');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (572, 287, 'A');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (674, 361, 'C');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (701, 669, 'D');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (705, 435, 'A');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (834, 984, 'E');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (873, 325, 'A');
INSERT INTO Behaviour_Monitoring (`behaviour_monitoring_id`, `student_id`, `behaviour_monitoring_details`) VALUES (994, 648, 'B');

/* ---------------------------------------------------------------------- */
/* Add table "Addresses"                                                  */
/* ---------------------------------------------------------------------- */
CREATE TABLE Addresses (
`address_id` INTEGER NOT NULL,
`address_details` VARCHAR(255) NOT NULL,
PRIMARY KEY (`address_id`)
);

INSERT INTO Addresses (`address_id`, `address_details`) VALUES (0, '607 Nikita Cape Suite 449');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (4, '4474 Dina Park');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (5, '19571 Garrett Manor');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (34, '423 Rosenbaum Shores Apt. 812');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (47, '100 Hayes Point');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (51, '0773 Kaci Villages');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (66, '33376 Terry Mews Suite 922');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (72, '90147 Greenholt Springs Apt. 497');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (74, '1951 Beatty Oval');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (76, '41082 Calista Mountains');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (85, '4240 Enrico Grove');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (90, '7127 Ressie Plains');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (94, '222 Chase Union Apt. 747');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (97, '564 Aaliyah Trace');
INSERT INTO Addresses (`address_id`, `address_details`) VALUES (98, '033 Robel Courts Apt. 312');



/* ---------------------------------------------------------------------- */
/* Add table "Ref_Event_Types"                                            */
/* ---------------------------------------------------------------------- */
CREATE TABLE Ref_Event_Types (
`event_type_code` CHAR(10) NOT NULL,
`event_type_description` VARCHAR(255) NOT NULL,
PRIMARY KEY (`event_type_code`)
);
CREATE TABLE Ref_Achievement_Type (
`achievement_type_code` CHAR(15) NOT NULL,
`achievement_type_description` VARCHAR(80),
PRIMARY KEY (`achievement_type_code`)
);


/* ---------------------------------------------------------------------- */
/* Add table "Ref_Address_Types"                                          */
/* ---------------------------------------------------------------------- */
CREATE TABLE Ref_Address_Types (
`address_type_code` CHAR(10) NOT NULL,
`address_type_description` VARCHAR(255) NOT NULL,
PRIMARY KEY (`address_type_code`)
);

/* ---------------------------------------------------------------------- */
/* Add table "Ref_Detention_Type"                                         */
/* ---------------------------------------------------------------------- */
CREATE TABLE Ref_Detention_Type (
`detention_type_code` CHAR(10) NOT NULL,
`detention_type_description` VARCHAR(80),
PRIMARY KEY (`detention_type_code`)
);

INSERT INTO Ref_Achievement_Type (`achievement_type_code`, `achievement_type_description`) VALUES ('Athletic', 'Athletic');
INSERT INTO Ref_Achievement_Type (`achievement_type_code`, `achievement_type_description`) VALUES ('Scholastic', 'Scholastic');
INSERT INTO Ref_Address_Types (`address_type_code`, `address_type_description`) VALUES ('CO', 'College');
INSERT INTO Ref_Address_Types (`address_type_code`, `address_type_description`) VALUES ('HM', 'Home');
INSERT INTO Ref_Detention_Type (`detention_type_code`, `detention_type_description`) VALUES ('After School', 'After School');
INSERT INTO Ref_Detention_Type (`detention_type_code`, `detention_type_description`) VALUES ('Break', 'On break');
INSERT INTO Ref_Detention_Type (`detention_type_code`, `detention_type_description`) VALUES ('Illness', 'Leave for illness');
INSERT INTO Ref_Detention_Type (`detention_type_code`, `detention_type_description`) VALUES ('Lunch', 'During lunchtime');
INSERT INTO Ref_Event_Types (`event_type_code`, `event_type_description`) VALUES ('Exam', 'Exam');
INSERT INTO Ref_Event_Types (`event_type_code`, `event_type_description`) VALUES ('Registration', 'Registration');


/* ---------------------------------------------------------------------- */
/* Add table "Student_Events"                                             */
/* ---------------------------------------------------------------------- */
CREATE TABLE Student_Events (
`event_id` INTEGER NOT NULL,
`event_type_code` CHAR(10) NOT NULL,
`student_id` INTEGER NOT NULL,
`event_date` DATETIME(3),
`other_details` VARCHAR(255) NOT NULL,
PRIMARY KEY (`event_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id),
FOREIGN KEY (event_type_code) REFERENCES Ref_Event_Types (event_type_code)
);

INSERT INTO Student_Events (`event_id`, `event_type_code`, `student_id`, `event_date`, `other_details`) VALUES (146, 'Exam', 287, '2008-08-15 22:16:17.000', '');
INSERT INTO Student_Events (`event_id`, `event_type_code`, `student_id`, `event_date`, `other_details`) VALUES (161, 'Exam', 777, '2014-07-15 18:18:15.000', '');
INSERT INTO Student_Events (`event_id`, `event_type_code`, `student_id`, `event_date`, `other_details`) VALUES (189, 'Exam', 361, '2013-04-14 04:14:10.000', '');
INSERT INTO Student_Events (`event_id`, `event_type_code`, `student_id`, `event_date`, `other_details`) VALUES (227, 'Registration', 669, '2012-12-06 06:44:53.000', '');




/* ---------------------------------------------------------------------- */
/* Add table "Teachers"                                                   */
/* ---------------------------------------------------------------------- */
CREATE TABLE Teachers (
`teacher_id` INTEGER NOT NULL,
`teacher_details` VARCHAR(255),
PRIMARY KEY (`teacher_id`)
);

INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (115, 'Jon');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (127, 'Tyson');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (164, 'Trinity');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (172, 'Viva');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (195, 'Osvaldo');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (212, 'Isabel');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (226, 'Adella');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (234, 'Chasity');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (252, 'Wilfredo');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (253, 'Marielle');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (274, 'Beverly');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (282, 'Nicholaus');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (298, 'Arianna');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (302, 'Angie');
INSERT INTO Teachers (`teacher_id`, `teacher_details`) VALUES (316, 'Hertha');

/* ---------------------------------------------------------------------- */
/* Add table "Ref_Achievement_Type"                                       */
/* ---------------------------------------------------------------------- */

/* ---------------------------------------------------------------------- */
/* Add table "Student_Loans"                                              */
/* ---------------------------------------------------------------------- */
CREATE TABLE Student_Loans (
`student_loan_id` INTEGER NOT NULL,
`student_id` INTEGER NOT NULL,
`date_of_loan` DATETIME(3),
`amount_of_loan` DECIMAL(15,4),
`other_details` VARCHAR(255),
PRIMARY KEY (`student_loan_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id)
);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (165, 777, '1980-01-06 00:00:00.000', '2216.1500', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (169, 669, '1991-03-24 00:00:00.000', '5223.1800', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (188, 777, '1983-08-01 00:00:00.000', '3221.4900', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (205, 777, '1977-08-27 00:00:00.000', '3358.8700', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (267, 435, '2018-01-17 00:00:00.000', '5174.7600', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (269, 361, '1989-05-07 00:00:00.000', '3803.6000', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (287, 984, '1989-04-23 00:00:00.000', '1561.5700', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (366, 361, '1992-11-14 00:00:00.000', '4190.3200', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (408, 762, '1994-02-24 00:00:00.000', '4213.1300', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (550, 762, '2004-04-11 00:00:00.000', '1644.6500', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (574, 325, '1975-07-21 00:00:00.000', '1419.9700', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (596, 824, '1978-08-01 00:00:00.000', '4454.3000', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (652, 984, '2001-07-31 00:00:00.000', '4407.2700', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (684, 415, '1993-11-23 00:00:00.000', '3768.4900', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (718, 325, '1981-05-31 00:00:00.000', '2312.5300', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (824, 824, '2012-11-19 00:00:00.000', '1785.4400', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (837, 984, '1994-02-10 00:00:00.000', '2645.7600', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (850, 287, '1973-10-22 00:00:00.000', '5006.9400', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (889, 567, '2014-01-06 00:00:00.000', '3685.7400', NULL);
INSERT INTO Student_Loans (`student_loan_id`, `student_id`, `date_of_loan`, `amount_of_loan`, `other_details`) VALUES (965, 824, '1983-05-03 00:00:00.000', '4528.5000', NULL);


/* ---------------------------------------------------------------------- */
/* Add table "Classes"                                                    */
/* ---------------------------------------------------------------------- */
CREATE TABLE Classes (
`class_id` INTEGER NOT NULL,
`student_id` INTEGER NOT NULL,
`teacher_id` INTEGER NOT NULL,
`class_details` VARCHAR(255) NOT NULL,
PRIMARY KEY (`class_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id),
FOREIGN KEY (teacher_id) REFERENCES Teachers (teacher_id)
);
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (114, 435, 253, 'databases');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (195, 471, 274, 'english');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (235, 811, 282, 'writing');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (248, 471, 252, 'statistics');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (294, 762, 234, 'math 100');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (354, 287, 302, 'math 300');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (387, 325, 316, 'statistics 100');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (411, 811, 316, 'databases 200');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (424, 669, 252, 'computer science 100');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (429, 669, 195, 'data structure');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (451, 762, 274, 'programming');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (455, 471, 274, 'art 300');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (493, 824, 252, 'music 100');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (529, 567, 127, 'computer science 300');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (552, 984, 234, 'law 200');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (553, 762, 226, 'art 100');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (579, 276, 282, 'debate');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (600, 361, 195, 'networks');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (613, 435, 212, 'dancing');
INSERT INTO Classes (`class_id`, `student_id`, `teacher_id`, `class_details`) VALUES (621, 811, 234, 'acting');


/* ---------------------------------------------------------------------- */
/* Add table "Students_Addresses"                                         */
/* ---------------------------------------------------------------------- */
CREATE TABLE Students_Addresses (
`student_address_id` INTEGER NOT NULL,
`address_id` INTEGER NOT NULL,
`address_type_code` CHAR(10) NOT NULL,
`student_id` INTEGER NOT NULL,
`date_from` DATETIME(3),
`date_to` DATETIME(3),
PRIMARY KEY (`student_address_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id),
FOREIGN KEY (address_id) REFERENCES Addresses (address_id),
FOREIGN KEY (address_type_code) REFERENCES Ref_Address_Types (address_type_code)
);
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (11, 94, 'HM', 984, '2011-06-29 09:45:39.000', '2018-03-22 07:50:48.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (15, 76, 'HM', 415, '2011-10-04 09:58:41.000', '2018-03-14 18:32:37.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (20, 97, 'CO', 777, '2015-02-01 00:20:42.000', '2018-03-04 09:58:38.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (23, 72, 'CO', 361, '2015-03-14 15:55:46.000', '2018-03-08 08:41:07.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (33, 97, 'HM', 762, '2017-05-18 23:15:01.000', '2018-03-20 08:06:53.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (35, 98, 'HM', 762, '2009-04-27 17:42:38.000', '2018-02-28 07:36:43.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (45, 90, 'HM', 777, '2014-03-28 08:03:34.000', '2018-03-11 19:21:54.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (56, 94, 'HM', 777, '2009-08-24 22:57:30.000', '2018-03-10 09:05:12.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (59, 98, 'HM', 777, '2013-05-27 16:51:49.000', '2018-02-27 11:03:50.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (67, 0, 'HM', 361, '2011-04-29 03:20:26.000', '2018-03-02 04:33:35.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (73, 34, 'CO', 471, '2008-04-20 04:24:19.000', '2018-03-18 22:15:17.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (80, 85, 'HM', 471, '2009-02-23 20:33:05.000', '2018-03-06 22:42:42.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (84, 76, 'HM', 415, '2008-09-21 02:28:34.000', '2018-03-03 17:46:12.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (91, 66, 'HM', 276, '2012-12-17 20:22:50.000', '2018-03-22 10:12:26.000');
INSERT INTO Students_Addresses (`student_address_id`, `address_id`, `address_type_code`, `student_id`, `date_from`, `date_to`) VALUES (92, 97, 'HM', 361, '2009-06-21 04:28:15.000', '2018-03-04 23:55:53.000');


/* ---------------------------------------------------------------------- */
/* Add table "Detention"                                                  */
/* ---------------------------------------------------------------------- */
CREATE TABLE Detention (
`detention_id` INTEGER NOT NULL,
`detention_type_code` CHAR(10) NOT NULL,
`student_id` INTEGER NOT NULL,
`datetime_detention_start` DATETIME(3),
`datetime_detention_end` DATETIME(3),
`detention_summary` VARCHAR(255),
`other_details` VARCHAR(255),
PRIMARY KEY (`detention_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id),
FOREIGN KEY (detention_type_code) REFERENCES Ref_Detention_Type (detention_type_code)
);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (133, 'Lunch', 361, '2012-03-18 09:49:33.000', '2011-09-15 05:58:59.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (141, 'After School', 811, '2012-06-07 15:01:05.000', '2009-05-23 17:33:31.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (211, 'Break', 762, '2011-04-24 17:23:32.000', '2013-09-06 15:49:53.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (242, 'After School', 648, '2014-01-16 00:49:33.000', '2013-04-07 15:42:52.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (384, 'Illness', 762, '2016-12-28 21:44:59.000', '2013-04-20 13:13:40.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (401, 'Break', 415, '2011-03-22 20:51:56.000', '2013-10-06 03:49:35.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (451, 'After School', 361, '2014-02-03 00:18:05.000', '2012-05-09 00:54:20.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (478, 'Illness', 762, '2010-03-14 06:33:25.000', '2015-10-16 19:21:09.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (492, 'Break', 471, '2018-03-16 04:10:29.000', '2008-06-03 01:53:37.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (545, 'Illness', 276, '2013-06-24 06:36:47.000', '2014-05-18 21:10:48.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (576, 'After School', 471, '2010-08-24 04:11:35.000', '2015-12-13 06:27:13.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (646, 'Illness', 984, '2017-08-12 03:26:18.000', '2013-12-02 02:48:47.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (796, 'Illness', 415, '2010-08-16 18:17:43.000', '2013-10-18 09:56:25.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (804, 'After School', 648, '2015-07-11 17:47:17.000', '2014-10-14 11:25:12.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (860, 'Illness', 435, '2009-07-29 16:16:12.000', '2016-06-03 08:58:25.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (868, 'Illness', 435, '2017-01-09 13:20:45.000', '2016-06-03 07:14:46.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (876, 'After School', 669, '2008-04-12 06:33:01.000', '2009-10-12 19:06:35.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (904, 'Break', 648, '2013-03-02 16:45:53.000', '2010-11-06 02:41:01.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (907, 'After School', 762, '2011-03-27 16:53:25.000', '2015-01-29 21:12:58.000', NULL, NULL);
INSERT INTO Detention (`detention_id`, `detention_type_code`, `student_id`, `datetime_detention_start`, `datetime_detention_end`, `detention_summary`, `other_details`) VALUES (962, 'After School', 435, '2011-05-19 23:10:25.000', '2015-12-14 01:07:11.000', NULL, NULL);



/* ---------------------------------------------------------------------- */
/* Add table "Achievements"                                               */
/* ---------------------------------------------------------------------- */
CREATE TABLE Achievements (
`achievement_id` INTEGER NOT NULL,
`achievement_type_code` CHAR(15) NOT NULL,
`student_id` INTEGER NOT NULL,
`date_achievement` DATETIME(3),
`achievement_details` VARCHAR(255),
`other_details` VARCHAR(255),
PRIMARY KEY (`achievement_id`),
FOREIGN KEY (student_id) REFERENCES Students (student_id),
FOREIGN KEY (achievement_type_code) REFERENCES Ref_Achievement_Type (achievement_type_code)
);
/* ---------------------------------------------------------------------- */
/* Foreign key constraints                                                */
/* ---------------------------------------------------------------------- */
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (153, 'Athletic', 777, 2013, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (159, 'Athletic', 415, 2013, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (262, 'Scholastic', 415, 2014, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (264, 'Scholastic', 471, 2014, 'Silver', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (316, 'Scholastic', 648, 2014, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (340, 'Scholastic', 276, 2014, 'Bronze', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (450, 'Athletic', 669, 2014, 'Bronze', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (602, 'Scholastic', 824, 2014, 'Silver', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (650, 'Athletic', 777, 2014, 'Silver', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (672, 'Athletic', 984, 2014, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (697, 'Scholastic', 762, 2014, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (702, 'Scholastic', 325, 2014, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (717, 'Athletic', 567, 2015, 'Silver', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (722, 'Athletic', 777, 2015, 'Silver', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (753, 'Scholastic', 325, 2015, 'Silver', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (770, 'Athletic', 287, 2015, 'Silver', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (877, 'Athletic', 471, 2015, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (885, 'Scholastic', 811, 2015, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (933, 'Athletic', 648, 2015, 'Gold', NULL);
INSERT INTO Achievements (`achievement_id`, `achievement_type_code`, `student_id`, `date_achievement`, `achievement_details`, `other_details`) VALUES (964, 'Scholastic', 811, 2016, 'Gold', NULL);

