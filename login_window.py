"""
Handles the Login Window
"""
import sqlite3
import bcrypt

# pylint: disable=no-name-in-module
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from register_window import RegisterWindow
from calculate import create_tables, get_user

db_file = "data.db"

class LoginWindow(QMainWindow):
    """
    A class to represent the login window of the application.
    Methods
    -------
    __init__():
        Initializes the login window, sets up the UI, and connects to the database.
    initUI():
        Sets up the user interface components for the login window.
    toggle_password_visibility():
        Toggles the visibility of the password input field.
    login():
        Authenticates the user by checking the entered credentials against the database.
    open_register_window():
        Opens the registration window for new users.
    open_main_window(user_id, username):
        Opens the main application window after successful login.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(350, 500)
        self.setWindowIcon(QtGui.QIcon("Fire.svg"))

        self.conn = sqlite3.connect(db_file)
        create_tables(self.conn)

        self.register_window = None
        self.main_window = None
        self.init_ui()

    def init_ui(self):
        """
        Initializes UI
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

        self.signin_label = QLabel("Sign in to CalCulator")
        self.signin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.signin_label.setStyleSheet(
            """
            padding: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            color: #ccc;
            margin-bottom: 20px;
        """
        )
        self.layout.addWidget(self.signin_label)

        self.warning_label = QLabel("")
        self.warning_label.setFixedHeight(60)
        self.warning_label.setStyleSheet(
            """
            padding: 10px;
            background-color: #ffe1df;
            color: #ff6d64;
            font-weight: bold;
            border: 1px solid #ff6d64;
            border-radius: 5px;
            margin: 0 10px 20px 10px
        """
        )
        self.warning_label.setVisible(False)
        self.layout.addWidget(self.warning_label)

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
             margin-bottom:20px;
        """
        )
        self.show_password_checkbox.stateChanged.connect(
            self.toggle_password_visibility
        )
        self.layout.addWidget(self.show_password_checkbox)

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet(
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
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.register_layout = QHBoxLayout()
        self.register_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.register_layout.setSpacing(5)
        self.layout.addLayout(self.register_layout)

        self.new_user_label = QLabel("Don't have an account?")
        self.new_user_label.setStyleSheet(
            """
            color: #ccc;
            font-size: 12px;
            padding: 0;
            margin:0 0 20px 0;
        """
        )
        self.register_layout.addWidget(self.new_user_label)

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet(
            """
            QPushButton {
                background: none;
                color: #FF5349;
                border: none;
                font-size: 12px;
                text-decoration: underline;
                padding: 0;
                margin:0 0 20px 0;
            }
            QPushButton::hover {
                color: #c8170d;
            }
            QPushButton::pressed {
                color: #a5170f;
            }
        """
        )
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.clicked.connect(self.open_register_window)
        self.register_layout.addWidget(self.register_button)

    def toggle_password_visibility(self):
        """
        Toggles the visibility of the password input field based on the state of the
        show_password_checkbox.
        If the show_password_checkbox is checked, the password input field will display
        the password in plain text.
        If the show_password_checkbox is unchecked, the password input field will mask
        the password.
        Returns:
            None
        """

        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def login(self):
        """
        Authenticates the user by verifying the provided username and password.
        Parameters:
        self (object): The instance of the class containing the login method.
        Returns:
        None
        """

        username = self.username_input.text().lower()
        password = self.password_input.text()

        cursor = self.conn.execute(
            "SELECT password FROM users WHERE LOWER(username) = ?", (username,)
        )
        stored_hash = cursor.fetchone()

        if stored_hash and bcrypt.checkpw(
            password.encode("utf-8"), stored_hash[0].encode("utf-8")
        ):
            user_id = get_user(self.conn, username, stored_hash[0])
            self.open_main_window(user_id, username)
        else:
            self.warning_label.setText("Invalid credentials. Please try again.")
            self.warning_label.setVisible(True)

    def open_register_window(self):
        """
        Opens the register window and closes the current window.
        This method creates an instance of the RegisterWindow class, displays it,
        and then closes the current window.
        Parameters:
        None
        Returns:
        None
        """

        self.register_window = RegisterWindow()
        self.register_window.show()
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
