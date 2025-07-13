import csv
import json

# Step 1: Read the roadmap file
def read_roadmap(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

# Step 2: Convert to JSON for uTemplate
def convert_to_json(data):
    return json.dumps(data, indent=4)

# Example usage
roadmap_data = read_roadmap('roadmap.csv')
json_data = convert_to_json(roadmap_data)

# Save JSON data to a file
with open('roadmap_data.json', 'w') as json_file:
    json_file.write(json_data)