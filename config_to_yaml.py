import yaml
import sys
import re

# Regular expressions for parsing
ALLOWED_NAME_PATTERN = r"[A-Z_]+"  # Allowed names for constants and keys
CONST_INITIALIZATION_EXPRESSION = rf"const ({ALLOWED_NAME_PATTERN}) = (\d+);"
DICT_OPEN_EXPRESSION = rf"({ALLOWED_NAME_PATTERN}) : \{{"
DICT_CLOSE_EXPRESSION = r"}"
KEY_VALUE_EXPRESSION = rf"({ALLOWED_NAME_PATTERN}) : ([\d\w#()\s]+)"  # Allows arrays as values in key-value pairs
ARRAY_EXPRESSION = r"#\((.*?)\)"  # Matches array syntax

# Global dictionary to store constants
constants = {}

def main():
    if len(sys.argv) != 2:
        print("Usage: python config_to_yaml.py <config_file_path>")
        return

    config_file_path = sys.argv[1]
    config_dict = parse_config_file(config_file_path)
    print(output_to_yaml(constants, config_dict))

def parse_config_file(config_file_path):
    try:
        with open(config_file_path, 'r') as file:
            return parse_block(file)  # Directly return the result of parse_block
    except FileNotFoundError:
        print(f"Error: The file '{config_file_path}' does not exist.")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def parse_block(file):
    global constants  # Access the global constants dictionary
    config_dict = {}

    for line in file:
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Check for constant initialization at the top level
        const_match = re.match(CONST_INITIALIZATION_EXPRESSION, line)
        if const_match:
            const_name, const_value = const_match.groups()
            constants[const_name] = int(const_value)  # Store in the global constants
            continue  # Skip to the next line

        # Check for a dictionary opening line
        dict_open_match = re.match(DICT_OPEN_EXPRESSION, line)
        if dict_open_match:
            current_key = dict_open_match.group(1)
            # Recursively parse the nested block
            config_dict[current_key] = parse_block(file)
            continue

        # Check for a dictionary closing line
        if re.match(DICT_CLOSE_EXPRESSION, line):
            return config_dict  # End of the current block

        # Check for key-value pair initialization
        key_value_match = re.match(KEY_VALUE_EXPRESSION, line)
        if key_value_match:
            key_name, value = key_value_match.groups()
            
            # Check if value is an array
            array_match = re.match(ARRAY_EXPRESSION, value)
            if array_match:
                # Parse and store array as a list of integers
                config_dict[key_name] = parse_array_values(array_match.group(1))
            elif value in constants:
                # Use constant value if referenced
                config_dict[key_name] = constants[value]
            else:
                # Convert to int if it's a number
                config_dict[key_name] = int(value) if value.isdigit() else value

    return config_dict

def parse_array_values(values_str):
    # Split the values based on spaces and convert them to integers
    values = [int(val) for val in values_str.split() if val.isdigit()]
    return values

def output_to_yaml(constants_dict, config_dict):
    # Merge with config_dict
    combined_output = {**constants_dict, **config_dict}
    
    yaml_output = yaml.dump(combined_output, default_flow_style=False)
    return yaml_output

if __name__ == "__main__":
    main()
