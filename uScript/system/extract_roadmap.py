import pandas as pd

# Load the roadmap file
roadmap_file = 'path/to/roadmap_file.csv'
roadmap_data = pd.read_csv(roadmap_file)

# Extract relevant columns
structured_data = roadmap_data[['Milestone', 'Deadline', 'Task', 'Responsible Party']]

# Example of transforming data into uTemplate format
def generate_utemplate(data):
    template = ""
    for row in data:
        template += f"- Milestone: {row['Milestone']}\n"
        template += f"  Deadline: {row['Deadline']}\n"
        template += f"  Task: {row['Task']}\n"
        template += f"  Responsible: {row['Responsible Party']}\n"
    return template

# Generate the uTemplate output
utemplate_output = generate_utemplate(structured_data.to_dict(orient='records'))
print(utemplate_output)