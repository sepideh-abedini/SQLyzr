CUSTOM_PROMPT = """
I'll give you a natural language question and the schema of the underlying database.
Your task is to generate a SQL query that answers the question based on the database schema.
Schema is given in YAML format and it has a key for each table. 
Within eacy table, we have keys for each column with the value representing the type of the column.
For columns that are foreign keys, it also includes the name of the table and column that the foreign key is pointing to.

Here are some examples:
Example 1:
DB Schema:
    tags:
      id: integer
      index: integer
      tag: text
    torrents:
      artist: text
      groupid: integer
      groupname: text
      groupyear: integer
      id: integer
      releasetype: text
      totalsnatched: integer

NL Question: What is the release title of the single that was released by Ron Hunt in 1979 that was downloaded 239 times? release title refers to groupName; Ron Hunt is an artist; groupYear = 1979; releaseType = 'single'; downloaded 239 times refer to totalSnatched = 239;
SQL: SELECT groupName FROM torrents WHERE artist LIKE 'ron hunt & ronnie g & the sm crew' AND groupYear = 1979 AND releaseType LIKE 'single' AND totalSnatched = 239

Example 2:
DB Schema:
    tags:
      id: integer
      index: integer
      tag: text
    torrents:
      artist: text
      groupid: integer
      groupname: text
      groupyear: integer
      id: integer
      releasetype: text
      totalsnatched: integer
NL Question: How many times was the album released by blowfly in 1980 downloaded? blowfly is an artist; groupYear = 1980; album refers to releaseType; downloaded refers to totalSnatched;
SQL: SELECT totalSnatched FROM torrents WHERE artist LIKE 'blowfly' AND groupYear = 1980

Now, generate a SQL query for the following question and database schema:
NL Question: {question}
DB Schema: {schema}
Your output should only contain the SQL query nothing else is permitted.
"""
