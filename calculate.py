"""csv module implements classes to read and write tabular data in CSV format."""
import csv
from collections import defaultdict
from datetime import datetime
import numpy as np
from PyQt6.QtWidgets import QMessageBox


def create_tables(conn):
    """
    Create the necessary tables in the database if they do not already exist.

    This function creates three tables:
    - users: Stores user information including id, username, password, sex, age, 
            height, and activity level.
    - weights: Stores weight records for users, including id, user_id, weight, and date.
    - calories: Stores calorie intake records for users, including id, user_id, calories, and date.

    Args:
        conn (sqlite3.Connection): The database connection object.

    Returns:
        None
    """
    with conn:
        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                sex TEXT NOT NULL,
                age INTEGER NOT NULL,
                height INTEGER NOT NULL,
                activity_level TEXT NOT NULL
            );
        """
        )
        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS weights(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER NOT NULL,
                     weight REAL NOT NULL,
                     date TEXT NOT NULL,
                     FOREIGN KEY(user_id) REFERENCES users(id)
                );
        """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                calories INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """
        )


def get_user(conn, username, password):
    """Check if a user exists and return their ID"""
    user = conn.execute(
        """
                        SELECT id FROM users WHERE username = ? and password = ?;
                        """,
        (username, password),
    ).fetchone()
    return user[0] if user else None


def create_user(conn, username, password, sex, age, height, activity_level):
    """Create a new user and return their ID"""
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, password, sex, age, height, activity_level)
            VALUES (?, ?, ?, ?, ?, ?);
        """,
            (username, password, sex, age, height, activity_level),
        )
        return cursor.lastrowid

def import_csv_to_db(conn, file_path, user_id):
    """Import data from a CSV file to the database
    Parameters:
    - conn: SQLite connection
    - file_path: Path to the CSV file
    - user_id: ID of the user

    Returns:
    - None
    """
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Parse date
            date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
            # Insert weight and calorie data into the database
            if "Weight" in row and row["Weight"]:
                conn.execute(
                    """
                    INSERT INTO weights (user_id, weight, date)
                    VALUES (?, ?, ?);
                """,
                    (user_id, float(row["Weight"]), date),
                )
            if "Calories" in row and row["Calories"]:
                conn.execute(
                    """
                    INSERT INTO calories (user_id, calories, date)
                    VALUES (?, ?, ?);
                """,
                    (user_id, int(row["Calories"]), date),
                )
        conn.commit()
    print("Data imported successfully!")


