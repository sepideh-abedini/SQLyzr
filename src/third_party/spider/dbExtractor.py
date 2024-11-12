import os
import json
# Get the list of all files and directories
path = "ConcatDB"
dir_list = os.listdir(path)
print("Files and directories in '", path, "' :")

print(len(dir_list))

db_list = []

for db_file in dir_list:
        db_entry = {
            "column_names": [],
            "db_id": db_file,
            "table_names": []
        }
        db_list.append(db_entry)

# Convert the list to JSON
json_output = json.dumps(db_list, indent=4)

# Write the JSON data to a file
with open('extractedNames.json', 'w') as json_file:
    json_file.write(json_output)

