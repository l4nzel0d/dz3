import unittest
from io import StringIO
import yaml
import os
from config_to_yaml import convert_to_number, evaluate_expression, parse_array, parse_block, parse_config_file, output_to_yaml, constants

class TestConfigToYaml(unittest.TestCase):

    def test_convert_to_number(self):
        # Test integer conversion
        self.assertEqual(convert_to_number("10"), 10)
        # Test float conversion
        self.assertEqual(convert_to_number("10.5"), 10.5)
        # Test string fallback for non-numeric values
        self.assertEqual(convert_to_number("non_numeric"), "non_numeric")

    def test_evaluate_expression(self):
        # Setup constants for testing
        constants["CONSTA"] = 10
        constants["CONSTB"] = 5

        # Test addition
        self.assertEqual(evaluate_expression("+", "CONSTA", "CONSTB"), 15)
        # Test subtraction
        self.assertEqual(evaluate_expression("-", "CONSTA", "CONSTB"), 5)
        # Test multiplication
        self.assertEqual(evaluate_expression("*", "CONSTA", "CONSTB"), 50)
        # Test division
        self.assertEqual(evaluate_expression("/", "CONSTA", "CONSTB"), 2)
    
    def test_parse_array(self):
        # Test array parsing
        array_str = "#( #( 1 2 ) #( 3 4 ) 5 6 )"
        self.assertEqual(parse_array(array_str), [[1, 2], [3, 4], 5, 6])

    def test_parse_config_file(self):
        # Sample configuration text with constants and arithmetic
        config_text = """
        const CONSTA = 10;
        const CONSTB = 5;
        
        SAMPLEDICT : {
            VALUEA : CONSTA
            VALUEB : $[+ CONSTA CONSTB]
            ARRAY : #( 1 2 3 )
        }
        """
        
        # Mocking file read by using StringIO
        config_file = StringIO(config_text)
        
        # Expected output dictionary
        expected_output = {
            "SAMPLEDICT": {
                "VALUEA": 10,
                "VALUEB": 15,  # 10 + 5
                "ARRAY": [1, 2, 3]
            }
        }
        
        parsed_config = parse_block(config_file)
        self.assertEqual(parsed_config, expected_output)

    def test_output_to_yaml(self):
        # Create a sample config dictionary that complies with the key restrictions
        constants_dict = {"CONST": 10}
        config_dict = {
            "SAMPLEDICT": {
                "VALUE": 10,
                "ARRAY": [1, 2, 3]
            }
        }
        
        # Specify a temporary file path for testing
        temp_file_path = "test_output.yaml"
        
        try:
            # Call output_to_yaml with the temporary file path
            output_to_yaml(constants_dict, config_dict, temp_file_path)
            
            # Read back the YAML output and validate
            with open(temp_file_path, 'r') as file:
                output_yaml = yaml.safe_load(file)
            
            expected_output = {
                "CONST": 10,
                "SAMPLEDICT": {
                    "VALUE": 10,
                    "ARRAY": [1, 2, 3]
                }
            }
            
            self.assertEqual(output_yaml, expected_output)
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

if __name__ == "__main__":
    unittest.main()