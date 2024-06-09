# Data Parser

Data Parser is an application developed using PyQt5 for parsing data from a website and displaying it in a user-friendly interface.

## Description

The application allows the user to select the parsing mode (normal or asynchronous), input the category URL, and then perform parsing. The retrieved data is displayed in tables, showing the selection ID, product count, and timestamp. The user can also view products associated with the selection and sorting functionalities.

## Installation

1. Install the required dependencies by running the following command:
```
pip install -r requirements.txt
```
2. Launch the application by executing the following command:
```
python main.py
```

## Usage

1. Enter the category URL in the "Category URL" field.
2. Click the "Parse Normally" button to initiate normal parsing or "Parse Asynchronously" for asynchronous parsing.
3. Once the parsing is complete, the data will be displayed in tables.
4. To view products associated with the selected selection, click on the corresponding row in the selections table.
5. To sort data by price or alphabetical order, click on the respective column in the products table.

## Authors

- **Ilya Kukharchuk** - *Java Software Engineer*

   - [LinkedIn Profile](https://linkedin.com/in/ilya-kukharchuk)
   - Email: iliakuharchuk@mail.ru


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
