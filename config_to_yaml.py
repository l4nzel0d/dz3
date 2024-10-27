import yaml
import sys
import re

# Regular expressions for parsing
ALLOWED_NAME_PATTERN = r"[A-Z_]+"
ALLOWED_OPERATIONS_EXPRESSION = r"\+|\-|\*|/"
CONST_INITIALIZATION_EXPRESSION = rf"const ({ALLOWED_NAME_PATTERN}) = (\d+);"
DICT_OPEN_EXPRESSION = rf"({ALLOWED_NAME_PATTERN}) : \{{"
DICT_CLOSE_EXPRESSION = r"}"
KEY_VALUE_EXPRESSION = rf"({ALLOWED_NAME_PATTERN}) : ([\d\w#()\s$[\]+\-/*]+)"
ARRAY_EXPRESSION = r"#\((.*?)\)"
ARITHMETIC_EXPRESSION = rf"\$\[({ALLOWED_OPERATIONS_EXPRESSION}) ({ALLOWED_NAME_PATTERN}|\d+) ({ALLOWED_NAME_PATTERN}|\d+)\]"

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
            constants[const_name] = int(const_value)
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
                config_dict[key_name] = int(value)  # Convert to int if it's a number

    return config_dict

def evaluate_expression(operator, operand1, operand2):
    # Convert operands to integers, resolving constants if needed
    operand1 = constants[operand1] if operand1 in constants else int(operand1)
    operand2 = constants[operand2] if operand2 in constants else int(operand2)

    # Perform the arithmetic operation
    if operator == "+":
        return operand1 + operand2
    elif operator == "-":
        return operand1 - operand2
    elif operator == "*":
        return operand1 * operand2
    elif operator == "/":
        return operand1 // operand2  # Using integer division for simplicity

def parse_array(value):
    # Extract the content inside #()
    inner_values = re.match(ARRAY_EXPRESSION, value).group(1)
    # Split by whitespace and convert to integers
    return [int(v) for v in inner_values.split()]

def output_to_yaml(constants_dict, config_dict):
    # Merge constants and configuration into a single output
    combined_output = {**constants_dict, **config_dict}
    
    yaml_output = yaml.dump(combined_output, default_flow_style=False)
    return yaml_output

if __name__ == "__main__":
    main()
