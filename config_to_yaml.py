import yaml
import sys
import re

# Regular expressions for parsing
ALLOWED_NAME_PATTERN = r"[A-Z_]+"
ALLOWED_OPERATIONS_EXPRESSION = r"\+|\-|\*|/"
CONST_INITIALIZATION_EXPRESSION = rf"const ({ALLOWED_NAME_PATTERN}) = ([\d\.]+);"  # Allow floats
DICT_OPEN_EXPRESSION = rf"({ALLOWED_NAME_PATTERN}) : \{{"
DICT_CLOSE_EXPRESSION = r"}"
KEY_VALUE_EXPRESSION = rf"({ALLOWED_NAME_PATTERN}) : ([\d\w#()\s$[\]+\-/*\.]+)"  # Allow floats
ARRAY_EXPRESSION = r"#\((.*?)\)"
ARITHMETIC_EXPRESSION = rf"\$\[({ALLOWED_OPERATIONS_EXPRESSION}) ({ALLOWED_NAME_PATTERN}|\d+|\d+\.\d+) ({ALLOWED_NAME_PATTERN}|\d+|\d+\.\d+)\]"

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
            return parse_block(file)
    except FileNotFoundError:
        print(f"Error: The file '{config_file_path}' does not exist.")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def parse_block(file):
    global constants
    config_dict = {}

    for line in file:
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Constant initialization
        const_match = re.match(CONST_INITIALIZATION_EXPRESSION, line)
        if const_match:
            const_name, const_value = const_match.groups()
            constants[const_name] = convert_to_number(const_value)  # Store as appropriate type
            continue

        # Dictionary opening line
        dict_open_match = re.match(DICT_OPEN_EXPRESSION, line)
        if dict_open_match:
            current_key = dict_open_match.group(1)
            config_dict[current_key] = parse_block(file)
            continue

        # Dictionary closing line
        if re.match(DICT_CLOSE_EXPRESSION, line):
            return config_dict

        # Key-value pair initialization
        key_value_match = re.match(KEY_VALUE_EXPRESSION, line)
        if key_value_match:
            key_name, value = key_value_match.groups()

            # Check for arithmetic expression
            arithmetic_match = re.match(ARITHMETIC_EXPRESSION, value)
            if arithmetic_match:
                operator, operand1, operand2 = arithmetic_match.groups()
                config_dict[key_name] = evaluate_expression(operator, operand1, operand2)
            # Check for array syntax
            elif re.match(ARRAY_EXPRESSION, value):
                array_values = parse_array(value)
                config_dict[key_name] = array_values
            elif value in constants:
                config_dict[key_name] = constants[value]  # Use constant value if referenced
            else:
                config_dict[key_name] = convert_to_number(value)  # Convert to appropriate type

    return config_dict

def convert_to_number(value):
    """Convert a string value to an int or float, depending on its format."""
    try:
        num = float(value)
        if num.is_integer():  # Check if it's a whole number
            return int(num)  # Store as int if there's no decimal part
        return num  # Store as float otherwise
    except ValueError:
        return value  # Return the original value if it cannot be converted

def evaluate_expression(operator, operand1, operand2):
    # Convert operands to appropriate types
    operand1 = constants[operand1] if operand1 in constants else convert_to_number(operand1)
    operand2 = constants[operand2] if operand2 in constants else convert_to_number(operand2)

    # Perform the arithmetic operation
    if operator == "+":
        return operand1 + operand2
    elif operator == "-":
        return operand1 - operand2
    elif operator == "*":
        return operand1 * operand2
    elif operator == "/":
        return operand1 / operand2  # Use float division for generality

def parse_array(value):
    # Extract the content inside #()
    inner_values = re.match(ARRAY_EXPRESSION, value).group(1)
    # Split by whitespace and convert to appropriate types
    return [convert_to_number(v) for v in inner_values.split()]

def output_to_yaml(constants_dict, config_dict):
    # Merge constants and configuration into a single output
    combined_output = {**constants_dict, **config_dict}
    
    yaml_output = yaml.dump(combined_output, default_flow_style=False)
    return yaml_output

if __name__ == "__main__":
    main()
