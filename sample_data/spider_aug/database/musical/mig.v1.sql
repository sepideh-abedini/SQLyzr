-- 1. Rename existing table
ALTER TABLE actor
    RENAME TO actor_old;

-- 2. Create new table with correct foreign key
CREATE TABLE actor
(
    Actor_ID   INTEGER PRIMARY KEY,
    Name       TEXT,
    Musical_ID INTEGER,
    Character  TEXT,
    Duration   TEXT,
    age        INTEGER,
    FOREIGN KEY (Musical_ID) REFERENCES musical (Musical_ID)
);

-- 3. Copy data from old table
INSERT INTO actor (Actor_ID, Name, Musical_ID, Character, Duration, age)
SELECT Actor_ID, Name, Musical_ID, Character, Duration, age
FROM actor_old;

-- 4. Drop old table
DROP TABLE actor_old;