import pytest
import sqlite3

from boxing.utils.sql_utils import (
    check_database_connection,
    check_table_exists,
    get_db_connection
)


##################################################
# Fixtures
##################################################

@pytest.fixture
def mock_sqlite_connection(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch("sqlite3.connect", return_value=mock_conn)
    return mock_conn, mock_cursor


##################################################
# check_database_connection Tests
##################################################

def test_check_database_connection_success(mock_sqlite_connection):
    """Test DB connection check executes SELECT 1 successfully."""
    _, cursor = mock_sqlite_connection
    check_database_connection()
    cursor.execute.assert_called_once_with("SELECT 1;")


def test_check_database_connection_failure(mocker):
    """Test DB connection failure raises wrapped exception."""
    mocker.patch("sqlite3.connect", side_effect=sqlite3.Error("connection fail"))

    with pytest.raises(Exception, match="Database connection error"):
        check_database_connection()


##################################################
# check_table_exists Tests
##################################################

def test_check_table_exists_success(mock_sqlite_connection):
    """Test check_table_exists passes if table is present."""
    _, cursor = mock_sqlite_connection
    cursor.fetchone.return_value = ("boxers",)

    check_table_exists("boxers")
    cursor.execute.assert_called_once()


def test_check_table_exists_missing(mock_sqlite_connection):
    """Test check_table_exists raises if table is missing."""
    _, cursor = mock_sqlite_connection
    cursor.fetchone.return_value = None

    with pytest.raises(Exception, match="does not exist"):
        check_table_exists("ghosts")


def test_check_table_exists_error(mocker):
    """Test DB error in table check raises exception."""
    mocker.patch("sqlite3.connect", side_effect=sqlite3.Error("boom"))

    with pytest.raises(Exception, match="Table check error"):
        check_table_exists("anything")


##################################################
# get_db_connection Tests
##################################################

def test_get_db_connection_success(mocker):
    """Test context yields a connection and closes it."""
    mock_conn = mocker.Mock()
    mocker.patch("sqlite3.connect", return_value=mock_conn)

    with get_db_connection() as conn:
        assert conn == mock_conn

    mock_conn.close.assert_called_once()


def test_get_db_connection_failure(mocker):
    """Test failed connection raises sqlite3.Error."""
    mocker.patch("sqlite3.connect", side_effect=sqlite3.Error("fail"))

    with pytest.raises(sqlite3.Error, match="fail"):
        with get_db_connection():
            pass
