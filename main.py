"""
This module provides a PyQt6-based GUI application for calorie and weight data tracking
"""
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# pylint: disable=no-name-in-module
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QGridLayout,
    QTableWidgetItem,
    QTableWidget,
    QTabWidget,
    QCalendarWidget,
    QFormLayout,
    QGraphicsOpacityEffect,
    QHeaderView,
)
from PyQt6 import QtGui
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from calculate import (
    calculate_caloric_needs,
    import_csv_to_db,
    export_db_to_csv,
    submit_updated_info,
    weight_entry,
    get_view_data,
    get_trend_data,
)

PERIOD_DAYS = {
    "1 week": 7,
    "1 month": 30,
    "3 months": 90,
    "6 months": 180,
    "1 year": 365,
}

class MainWindow(QMainWindow):
    """
    Main application window for the CalCulator application.
    This class represents the main window of the application, providing the user interface
    for various functionalities such as entering data, viewing data, calculating caloric needs,
    and updating user information. It sets up the main layout, styles, and connects UI components
    to their respective methods.
    Attributes:
        conn (sqlite3.Connection): Database connection object.
        user_id (int): ID of the current user.
        username (str): Username of the current user.
    """
    def __init__(self, conn, user_id, username):
        super().__init__()
        self.setWindowTitle("CalCulator")
        self.setWindowIcon(QtGui.QIcon("Fire.svg"))
        self.setFixedSize(1200, 800)

        self.conn = conn
        self.user_id = user_id
        self.username = username

        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface for the main window.
        This method sets up the central widget, layouts, and various UI components
        including buttons, labels, and separators. It also applies styles to the widgets
        and connects button signals to their respective slots.
        """
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("font-family: Tahoma,Arial, sans-serif;")

        self.layout = QHBoxLayout()  # Main layout

        self.side_widget = QWidget()  # Left sidebar
        self.side_widget.setObjectName("side_widget")
        self.side_widget.setFixedWidth(300)  # Set fixed width for left sidebar
        self.side_layout = QVBoxLayout()  # Left sidebar layout
        self.side_widget.setLayout(self.side_layout)

        self.central_widget.setStyleSheet(
            """
            QWidget#side_widget, QWidget#info_widget {
            background-color: #2d2d2d;
            border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: 1px solid #FF5349;
                font-weight: bold;
                color: #ff5349;

                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton::hover {
                background-color: #ed2115;
                border: none;
                color: #fff;
            }
            QPushButton::pressed {
                background-color: #c8170d;
                border: none;
                color: #fff;
            }
            QPushButton#log_out_btn {
                padding: 10px;
                background-color:#FF5349;
                font-weight: bold;
                color: #fff;

                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton#log_out_btn::hover {
                background-color: #ed2115;
                border: none;
                color: #fff;
            }
            QPushButton#log_out_btn::pressed {
                background-color: #c8170d;
                border: none;
                color: #fff;
            }

            QPushButton#top_button{
                margin-top: 10px;
            }

            QLabel#welcome_back_label {
                padding: 10px 0 0 0;
                font-size: 24px;
                font-weight: bold;
                color: #ccc;
                margin-bottom: 10px;
            }
        """
        )

        self.info_widget = QWidget()  # Right info display
        self.info_widget.setObjectName("info_widget")
        self.info_widget.setFixedWidth(876)
        self.info_layout = QGridLayout()  # Right info display layout
        self.info_widget.setLayout(self.info_layout)

        self.layout.addWidget(self.side_widget)
        self.layout.addWidget(self.info_widget)
        self.central_widget.setLayout(self.layout)  # Set main layout

        self.welcome_back_label = QLabel(f"Welcome back, {self.username.capitalize()}!")
        self.welcome_back_label.setObjectName("welcome_back_label")
        self.side_layout.addWidget(self.welcome_back_label)

        self.separator = QLabel()
        self.separator.setFixedHeight(2)
        self.separator.setStyleSheet("background-color: #3d3d3d;")
        self.side_layout.addWidget(self.separator)

        self.calculate_needs_button = QPushButton("Calculate Calories")
        self.calculate_needs_button.setObjectName("top_button")
        self.calculate_needs_button.clicked.connect(self.calculate_needs)
        self.side_layout.addWidget(self.calculate_needs_button)

        self.enter_data_button = QPushButton("Enter Data")
        self.enter_data_button.clicked.connect(self.enter_data)
        self.side_layout.addWidget(self.enter_data_button)

        self.view_data_button = QPushButton("View Data")
        self.view_data_button.clicked.connect(self.view_data)
        self.side_layout.addWidget(self.view_data_button)

        self.view_trends_button = QPushButton("View Trends")
        self.view_trends_button.clicked.connect(self.view_trends)
        self.side_layout.addWidget(self.view_trends_button)

        spacer_height = 25

        self.separator2 = QLabel()
        self.separator2.setFixedHeight(spacer_height)
        self.separator2.setStyleSheet("background-color: #2d2d2d; margin: 20px 0;")
        self.side_layout.addWidget(self.separator2)

        self.update_info_button = QPushButton("Update Info")
        self.update_info_button.clicked.connect(self.update_user_info)
        self.side_layout.addWidget(self.update_info_button)

        self.separator3 = QLabel()
        self.separator3.setFixedHeight(spacer_height)
        self.separator3.setStyleSheet("background-color: #2d2d2d; margin: 20px 0;")
        self.side_layout.addWidget(self.separator3)

        self.import_data_button = QPushButton("Import Data")
        self.import_data_button.clicked.connect(self.import_data)
        self.side_layout.addWidget(self.import_data_button)

        self.export_data_button = QPushButton("Export Data")
        self.export_data_button.clicked.connect(self.export_data)
        self.side_layout.addWidget(self.export_data_button)

        self.side_layout.addStretch(1)

        self.exit_button = QPushButton("Log out")
        self.exit_button.setObjectName("log_out_btn")
        self.exit_button.clicked.connect(self.close)
        self.side_layout.addWidget(self.exit_button)

        for button in self.side_widget.findChildren(QPushButton):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.side_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def enter_data(self):
        """
        Clears the current information widget and sets up a new layout for entering data.
        This method creates a vertical layout containing a styled QCalendarWidget and a form layout
        with input fields for weight and calories. It also adds a submit button to the layout.
        The entire layout is then added to the info_layout widget.
        Widgets and Layouts:
        - QCalendarWidget: A calendar widget with custom styles.
        - QLineEdit: Input fields for weight and calories with placeholder text.
        - QPushButton: A button to submit the entered data.
        - QVBoxLayout: Main layout to hold the calendar and form layout.
        - QFormLayout: Layout to organize the input fields.
        - QWidget: Container widget to hold the entire layout with custom styles.
        Styles:
        - Custom styles are applied to the QCalendarWidget, QLineEdit, and QLabel widgets.
        Connections:
        - The submit button is connected to the submit_data method.
        """

        self.clear_info_widget()

        layout = QVBoxLayout()

        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet(
            """
            QCalendarWidget {
            background-color: #2d2d2d;
            color: #ccc;
            border: 1px solid #1e1e1e;
            border-radius: 5px;
            }
            QCalendarWidget QToolButton {
            color: #ccc;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            padding: 5px;
            margin: 5px;
            }
            QCalendarWidget QToolButton::hover {
            background-color: #5d5d5d;
            }
            QCalendarWidget QToolButton::pressed {
            background-color: #4f4f4f;
            }
            QCalendarWidget QToolButton::menu-indicator {
            image: none;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
            background-color: #1e1e1e;
            border-radius: 5px;
            }
            QCalendarWidget QSpinBox {
            background-color: #2d2d2d;
            color: #ccc;
            border: none;
            font-size: 16px;
            }
            QCalendarWidget QAbstractItemView:enabled {
            color: #ccc;
            background-color: #2d2d2d;
            selection-background-color: #5d5d5d;
            selection-color: #fff;
            }
        """
        )
        self.calendar.setWeekdayTextFormat(
            Qt.DayOfWeek.Saturday, self.calendar.weekdayTextFormat(Qt.DayOfWeek.Monday)
        )
        self.calendar.setWeekdayTextFormat(
            Qt.DayOfWeek.Sunday, self.calendar.weekdayTextFormat(Qt.DayOfWeek.Monday)
        )
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )

        layout.addWidget(self.calendar)

        form_layout = QFormLayout()

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Enter weight (lbs)")
        form_layout.addRow("Weight:", self.weight_input)

        self.calories_input = QLineEdit()
        self.calories_input.setPlaceholderText("Enter calories")
        form_layout.addRow("Calories:", self.calories_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("Enter Data")
        self.submit_button.clicked.connect(self.submit_data)
        self.submit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.submit_button)

        container_widget = QWidget()
        container_widget.setStyleSheet(
            """
            QLabel {
                font-family: Tahoma, Arial, sans-serif;
                color: #ccc;
                font-weight: bold;
                font-size: 18px;
            }
            QLineEdit {
                font-family: Tahoma, Arial, sans-serif;
                color: #ccc;
                border: 1px solid gray;
                border-radius: 4px;
                padding: 4px;
                font-size: 18px;
            }
        """
        )
        container_widget.setLayout(layout)
        self.info_layout.addWidget(container_widget)

    def submit_data(self):
        """
        Submits the weight and calorie data for the selected date.
        This method retrieves the selected date, weight, and calorie inputs from the user 
        interface.
        It checks if the inputs are provided and displays a warning message if any field is empty.
        If data for the specified date already exists, it prompts the user to confirm whether to
        update the existing data.
        Depending on the user's response, it either updates the existing data or inserts new data 
        into the database.
        Finally, it commits the changes to the database and displays a success message.
        Raises:
            QMessageBox.warning: If any of the input fields are empty.
            QMessageBox.question: If data for the specified date already exists.
            QMessageBox.information: To inform the user about the success or cancellation of the 
            data entry.
        """

        selected_date = self.calendar.selectedDate().toString("yyyy-MM-d")
        weight = self.weight_input.text()
        calories = self.calories_input.text()

        if not weight or not calories:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        weight_entry(self, selected_date, weight, calories)

        self.weight_input.clear()
        self.calories_input.clear()


    def view_data(self):
        """
        Creates and displays a tabbed widget containing data tables for different time periods.
        This method initializes a QTabWidget with tabs representing different time periods 
        (e.g., "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "All"). Each tab contains 
        a QTableWidget styled with a dark theme and headers for "Date", "Weight", and "Calories". 
        The method also connects the tab change event to update the displayed data accordingly.
        The method performs the following steps:
        1. Initializes the QTabWidget and sets its stylesheet.
        2. Connects the tab change event to the update_tab_data method.
        3. Creates a QTableWidget for each period, sets its stylesheet, and configures its columns.
        4. Adds each QTableWidget to the QTabWidget.
        5. Clears the current info widget.
        6. Adds the QTabWidget to the info layout.
        7. Updates the data for the first tab.
        Note:
            This method assumes that the following instance attributes are defined:
            - self.tab_widget: The QTabWidget instance.
            - self.info_layout: The layout where the tab widget will be added.
            - self.clear_info_widget: A method to clear the current info widget.
            - self.update_tab_data: A method to update the data displayed in the current tab.
        """

        periods = ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "All"]

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
            border: 1px solid #1e1e1e;
            top:-1px;
            background: #2d2d2d;
            }

            QTabBar::tab {
            background: #1e1e1e;
            border: 1px solid #1e1e1e;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            padding: 15px;
            font-family: Tahoma, Arial, sans-serif;
            font-size: 14px;
            font-weight: bold;
            color: #ccc;
            }

            QTabBar::tab:selected {
            background: #2d2d2d;
            margin-bottom: -1px;
            }
        """
        )
        self.tab_widget.currentChanged.connect(self.update_tab_view_data)

        for period in periods:
            table_widget = QTableWidget()
            table_widget.setStyleSheet(
                """
                QTableWidget {
                    background-color: #2d2d2d;
                    font-family: Tahoma, Arial, sans-serif;
                    color: #ccc;
                    border: 1px solid #1e1e1e;
                    gridline-color: #1e1e1e;
                }
                QHeaderView::section {
                    background-color: #3c3c3c;
                    font-weight: bold;
                    font-size: 12px;
                    color: #ccc;
                    padding: 4px;
                }
                QTableWidget::item {
                    padding: 10px;
                font-size:10px;
                }
            """
            )
            table_widget.horizontalHeader().setStretchLastSection(True)
            table_widget.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            table_widget.setColumnCount(3)
            table_widget.setHorizontalHeaderLabels(["Date", "Weight", "Calories"])
            self.tab_widget.addTab(table_widget, period)

        self.clear_info_widget()

        self.info_layout.addWidget(self.tab_widget)
        self.update_tab_view_data(0)

    def clear_info_widget(self):
        """
        Clears all widgets from the info_layout.
        This method iterates over the widgets in the info_layout in reverse order,
        removes each widget from the layout, and sets its parent to None to ensure
        it is properly deleted.
        """

        for i in reversed(range(self.info_layout.count())):
            widget_to_remove = self.info_layout.itemAt(i).widget()
            self.info_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

    def update_tab_view_data(self, index):
        """
        Updates the data displayed in the table widget of the specified tab.
        Args:
            index (int): The index of the tab to update.
        The method retrieves the period associated with the tab, fetches the relevant data
        from the database based on the period, and populates the table widget with the data.
        If the period is not recognized, it fetches all available data.
        The data includes the date, weight, and calories, which are displayed in the table
        widget with centered text alignment.
        """

        period = self.tab_widget.tabText(index).lower()
        table_widget = self.tab_widget.widget(index)

        period_days = PERIOD_DAYS.get(period, None)

        data = get_view_data(self, period_days)
        table_widget.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table_widget.setItem(row_idx, col_idx, item)

    def calculate_needs(self):
        """
        Calculate and display the user's caloric needs based on their data.
        This method retrieves the user's caloric needs from the database, clears any existing
        information widgets, and then creates and displays new labels with the calculated
        caloric needs and recommendations.
        The displayed information includes:
        - Estimated Basal Metabolic Rate (BMR)
        - General recommendation
        - Warning message
        - Caloric intake to maintain weight
        - Caloric intake to gain muscle
        - Caloric intake to lose weight
        The labels are styled with a specific font and color, and added to the layout of the
        info widget.
        Parameters:
        None
        Returns:
        None
        """
        result = calculate_caloric_needs(self.conn, self.user_id)

        self.clear_info_widget()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        font_height = 35

        bmr_label = QLabel(f"Estimated BMR: {result['BMR']} kcal/day")
        bmr_label.setFixedHeight(font_height)
        layout.addWidget(bmr_label)

        recommendation_label = QLabel(f"{result['Recommendation']}")
        recommendation_label.setFixedHeight(font_height * 2)
        layout.addWidget(recommendation_label)

        warning_label = QLabel(f"{result['Warning']}")
        warning_label.setFixedHeight(font_height)
        layout.addWidget(warning_label)

        maintenance_label = QLabel(
            f"Based on your data, to maintain weight eat {result['Maintenance']} kcal/day"
        )
        maintenance_label.setFixedHeight(font_height)
        layout.addWidget(maintenance_label)

        gain_muscle_label = QLabel(
            f"Based on your data, to gain muscle eat {result['Gain']} kcal/day"
        )
        gain_muscle_label.setFixedHeight(font_height)
        layout.addWidget(gain_muscle_label)

        lose_weight_label = QLabel(
            f"Based on your data, to lose weight, eat {result['Lose']} kcal/day"
        )
        lose_weight_label.setFixedHeight(font_height)
        layout.addWidget(lose_weight_label)

        container_widget = QWidget()
        container_widget.setStyleSheet(
            """
            QLabel {
            font-family: Tahoma, Arial, sans-serif;
            color: #ccc;
            font-weight: bold;
            font-size: 18px;
            padding-bottom: 10px;
            }
        """
        )
        container_widget.setLayout(layout)
        self.info_layout.addWidget(container_widget)

    def update_user_info(self):
        """
        Updates the user information form with input fields for age, height, and activity level.
        This method clears the existing information widget and sets up a new form layout with the
        following fields:
        - Age: A QLineEdit for entering the user's age.
        - Height: A QLineEdit for entering the user's height in inches.
        - Activity Level: A QComboBox for selecting the user's activity level from predefined 
        options.
        Additionally, a submit button is added to the form to allow the user to submit their 
        information.
        The form and its elements are styled using a stylesheet for a consistent appearance.
        """
        self.clear_info_widget()

        layout = QFormLayout()

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter your age")
        layout.addRow("Age:", self.age_input)

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Enter your height (inches)")
        layout.addRow("Height:", self.height_input)

        self.activity_level_input = QComboBox()
        self.activity_level_input.addItems(
            [
                "Sedentary (little or no exercise)",
                "Lightly active (light exercise/sports 1-3 days/week)",
                "Moderately active (moderate exercise/sports 3-5 days/week)",
                "Very active (hard exercise/sports 6-7 days a week)",
                "Extremely active (very hard exercise & physical job or 2x training)",
            ]
        )
        layout.addRow("Activity Level:", self.activity_level_input)

        self.submit_button = QPushButton("Update Info")
        self.submit_button.clicked.connect(self.submit_user_info)
        layout.addWidget(self.submit_button)
        self.submit_button.setCursor(Qt.CursorShape.PointingHandCursor)

        container_widget = QWidget()
        container_widget.setStyleSheet(
            """
                QComboBox {
                    font-family: Tahoma, Arial, sans-serif;
                    color: #ccc;
                    border: 1px solid gray;
                    border-radius: 4px;
                    padding: 4px;
                    font-size: 18px;
                    background-color: #2d2d2d;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    color: #ccc;
                    selection-background-color: #5d5d5d;
                    selection-color: #fff;
                }

            QLabel {
                font-family: Tahoma, Arial, sans-serif;
                color: #ccc;
                font-weight: bold;
                font-size: 18px;
            }
            QLineEdit {
                font-family: Tahoma, Arial, sans-serif;
                color: #ccc;
                border: 1px solid gray;
                border-radius: 4px;
                padding: 4px;
                font-size: 18px;
            }
        """
        )

        container_widget.setLayout(layout)
        self.info_layout.addWidget(container_widget)
        self.submit_button.setCursor(Qt.CursorShape.PointingHandCursor)

    def submit_user_info(self):
        """
        Updates the user's information in the database with the provided age, height, and activity 
        level. This method retrieves the user's input from the GUI fields, validates that all 
        fields are filled, and then updates the corresponding user's record in the database. If any
        field is empty, a warning message is displayed. Upon successful update, an information 
        message is shown.
        Raises:
            QMessageBox.warning: If any of the input fields (age, height, activity level)
            are empty.
            QMessageBox.information: If the user's information is updated successfully.
        """
        age = self.age_input.text()
        height = self.height_input.text()
        activity_level = self.activity_level_input.currentText()

        if not age or not height or not activity_level:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        submit_updated_info(self, age, height, activity_level)

        QMessageBox.information(self, "Success", "User info updated successfully.")

    def view_trends(self):
        """
        Creates and displays a tab widget for viewing trends over different periods.
        This method initializes a QTabWidget with predefined periods such as "1 Week", "1 Month", 
        "3 Months", "6 Months", "1 Year", and "All". It sets the style for the tab widget and 
        its tabs, connects the tab change event to the update_trends method, and adds a tab 
        for each period. Finally, it clears the current info widget and adds the tab widget 
        to the info layout.
        """
        periods = ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "All"]

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
            border: 1px solid #1e1e1e;
            top:-1px;
            background: #2d2d2d;
            }

            QTabBar::tab {
            background: #1e1e1e;
            border: 1px solid #1e1e1e;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            padding: 15px;
            font-family: Tahoma, Arial, sans-serif;
            font-size: 14px;
            font-weight: bold;
            color: #ccc;
            }

            QTabBar::tab:selected {
            background: #2d2d2d;
            margin-bottom: -1px;
            }
        """
        )

        self.tab_widget.currentChanged.connect(self.update_tab_trends_data)

        for period in periods:
            self.tab_widget.addTab(self.create_trend_tab(), period)

        self.clear_info_widget()

        self.info_layout.addWidget(self.tab_widget)

    def create_trend_tab(self):
        """
        Creates a trend tab layout for displaying average weight and weight difference information.
        This method sets up a vertical layout containing labels for average weight, date range, 
        and weight difference,
        along with their respective styles and fonts. It also creates a matplotlib canvas for 
        plotting trends.
        Returns:
            QWidget: A container widget with the trend tab layout and associated labels and 
            canvas.
        """

        layout = QVBoxLayout()

        bold_font = QFont("Tahoma", 24, QFont.Weight.Bold)
        thin_font = QFont("Tahoma", 14)

        label_height = 30

        avg_weight_label = QLabel()
        avg_weight_label.setFixedHeight(label_height)
        avg_weight_label.setFont(bold_font)
        avg_weight_label.setStyleSheet("color: #ccc")

        avg_label = QLabel("Average")
        avg_label.setFixedHeight(label_height)
        avg_label.setFont(thin_font)
        avg_label.setStyleSheet("color: #ccc")
        avg_label.setGraphicsEffect(self.create_opacity_effect(0.5))

        date_range_label = QLabel()
        date_range_label.setFixedHeight(label_height)
        date_range_label.setFont(thin_font)
        date_range_label.setStyleSheet("color: #ccc")
        date_range_label.setGraphicsEffect(self.create_opacity_effect(0.5))

        weight_diff_label = QLabel()
        weight_diff_label.setFixedHeight(label_height)
        weight_diff_label.setFont(bold_font)
        weight_diff_label.setStyleSheet("color: #ccc")

        diff_label = QLabel("Difference")
        diff_label.setFixedHeight(label_height)
        diff_label.setStyleSheet("color: #ccc")
        diff_label.setGraphicsEffect(self.create_opacity_effect(0.5))
        diff_label.setFont(thin_font)

        spacer_label = QLabel()
        spacer_label.setFixedHeight(label_height)

        # Create Layouts
        average_layout = QVBoxLayout()
        average_layout.setSpacing(10)
        average_layout.addWidget(avg_label)
        average_layout.addWidget(avg_weight_label)
        average_layout.addWidget(date_range_label)

        difference_layout = QVBoxLayout()
        difference_layout.setSpacing(10)
        difference_layout.addWidget(diff_label)
        difference_layout.addWidget(weight_diff_label)
        difference_layout.addWidget(spacer_label)

        trend_text_layout = QHBoxLayout()
        trend_text_layout.addStretch(1)
        trend_text_layout.addLayout(average_layout)
        trend_text_layout.addStretch(2)
        trend_text_layout.addLayout(difference_layout)
        trend_text_layout.addStretch(1)

        layout.addLayout(trend_text_layout)

        canvas = FigureCanvas(plt.Figure())
        plt.rcParams["font.family"] = "Tahoma"
        layout.addWidget(canvas)

        container_widget = QWidget()
        container_widget.setLayout(layout)
        container_widget.avg_weight_label = avg_weight_label
        container_widget.date_range_label = date_range_label
        container_widget.weight_diff_label = weight_diff_label
        container_widget.canvas = canvas

        return container_widget

    def update_tab_trends_data(self):
        """
        Updates the trend data and visual representation for the current tab based on the selected 
        period.
        This function retrieves weight data from the database for the specified period, calculates 
        average weight,
        weight difference, and date range, and updates the corresponding labels in the UI. It also 
        plots the weight
        data and a rolling average trend on a matplotlib canvas.
        The period is determined by the currently selected tab, which can be one of the following:
        "1 week", "1 month", "3 months", "6 months", "1 year", or a custom period.
        The function performs the following steps:
        1. Retrieves the selected period and current tab widget.
        2. Maps the period to the corresponding number of days.
        3. Executes a SQL query to fetch weight data for the user within the specified period.
        4. Calculates average weight, weight difference, and date range.
        5. Updates the UI labels with the calculated values.
        6. Plots the weight data and a rolling average trend on a matplotlib canvas.
        7. Styles the plot with custom colors and formatting.
        Args:
            None
        Returns:
            None
        """
        period = self.tab_widget.tabText(self.tab_widget.currentIndex()).lower()
        current_tab = self.tab_widget.currentWidget()

        period_days = PERIOD_DAYS.get(period, None)

        data = get_trend_data(self, period_days)
        dates = [row[0] for row in data]
        weights = [row[1] for row in data]

        if weights:
            avg_weight = sum(weights) / len(weights)
            weight_diff = weights[0] - weights[-1]
            signed_weight_diff = np.sign(weight_diff) * abs(weight_diff)
            start_date = pd.to_datetime(dates[-1])
            end_date = pd.to_datetime(dates[0])
            if start_date.year == end_date.year:
                if start_date.month == end_date.month:
                    date_range = (
                        f"{start_date.strftime('%b %d')}-{end_date.strftime('%d, %Y')}"
                    )
                else:
                    date_range = f"{start_date.strftime('%b %d')}-{end_date.strftime('%b %d, %Y')}"
            else:
                date_range = f"{start_date.strftime('%b %d, %Y')}-{end_date.strftime('%b %d, %Y')}"

            current_tab.avg_weight_label.setText(f"{avg_weight:.1f} lbs")
            current_tab.date_range_label.setText(f"{date_range}")
            current_tab.weight_diff_label.setText(f"{signed_weight_diff:+.2f} lbs")

            fig = current_tab.canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)

            ax.plot(
                mdates.date2num(dates[::-1]),
                weights[::-1],
                label="Scale Weight",
                color="#ff5349",
                linewidth=2,
                alpha=0.25,
            )

            step = max(1, len(dates) // 12)
            # Set x-axis label step dynamically
            if period_days:
                if period_days <= 7:
                    step = 1
                elif period_days <= 30:
                    step = 2
                elif period_days <= 90:
                    step = 7
                elif period_days <= 180:
                    step = 14
                elif period_days <= 365:
                    step = 30
            else:
                step = max(1, len(dates) // 12)

            ax.xaxis.set_major_locator(mdates.DayLocator(interval=step))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
            ax.set_xlim([mdates.date2num(start_date), mdates.date2num(end_date)])
            fig.autofmt_xdate()

            window_size = 7  # Control smoothness
            weights_series = pd.Series(weights)
            rolling_avg = weights_series.rolling(
                window=window_size, center=True, min_periods=1
            ).mean()
            ax.plot(
                mdates.date2num(dates),
                rolling_avg,
                label="Trend Weight",
                color="#ff5349",
                linewidth=2,
            )

            # Styling
            ax.set_facecolor("#2d2d2d")
            fig.patch.set_facecolor("#2d2d2d")
            ax.tick_params(colors="#ccc", which="both", left=False, right=False)
            ax.xaxis.label.set_color("#ccc")
            ax.yaxis.label.set_color("#ccc")
            ax.title.set_color("#ccc")
            for spine in ax.spines.values():
                spine.set_edgecolor("#ccc")
            ax.yaxis.tick_right()
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["top"].set_visible(False)
            y_min, y_max = ax.get_ylim()
            y_mid = round((math.floor(y_min) + math.floor(y_max)) / 2)
            ax.axhline(
                math.ceil(y_max), linestyle="dotted", color="#ccc", linewidth=1.5
            )
            ax.axhline(y_mid, linestyle="dotted", color="#ccc", linewidth=1.5)
            ax.set_yticks([math.floor(y_min), y_mid, math.ceil(y_max)])
            ax.legend(loc="lower right", frameon=False, labelcolor="#ccc")

            current_tab.canvas.draw()

    def import_data(self):
        """
        Opens a file dialog to select a CSV file and imports its data into the database.
        This method uses a QFileDialog to allow the user to select a CSV file from their filesystem.
        If a file is selected, it calls the `import_csv_to_db` function to import the data from the
        CSV file into the database associated with the current connection and user ID. Upon 
        successful import, a message box is displayed to inform the user.
        Returns:
            None
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Data from CSV", "", "CSV Files (*.csv)"
        )
        if file_path:
            import_csv_to_db(self.conn, file_path, self.user_id)
            QMessageBox.information(
                self, "Import Successful", "Data imported successfully."
            )

    def export_data(self):
        """
        Exports data from the database to a CSV file.
        This method calls the `export_db_to_csv` function, passing the current
        database connection and user ID as arguments. Upon successful export,
        it displays an information message box to inform the user.
        Raises:
            Any exceptions raised by `export_db_to_csv` will propagate up to the caller.
        """
        export_db_to_csv(self.conn, self.user_id)
        QMessageBox.information(
            self, "Export Successful", "Data exported successfully."
        )

    def create_opacity_effect(self, opacity):
        """
        Creates a QGraphicsOpacityEffect with the specified opacity.
        Args:
            opacity (float): The opacity level to set, where 0.0 is fully transparent 
            and 1.0 is fully opaque.
        Returns:
            QGraphicsOpacityEffect: The opacity effect with the specified opacity level.
        """
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(opacity)
        return effect

if __name__ == "__main__":
    from login_window import LoginWindow
    app = QApplication(sys.argv)
    LoginWindow = LoginWindow()
    LoginWindow.show()
    sys.exit(app.exec())
