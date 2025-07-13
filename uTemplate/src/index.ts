     import pandas as pd

     # Load the roadmap file
     roadmap_data = pd.read_csv('roadmap_file.csv')  # Adjust based on file format

     # Extract relevant columns
     extracted_data = roadmap_data[['Milestone', 'Timeline', 'Task', 'Responsible Party']]