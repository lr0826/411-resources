from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    """
    A class to represent a boxer.

    Attributes:
        id (int): Unique identifier for the boxer.
        name (str): The name of the boxer.
        weight (int): The weight of the boxer in pounds.
        height (int): The height of the boxer in inches.
        reach (float): The reach of the boxer in inches.
        age (int): The age of the boxer.
        weight_class (str): The weight class of the boxer (automatically assigned).
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """
        Assigns the weight class of the boxer based on their weight.

        This method is called automatically after the Boxer instance is initialized.
        """
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """
    Creates a new boxer in the database.

    Args:
        name (str): Name of the boxer (must be unique).
        weight (int): Weight of the boxer in pounds.
        height (int): Height in inches.
        reach (float): Reach in inches.
        age (int): Age between 18 and 40.

    Raises:
        ValueError: If any field is invalid or boxer already exists.
        sqlite3.Error: For general database errors.
    """
    logger.info(f"Creating boxer: {name}")

    if weight < 125:
        logger.error(f"Invalid weight: {weight}")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Invalid height: {height}")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Invalid reach: {reach}")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Invalid age: {age}")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))
            conn.commit()
            logger.info(f"Successfully created boxer: {name}")

    except sqlite3.IntegrityError:
        logger.error(f"Integrity error: Boxer '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")
    except sqlite3.Error as e:
        logger.error(f"Database error while creating boxer '{name}': {e}")
        raise e



def delete_boxer(boxer_id: int) -> None:
    """
    Deletes a boxer by their ID.

    Args:
        boxer_id (int): Unique ID of the boxer.

    Raises:
        ValueError: If boxer is not found.
        sqlite3.Error: For general database errors.
    """
    logger.info(f"Attempting to delete boxer with ID: {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Successfully deleted boxer with ID: {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer ID {boxer_id}: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    Retrieves a leaderboard of boxers sorted by win percentage or total wins.

    Args:
        sort_by (str): Sort key; either "wins" or "win_pct".

    Returns:
        List[dict[str, Any]]: Leaderboard with boxer stats.

    Raises:
        ValueError: If sort_by is invalid.
        sqlite3.Error: For general database errors.
    """
    logger.info(f"Generating leaderboard sorted by {sort_by}")
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)
            }
            leaderboard.append(boxer)

        logger.info(f"Successfully generated leaderboard with {len(leaderboard)} entries")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error while generating leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """
    Retrieves a boxer from the database by ID.

    Args:
        boxer_id (int): The ID of the boxer to retrieve.

    Returns:
        Boxer: The boxer object.

    Raises:
        ValueError: If boxer is not found.
        sqlite3.Error: For general database errors.
    """
    logger.info(f"Retrieving boxer by ID: {boxer_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer found with ID: {boxer_id}")
                return Boxer(*row)
            else:
                logger.warning(f"Boxer with ID {boxer_id} not found")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error retrieving boxer ID {boxer_id}: {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Retrieves a boxer from the database by name.

    Args:
        boxer_name (str): The name of the boxer.

    Returns:
        Boxer: The boxer object.

    Raises:
        ValueError: If boxer is not found.
        sqlite3.Error: For general database errors.
    """
    logger.info(f"Retrieving boxer by name: {boxer_name}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer found: {boxer_name}")
                return Boxer(*row)
            else:
                logger.warning(f"Boxer '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error retrieving boxer '{boxer_name}': {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """
    Determines the weight class of a boxer based on their weight.

    Args:
        weight (int): The boxer's weight in pounds.

    Returns:
        str: The weight class name.

    Raises:
        ValueError: If weight is below minimum threshold (125).
    """
    if weight >= 203:
        return 'HEAVYWEIGHT'
    elif weight >= 166:
        return 'MIDDLEWEIGHT'
    elif weight >= 133:
        return 'LIGHTWEIGHT'
    elif weight >= 125:
        return 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight class lookup for weight: {weight}")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Updates a boxer's record based on fight result.

    Args:
        boxer_id (int): ID of the boxer to update.
        result (str): "win" or "loss".

    Raises:
        ValueError: If boxer is not found or result is invalid.
        sqlite3.Error: For general database errors.
    """
    logger.info(f"Updating boxer stats for ID {boxer_id} with result '{result}'")
    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result value: {result}")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found for stats update")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Boxer stats updated for ID {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error updating stats for boxer ID {boxer_id}: {e}")
        raise e
