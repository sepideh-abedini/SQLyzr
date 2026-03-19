-- Migration for table follows
ALTER TABLE follows RENAME TO follows_old;
CREATE TABLE follows (
 f1 int(11) NOT NULL  REFERENCES user_profiles(uid),
  f2 int(11) NOT NULL  REFERENCES user_profiles(uid),
  follows_pk TEXT PRIMARY KEY
);
INSERT INTO follows (f1, f2, follows_pk)
SELECT f1, f2, CAST(f1 AS TEXT) || '_' || CAST(f2 AS TEXT) AS follows_pk FROM follows_old;
DROP TABLE follows_old;
