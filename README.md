# CalCulator

CalCulator is a PyQt6-based GUI application for calorie and weight data tracking. It allows users to create accounts, log in, enter their weight and calorie data, view trends, and calculate their caloric needs.

<img alt="Trends screen of the CalCulator app"  src=https://github.com/user-attachments/assets/08c3fcb4-828c-40e6-aff5-7f78314cd6f0 title="CalCulator, Trends screen" width=70%/>


## Features

- User registration and login
- Enter weight and calorie data
- View data in tabular format
- Export and import data to/from CSV files
- Calculate caloric needs based on user data
- View weight trends over different periods

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/calculator.git
   cd calculator
   ```

2. Create a virtual environment and activate it:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```sh
   python main.py
   ```

2. Register a new user or log in with an existing account.

3. Use the application to enter your weight and calorie data, view trends, and calculate your caloric needs.

## Project Structure

- [calculate.py](http://_vscodecontentref_/0): Contains functions for database operations, data import/export, and caloric needs calculation.
- [main.py](http://_vscodecontentref_/1): Contains the PyQt6-based GUI application.
- [login_window.py](http://_vscodecontentref_/2): Contains the login window class and related functionalities.
- [register_window.py](http://_vscodecontentref_/3): Contains the registration window class and related functionalities.
- [README.md](http://_vscodecontentref_/4): Provides an overview of the project, setup instructions, and usage guidelines.

## Dependencies

- PyQt6
- SQLite3
- NumPy
- Pandas
- Bcrypt
- Matplotlib

## License

This project is licensed under the MIT License. See the LICENSE file for details.
