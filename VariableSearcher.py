import os
import fnmatch
import csv
import time


class VariableSearcher:
    def __init__(self, directory, file_pattern, exclude_filetypes=None, exclude_locations=None):
        self.directory = directory
        self.file_pattern = file_pattern
        self.exclude_filetypes = exclude_filetypes if exclude_filetypes else []
        self.exclude_locations = exclude_locations if exclude_locations else []

    def extract_variables_from_csv(self, file_path, column_name):
        variables = set()  # Use a set to ensure uniqueness
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    variable_name = row.get(column_name)
                    if variable_name:
                        variables.add(variable_name)  # Add to the set
        except Exception as e:
            print(f"Error reading CSV file {file_path}: {e}")
        
        return list(variables)  # Convert back to list if needed

    def _search_variables_in_files(self, variables):
        variable_file_map = {var: [] for var in variables}
        start_time = time.time()

        try:
            for root, _, filenames in os.walk(self.directory):
                if any(exclude in root for exclude in self.exclude_locations):
                    continue  # Skip excluded locations

                print(f"Currently in directory: {root}")  # Debugging output
                for filename in fnmatch.filter(filenames, self.file_pattern):
                    if any(filename.endswith(ext) for ext in self.exclude_filetypes):
                        continue  # Skip excluded filetypes
                    file_path = os.path.join(root, filename)
                    print(f"Checking file: {file_path}")  # Debugging output
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            for line_number, line in enumerate(file, 1):
                                for var in variables:
                                    if var.lower() in line.lower():
                                        variable_file_map[var].append(
                                            (file_path, line_number)
                                        )
                                        print(
                                            f"Variable '{var}' found in "
                                            f"{file_path} on line {line_number}"
                                        )
                    except Exception as e:
                        print(f"Could not read file {file_path}: {e}")
        except Exception as e:
            print(f"Error traversing directory {self.directory}: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time taken: {total_time:.2f} seconds")
        
        return variable_file_map

    def search_by_name(self, names):
        return self._search_variables_in_files(names)

    def search_by_id(self, ids):
        return self._search_variables_in_files(ids)

    def save_results_to_csv(self, results, output_file):
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Variable', 'File Path', 'Line Number'])
                for var, occurrences in results.items():
                    for file_path, line_number in occurrences:
                        writer.writerow([var, file_path, line_number])
            print(f"Results successfully saved to {output_file}")
        except Exception as e:
            print(f"Error saving results to {output_file}: {e}")


# Example usage
directory_to_search = '/path/to/your/directory'
file_pattern = '*.*'  # You can change this to specific file types like '*.py', '*.txt', etc.
exclude_filetypes = ['.dat']  # Example exclusion list
exclude_locations = ['/path/to/exclude1', '/path/to/exclude2']  # Example locations to exclude

# Instantiate the searcher
searcher = VariableSearcher(directory_to_search, file_pattern, exclude_filetypes, exclude_locations)

# Extract names and IDs from the CSV file
csv_file_path = '/path/to/your/csv_file.csv'
name_column = 'Name'  # Column for names
id_column = 'ID'  # Column for IDs

names_to_search = searcher.extract_variables_from_csv(csv_file_path, name_column)
ids_to_search = searcher.extract_variables_from_csv(csv_file_path, id_column)

# Perform the search by name
result_by_name = searcher.search_by_name(names_to_search)

# Perform the search by ID
result_by_id = searcher.search_by_id(ids_to_search)

# Save the results to CSV files
output_file_name = 'search_results_by_name.csv'
output_file_id = 'search_results_by_id.csv'

searcher.save_results_to_csv(result_by_name, output_file_name)
searcher.save_results_to_csv(result_by_id, output_file_id)
