import pytest
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def make_boxer(name: str) -> Boxer:
    """Helper to create a Boxer instance."""
    return Boxer(id=1, name=name, weight=180, height=70, reach=72.5, age=28)


def test_enter_ring_valid():
    """Test that valid boxers can enter the ring."""
    ring = RingModel()
    boxer1 = make_boxer("Ali")
    boxer2 = make_boxer("Tyson")

    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)

    assert len(ring.get_boxers()) == 2


def test_enter_ring_too_many():
    """Test that entering a third boxer raises a ValueError."""
    ring = RingModel()
    ring.enter_ring(make_boxer("Ali"))
    ring.enter_ring(make_boxer("Tyson"))

    with pytest.raises(ValueError, match="Ring is full"):
        ring.enter_ring(make_boxer("Rocky"))


def test_enter_ring_wrong_type():
    """Test that entering a non-Boxer raises TypeError."""
    ring = RingModel()

    with pytest.raises(TypeError):
        ring.enter_ring("NotABoxer")  # type: ignore


def test_clear_ring():
    """Test that the ring clears properly."""
    ring = RingModel()
    ring.enter_ring(make_boxer("Ali"))
    ring.enter_ring(make_boxer("Tyson"))

    ring.clear_ring()
    assert ring.get_boxers() == []


def test_fight_calls_update_stats(mocker):
    """Test that a fight calls update_boxer_stats and returns a winner."""
    ring = RingModel()

    boxer1 = make_boxer("Ali")
    boxer2 = make_boxer("Tyson")
    boxer2.id = 2  # Give them unique IDs

    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)

    mocker.patch("boxing.models.ring_model.get_random", return_value=0.3)
    mock_update = mocker.patch("boxing.models.ring_model.update_boxer_stats")

    winner = ring.fight()

    assert winner in ["Ali", "Tyson"]
    assert len(ring.get_boxers()) == 0  # Ring should be cleared
    mock_update.assert_called()
    assert mock_update.call_count == 2


def test_fight_not_enough_boxers():
    """Test that fight raises ValueError if less than 2 boxers in ring."""
    ring = RingModel()
    ring.enter_ring(make_boxer("Ali"))

    with pytest.raises(ValueError):
        ring.fight()
