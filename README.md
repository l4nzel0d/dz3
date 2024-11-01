# Custom Config Language CLI Tool

This repository contains a command-line tool for parsing and converting text written in a custom configuration language. The tool reads a configuration file specified by the user, interprets the custom syntax, and outputs the parsed content in a specified format.

## Features

- Command-line interface for ease of use
- Parses a custom configuration language with defined syntax
- Supports conversion of configuration data to a structured output format (YAML)
- Customizable rules for parsing arithmetic expressions, constants, arrays, and dictionaries

## Prerequisites

- Python 3.x
- Required Python packages:
  - `sys` and `argparse` for CLI argument parsing
  - `re` for regular expression parsing
  - `yaml` (PyYAML) for YAML output support

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/l4nzel0d/dz3
   cd dz3
   ```

2. Install required Python packages:
   ```bash
   pip install pyyaml
   ```

## Configuration Syntax

The custom configuration language supports several features:

- **Constant Initialization**: Define constants that can be referenced throughout the configuration.
- **Dictionaries**: Group key-value pairs into nested structures.
- **Arrays**: Represent lists of values.
- **Arithmetic Expressions**: Supports basic arithmetic operations (+, -, *, /) between constants and literals.

## Usage

To parse and convert a configuration file, specify the file path as a command-line argument:

```bash
python config_to_output.py <config_file_path>
```

### Example Input

Given a configuration file `config.txt` with content:

```plaintext
const DEFAULTTIMEOUT = 20;

APPLICATIONSETTINGS : {
    LOGLEVEL : #( 1 2 3 ),
    MAXRETRIES : 5,
    TIMEOUT : $[+ DEFAULTTIMEOUT 10],
    DATABASESETTINGS : {
        HOST : 127,
        PORT : 3306
    }
}
```

Running the tool generates an output file (e.g., `output.yaml`) with:

```yaml
APPLICATIONSETTINGS:
  DATABASESETTINGS:
    HOST: 127
    PORT: 3306
  LOGLEVEL:
  - 1
  - 2
  - 3
  MAXRETRIES: 5
  TIMEOUT: 30
DEFAULTTIMEOUT: 20
```

## Testing

Unit tests are provided to verify functionality. Run them as follows:

```bash
python -m unittest test_config_to_output.py
```

## Author

Created by **l4nzel0d** aka **Boris Vasilyev**