def export_db_to_csv(conn, user_id):
    """Export data from the database to a CSV file
    Parameters:
    - conn: SQLite connection
    - user_id: ID of the user

    Returns:
    - None
    """
    # Generate CSV file name with current date
    file_name = f"data_{datetime.now().strftime('%m%d%y')}.csv"

    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Weight", "Calories"])

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT date, weight FROM weights WHERE user_id = ?;
        """,
            (user_id,),
        )
        weights = cursor.fetchall()
        cursor.execute(
            """
            SELECT date, calories FROM calories WHERE user_id = ?;
        """,
            (user_id,),
        )
        calories = cursor.fetchall()

        # Combine weight and calorie data
        data = defaultdict(lambda: [None, None])
        for date, weight in weights:
            data[date].insert(1, weight)
        for date, calorie in calories:
            data[date].insert(2, calorie)

        # Write data to CSV file
        for date, values in data.items():
            writer.writerow([date, *values])

    print("Data exported successfully!")


def calculate_caloric_needs(conn, user_id, period_days=-1):
    """Calculate caloric needs for a user
    Parameters:
    - conn: SQLite connection
    - user_id: ID of the user
    - period_days: Number of days to calculate trends (default: all data)

    Returns:
    - Estimated maintenance calories
    """
    cursor = conn.cursor()

    # Get weights data
    cursor.execute(
        """
        SELECT weight, date FROM weights
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?;
    """,
        (user_id, period_days if period_days else -1),
    )
    weights_data = cursor.fetchall()

    # Get calories data
    cursor.execute(
        """
        SELECT calories, date FROM calories
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?;
    """,
        (user_id, period_days if period_days else -1),
    )
    calories_data = cursor.fetchall()

    # Validate data
    if len(weights_data) != len(calories_data):
        raise ValueError("Weights and calories lists must have the same length.")

    # Parse data
    weights = [w[0] for w in weights_data]
    calories = [c[0] for c in calories_data]

    if not weights or not calories:
        raise ValueError("No data found for the user.")

    period_days = len(weights)

    # Fetch user data
    cursor.execute(
        """
        SELECT sex, age, height, activity_level FROM users WHERE id = ?;
    """,
        (user_id,),
    )
    user_data = cursor.fetchone()

    if not user_data:
        raise ValueError("User data not found.")

    sex, age, height, activity_level = user_data

    bmr = (
        129.6 * ((weights[0] * 0.453592) ** 0.55)
        + 0.011 * ((height * 2.54) ** 2)
        - (1.96 * age if age <= 60 else 4.9 * (age - 60))
        - 213.8 * (0 if sex.lower() == "male" else 1)
    )

    # Activity level multiplier
    pal_dict = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extremely active": 1.9,
    }
    pal = pal_dict.get(activity_level)
    if not pal:
        raise ValueError("Invalid activity level.")

    maintenance_bmr = bmr * pal

    ###############################################

    delta = 0.1
    weight_trend = calculate_weight_trend(weights)
    avg_weight_change = (weight_trend - weights[0]) / (len(weights) / 7)  # lbs/week

    # Maintenance calories
    avg_calories = sum(calories) / len(calories)
    energy_balance = avg_weight_change * 3500
    maintenance_calories = avg_calories - energy_balance

    # Target calorie adjustments
    gain_calories = maintenance_calories + ((0.5 * 3500) / 7)  # +0.5lb week
    lose_calories = maintenance_calories - ((1.0 * 3500) / 7)  # -1.0 lbs week

    # Dynamic adjustment based on trends
    if -delta <= avg_weight_change <= delta:
        recommendation = (
            "You are maintaining weight. Continue at your current calorie level\n"
            "if you want to stay around this weight."
        )
        maintenance_calories = round(calories[0])
        gain_calories = maintenance_calories + ((0.5 * 3500) / 7)  # +0.5lb week
        lose_calories = maintenance_calories - ((1.0 * 3500) / 7)  # -1.0 lbs week
    elif avg_weight_change < -delta:
        recommendation = (
            f"You are losing weight at {avg_weight_change:.2f} lbs/week."
            "Consider increasing calories if you don't want to lose weight this quickly."
        )
    elif avg_weight_change > delta:
        recommendation = (
            f"You are gaining weight at {avg_weight_change:.2f} lbs/week."
            "Consider reducing calories if you don't want to gain weight this quickly."
        )
    else:
        recommendation = ""

    # Rapid change warnings
    rapid_change_warning = ""
    if avg_weight_change < -1.5:
        rapid_change_warning = (
            "Warning: You are losing weight too rapidly. Consider increasing calories."
        )
    elif avg_weight_change > 0.75:
        rapid_change_warning = (
            "Warning: You are gaining weight too rapidly. Consider reducing calories."
        )

    return {
        "BMR": round(maintenance_bmr),
        "Maintenance": round(maintenance_calories),
        "Gain": round(gain_calories),
        "Lose": round(lose_calories),
        "Recommendation": recommendation,
        "Warning": rapid_change_warning,
    }


def calculate_weight_trend(weights, half_life=7):
    """
    Calculate a weighted moving average for weight trend estimation.
    More recent weights are weighted higher.
    """
    days = len(weights)
    weights = np.array(weights)
    decay_weights = np.exp(-np.arange(days) / half_life)
    decay_weights /= decay_weights.sum()
    return np.sum(weights * decay_weights)


def trend_summary(daily_weight_change, avg_calories, delta=0.1):
    """
    Summarizes the weight trend based on daily weight change and average calorie intake.
    Parameters:
    daily_weight_change (float): The daily change in weight in pounds.
    avg_calories (float): The average number of calories consumed per day.
    delta (float, optional): The threshold for considering weight change as maintaining. 
        Default is 0.1.
    Returns:
    str: A summary of the weight trend and average calorie intake.
    """
    if abs(daily_weight_change) <= delta:
        trend = "you are maintaining your weight."
    elif daily_weight_change > delta:
        trend = f"you are gaining weight at {daily_weight_change:.2f}lbs/day."
    else:  # daily_weight_change < delta
        trend = f"you are losing weight at {abs(daily_weight_change):.2f}lbs/day."

    return f"Eating {round(avg_calories)} calories on average, {trend}"

def submit_updated_info(self, age, height, activity_level):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET age = ?, height = ?, activity_level = ?
            WHERE id = ?
        """,
            (age, height, activity_level, self.user_id),
        )
        self.conn.commit()

