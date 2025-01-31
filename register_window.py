"""
Handles the Register Window
"""
import sqlite3
import bcrypt

# pylint: disable=no-name-in-module
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from calculate import create_tables, create_user

db_file = "data.db"

class RegisterWindow(QMainWindow):
    """
    A window for user registration.
    This class creates a user interface for registering a new user, including
    input fields for username, password, sex, age, height, and activity level.
    It also handles the registration logic and transitions to the main window
    or login window as needed.
    Methods
    -------
    __init__():
        Initializes the RegisterWindow.
    init_ui():
        Sets up the user interface.
    toggle_password_visibility():
        Toggles the visibility of the password input field.
    register():
        Handles the registration process.
    open_login_window():
        Opens the login window.
    open_main_window(user_id, username):
        Opens the main window with the given user ID and username.
    """

    def __init__(self):
        """
        Initializes the main window for the Register application.
        This constructor sets up the window title, icon, size, and initializes
        the SQLite database connection. It also calls the method to create
        necessary tables and initializes the UI components.
        Parameters:
        None
        Returns:
        None
        """

        super().__init__()
        self.setWindowTitle("Register")
        self.setWindowIcon(QtGui.QIcon("Fire.svg"))
        self.setFixedSize(350, 700)

        self.conn = sqlite3.connect(db_file)
        create_tables(self.conn)

        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface for the registration form.
        This method sets up the central widget, layout, and various input fields
        including username, password, sex, age, height, and activity level. It also
        includes a register button and a login section for users who already have an account.
        Parameters:
        None
        Returns:
        None
        """

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.central_widget.setStyleSheet(
            """
            font-family: Tahoma,Arial, sans-serif;
            margin: 0px 10px 0px 10px;
        """
        )

        self.signup_label = QLabel("Create your account")
        self.signup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.signup_label.setStyleSheet(
            """
            padding: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #ccc;
            margin-bottom: 20px;
        """
        )
        self.layout.addWidget(self.signup_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(
            """
            padding: 10px;
            margin-bottom:10px;
            border: 1px solid #333;
            border-radius: 5px;
        """
        )
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(
            """
            padding: 10px;
            margin-bottom:5px;
            border: 1px solid #333;
            border-radius: 5px;
        """
        )
        self.layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.setStyleSheet(
            """
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #333;
        """
        )
        self.show_password_checkbox.stateChanged.connect(
            self.toggle_password_visibility
        )
        self.layout.addWidget(self.show_password_checkbox)

        self.sex_layout = QHBoxLayout()
        self.sex_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.sex_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(self.sex_layout)

        self.sex_label = QLabel("Sex:")
        self.sex_label.setStyleSheet(
            """
            padding: 0 0 10px 0;
            margin-bottom:10px;
            color: #ccc;
            font-weight: bold;
        """
        )
        self.sex_layout.addWidget(self.sex_label)

        self.male_radio = QRadioButton("Male")
        self.male_radio.setStyleSheet(
            """
            color: #ccc;
            padding: 0 0 10px 0;
            margin-bottom:10px;
        """
        )
        self.sex_layout.addWidget(self.male_radio)

        self.female_radio = QRadioButton("Female")
        self.female_radio.setStyleSheet(
            """
            color: #ccc;
            padding: 0 0 10px 0;
            margin-bottom:10px;
        """
        )
        self.sex_layout.addWidget(self.female_radio)

        self.sex_group = QButtonGroup(self)
        self.sex_group.addButton(self.male_radio)
        self.sex_group.addButton(self.female_radio)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Age")
        self.age_input.setStyleSheet(
            """
            padding: 10px;
            margin-bottom:10px;
            border: 1px solid #333;
            border-radius: 5px;
        """
        )
        self.layout.addWidget(self.age_input)

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height (in)")
        self.height_input.setStyleSheet(
            """
            padding: 10px;
            margin-bottom:10px;
            border: 1px solid #333;
            border-radius: 5px;
        """
        )
        self.layout.addWidget(self.height_input)

        self.activity_layout = QHBoxLayout()
        self.activity_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.activity_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.addLayout(self.activity_layout)

        self.activity_label = QLabel("Activity Level:")
        self.activity_label.setStyleSheet(
            """
            padding: 0 0 10px 10px;
            margin: 10px 0 20px 0;
            color: #ccc;
            font-weight: bold;
        """
        )
        self.activity_layout.addWidget(self.activity_label)
        self.activity_dropdown = QComboBox(self)
        self.activity_dropdown.addItem("Sedentary (little or no exercise)")
        self.activity_dropdown.addItem(
            "Lightly active (light exercise/sports 1-3 days/week)"
        )
        self.activity_dropdown.addItem(
            "Moderately active (moderate exercise/sports 3-5 days/week)"
        )
        self.activity_dropdown.addItem(
            "Very active (hard exercise/sports 6-7 days a week)"
        )
        self.activity_dropdown.addItem(
            "Extremely active (very hard exercise & physical job or 2x training)"
        )
        self.activity_layout.addWidget(self.activity_dropdown)
        self.activity_dropdown.setStyleSheet(
            """
            padding: 10px;
            margin-bottom:20px;
            color: #ccc;
        """
        )

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px;
                background-color: #FF5349;
                font-weight: bold;
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                margin-bottom:20px;
            }
            QPushButton::hover {
                background-color: #ed2115;
            }
            QPushButton::pressed {
                background-color: #c8170d;
            }
        """
        )
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

        # Create a horizontal layout for the "Already have an account? Login"
        # section
        self.login_layout = QHBoxLayout()
        self.login_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.login_layout.setSpacing(5)
        self.layout.addLayout(self.login_layout)

        self.already_user_label = QLabel("Already have an account?")
        self.already_user_label.setStyleSheet(
            """
            font-size: 12px;
            color: #ccc;
            margin: 0;
            padding: 0 0 20px 0;
        """
        )
        self.login_layout.addWidget(self.already_user_label)

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet(
            """
            QPushButton {
                background: none;
                color: #FF5349;
                border: none;
                font-size: 12px;
                text-decoration: underline;
                margin: 0;
                padding: 0 0 20px 0;
            }
            QPushButton:hover {
                color: #c8170d;
            }
            QPushButton:pressed {
                color: #a5170f;
            }
        """
        )
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.open_login_window)
        self.login_layout.addWidget(self.login_button)

    def toggle_password_visibility(self):
        """
        Toggles the visibility of the password input field based on the state of the
        show password checkbox.
        Parameters:
        None
        Returns:
        None
        """

        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def register(self):
        """
        Registers a new user with the provided information from the input fields.
        Parameters:
        self (object): The instance of the class containing the method.
        username (str): The username input by the user.
        password (str): The password input by the user.
        sex (str): The sex of the user, either "Male" or "Female".
        age (str): The age input by the user.
        height (str): The height input by the user.
        Returns:
        None
        """

        username = self.username_input.text().lower()
        password = self.password_input.text()
        sex = (
            "Male"
            if self.male_radio.isChecked()
            else "Female" if self.female_radio.isChecked() else None
        )
        age = self.age_input.text()
        height = self.height_input.text()

        if not username or not password or not sex or not age or not height:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user_id = create_user(
            self.conn,
            username,
            hashed_password,
            sex,
            int(age),
            int(height),
            "sedentary",
        )  # Default activity level

        self.open_main_window(user_id, username)

    def open_login_window(self):
        """
        Opens the login window and closes the current window.
        This method initializes a new instance of the LoginWindow class,
        displays it, and then closes the current window.
        Parameters:
        None
        Returns:
        None
        """
        from login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def open_main_window(self, user_id, username):
        """
        Opens the main window of the application.
        Args:
            user_id (int): The ID of the user.
            username (str): The username of the user.
        Returns:
            None
        """
        
        from main import MainWindow
        self.main_window = MainWindow(self.conn, user_id, username)
        self.main_window.show()
        self.close()
