import pytest
from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    get_weight_class
)

##################################################
# Fixtures
##################################################

@pytest.fixture
def sample_boxer_data():
    """Provides sample valid boxer data."""
    return {
        "name": "Ali",
        "weight": 180,
        "height": 70,
        "reach": 74.5,
        "age": 28
    }

@pytest.fixture
def mock_cursor(mocker):
    """Mocks the DB connection + cursor."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []

    mocker.patch("boxing.models.boxers_model.get_db_connection", return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None))
    return mock_cursor

##################################################
# Create Boxer Tests
##################################################

def test_create_boxer_success(mock_cursor, sample_boxer_data):
    """Test creating a boxer with valid data."""
    create_boxer(**sample_boxer_data)

    mock_cursor.execute.assert_any_call("SELECT 1 FROM boxers WHERE name = ?", ("Ali",))
    assert mock_cursor.execute.call_count == 2


def test_create_boxer_duplicate(mock_cursor, sample_boxer_data):
    """Test that duplicate boxer name raises ValueError."""
    mock_cursor.fetchone.return_value = (1,)  # Simulate boxer exists

    with pytest.raises(ValueError, match="already exists"):
        create_boxer(**sample_boxer_data)


def test_create_boxer_invalid_weight(sample_boxer_data):
    """Test that invalid weight raises ValueError."""
    sample_boxer_data["weight"] = 100
    with pytest.raises(ValueError, match="Invalid weight"):
        create_boxer(**sample_boxer_data)


def test_create_boxer_invalid_age(sample_boxer_data):
    """Test that invalid age raises ValueError."""
    sample_boxer_data["age"] = 45
    with pytest.raises(ValueError, match="Invalid age"):
        create_boxer(**sample_boxer_data)


##################################################
# Weight Class Tests
##################################################

@pytest.mark.parametrize("weight,expected_class", [
    (210, "HEAVYWEIGHT"),
    (180, "MIDDLEWEIGHT"),
    (140, "LIGHTWEIGHT"),
    (126, "FEATHERWEIGHT")
])
def test_get_weight_class_valid(weight, expected_class):
    """Test weight class calculation for valid weights."""
    assert get_weight_class(weight) == expected_class


def test_get_weight_class_invalid():
    """Test that weight class lookup fails below minimum weight."""
    with pytest.raises(ValueError, match="Invalid weight"):
        get_weight_class(100)
##################################################
# Get Boxer by ID Tests
##################################################

def test_get_boxer_by_id_success(mocker):
    """Test retrieving a boxer by ID returns a Boxer instance."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    boxer_data = (1, "Ali", 180, 70, 74.5, 28)
    mock_cursor.fetchone.return_value = boxer_data
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch(
        "boxing.models.boxers_model.get_db_connection",
        return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None)
    )

    from boxing.models.boxers_model import get_boxer_by_id, Boxer
    boxer = get_boxer_by_id(1)

    assert isinstance(boxer, Boxer)
    assert boxer.name == "Ali"
    assert boxer.weight == 180
    assert boxer.weight_class == "MIDDLEWEIGHT"


def test_get_boxer_by_id_not_found(mocker):
    """Test retrieving a boxer with invalid ID raises ValueError."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch(
        "boxing.models.boxers_model.get_db_connection",
        return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None)
    )

    from boxing.models.boxers_model import get_boxer_by_id

    with pytest.raises(ValueError, match="not found"):
        get_boxer_by_id(999)
##################################################
# Delete Boxer Tests
##################################################

def test_delete_boxer_success(mocker):
    """Test deleting a boxer by ID when they exist."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch(
        "boxing.models.boxers_model.get_db_connection",
        return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None)
    )

    from boxing.models.boxers_model import delete_boxer
    delete_boxer(1)

    mock_cursor.execute.assert_any_call("DELETE FROM boxers WHERE id = ?", (1,))


def test_delete_boxer_not_found(mocker):
    """Test that deleting nonexistent boxer raises ValueError."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch(
        "boxing.models.boxers_model.get_db_connection",
        return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None)
    )

    from boxing.models.boxers_model import delete_boxer

    with pytest.raises(ValueError, match="not found"):
        delete_boxer(999)
##################################################
# Leaderboard Tests
##################################################

def test_get_leaderboard_sorted_by_wins(mocker):
    """Test that leaderboard returns structured output sorted by wins."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_cursor.fetchall.return_value = [
        (1, "Ali", 180, 70, 74.5, 28, 10, 8, 0.8),
        (2, "Tyson", 200, 72, 76, 30, 12, 9, 0.75)
    ]
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch(
        "boxing.models.boxers_model.get_db_connection",
        return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None)
    )

    from boxing.models.boxers_model import get_leaderboard
    result = get_leaderboard(sort_by="wins")

    assert isinstance(result, list)
    assert result[0]["name"] == "Ali"
    assert result[1]["name"] == "Tyson"


def test_get_leaderboard_invalid_sort():
    """Test that invalid sort_by raises ValueError."""
    from boxing.models.boxers_model import get_leaderboard

    with pytest.raises(ValueError, match="Invalid sort_by"):
        get_leaderboard(sort_by="bad_param")
##################################################
# Update Boxer Stats Tests
##################################################

def test_update_boxer_stats_win(mocker):
    """Test updating stats with 'win' result."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_cursor.fetchone.return_value = (1,)
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch(
        "boxing.models.boxers_model.get_db_connection",
        return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None)
    )

    from boxing.models.boxers_model import update_boxer_stats
    update_boxer_stats(1, "win")

    assert mock_cursor.execute.call_count >= 1


def test_update_boxer_stats_invalid_result():
    """Test that invalid result raises ValueError."""
    from boxing.models.boxers_model import update_boxer_stats

    with pytest.raises(ValueError, match="Invalid result"):
        update_boxer_stats(1, "draw")


def test_update_boxer_stats_not_found(mocker):
    """Test that missing boxer ID raises ValueError."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value = mock_cursor

    mocker.patch(
        "boxing.models.boxers_model.get_db_connection",
        return_value=mocker.MagicMock(__enter__=lambda s: mock_conn, __exit__=lambda *a: None)
    )

    from boxing.models.boxers_model import update_boxer_stats

    with pytest.raises(ValueError, match="not found"):
        update_boxer_stats(999, "win")