def weight_entry(self, selected_date, weight, calories):
        cursor = self.conn.cursor()
        # cursor.execute("""
        #     INSERT OR REPLACE INTO weights (user_id, date, weight) VALUES (?, ?, ?)
        # """, (self.user_id, selected_date, weight))
        # cursor.execute("""
        #     INSERT OR REPLACE INTO calories (user_id, date, calories) VALUES (?, ?, ?)
        # """, (self.user_id, selected_date, calories))
        # self.conn.commit()

        # Check if an entry for the specified date already exists
        weight_entry = cursor.execute(
            """
                   SELECT weight FROM weights WHERE user_id = ? AND date = ?;""",
            (self.user_id, selected_date),
        ).fetchone()

        calorie_entry = cursor.execute(
            """
                    SELECT calories FROM calories WHERE user_id = ? AND date = ?;""",
            (self.user_id, selected_date),
        ).fetchone()

        if weight_entry or calorie_entry:
            reply = QMessageBox.question(
                self,
                "Data Exists",
                "Data already exists for this date. Do you want to update it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                QMessageBox.information(self, "Cancelled", "Data entry cancelled.")
                return

        # Update or insert weight data
        if weight_entry:
            cursor.execute(
                """
                     UPDATE weights SET weight = ? WHERE user_id = ? AND date = ?;""",
                (weight, self.user_id, selected_date),
            )
        else:
            cursor.execute(
                """
                     INSERT INTO weights (user_id, weight, date) VALUES (?, ?, ?);""",
                (self.user_id, weight, selected_date),
            )

        if calorie_entry:
            cursor.execute(
                """
                     UPDATE calories SET calories = ? WHERE user_id = ? AND date = ?;""",
                (calories, self.user_id, selected_date),
            )
        else:
            cursor.execute(
                """
                     INSERT INTO calories (user_id, calories, date) VALUES (?, ?, ?);""",
                (self.user_id, calories, selected_date),
            )

        self.conn.commit()
        QMessageBox.information(self, "Success", "Data Entered successfully.")

def get_trend_data(self, period_days):
        cursor = self.conn.cursor()
        if period_days:
            cursor.execute(
                """
                SELECT date, weight FROM (
                    SELECT date, weight,
                    ROW_NUMBER() OVER (ORDER BY date DESC) as row_num
                    FROM weights
                    WHERE user_id = ?
                ) WHERE row_num <= ?;
            """,
                (self.user_id, period_days),
            )
        else:
            cursor.execute(
                """
                SELECT date, weight FROM weights
                WHERE user_id = ?
                ORDER BY date DESC;
            """,
                (self.user_id,),
            )

        data = cursor.fetchall()
        return data

def get_view_data(self, period_days):
        cursor = self.conn.cursor()
        if period_days:
            cursor.execute(
                """
                SELECT date, weight, calories FROM (
                    SELECT date, weight, calories,
                    ROW_NUMBER() OVER (ORDER BY date DESC) as row_num
                    FROM weights
                    LEFT JOIN calories USING (user_id, date)
                    WHERE user_id = ?
                ) WHERE row_num <= ?;
            """,
                (self.user_id, period_days),
            )
        else:
            cursor.execute(
                """
                SELECT date, weight, calories FROM weights
                LEFT JOIN calories USING (user_id, date)
                WHERE user_id = ?
                ORDER BY date DESC;
            """,
                (self.user_id,),
            )

        data = cursor.fetchall()
        return data