-- Migration for table competition_record
ALTER TABLE competition_record RENAME TO competition_record_old;
CREATE TABLE competition_record (
 Competition_ID INT   REFERENCES farm_competition(Competition_ID),
  Farm_ID INT   REFERENCES farm(Farm_ID),
  Rank INT,
  competition_record_pk TEXT PRIMARY KEY
);
INSERT INTO competition_record (Competition_ID, Farm_ID, Rank, competition_record_pk)
SELECT Competition_ID, Farm_ID, Rank, CAST(Competition_ID AS TEXT) || '_' || CAST(Farm_ID AS TEXT) AS competition_record_pk FROM competition_record_old;
DROP TABLE competition_record_old;
