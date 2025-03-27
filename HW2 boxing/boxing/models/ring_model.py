import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to simulate a boxing ring where two boxers can fight.

    Attributes:
        ring (List[Boxer]): A list containing up to two boxers currently in the ring.
    """
    def __init__(self):
        """
        Initializes the RingModel with an empty ring.
        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between two boxers currently in the ring.

        The fight uses a logistic function based on skill difference to determine the winner.
        Updates win/loss statistics accordingly and clears the ring after the fight.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If fewer than two boxers are in the ring.
        """
        if len(self.ring) < 2:
            logger.error("Attempted to fight with less than two boxers in the ring")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Starting fight between {boxer_1.name} and {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.debug(f"{boxer_1.name}'s skill: {skill_1}, {boxer_2.name}'s skill: {skill_2}")

        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()
        logger.debug(f"Random number received: {random_number}, threshold: {normalized_delta}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        logger.info(f"Winner: {winner.name}, Loser: {loser.name}")

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.info(f"Updated stats for winner {winner.name} and loser {loser.name}")

        self.clear_ring()
        return winner.name

    def clear_ring(self):
        """
        Removes all boxers from the ring.
        """
        if not self.ring:
            logger.warning("Tried to clear an already empty ring")
            return
        logger.info("Clearing the ring")
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add.

        Raises:
            TypeError: If the argument is not a Boxer instance.
            ValueError: If the ring already contains two boxers.
        """
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Ring is full, cannot add more boxers")
            raise ValueError("Ring is full, cannot add more boxers.")

        logger.info(f"Adding boxer {boxer.name} to the ring")
        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
        Retrieves the list of boxers currently in the ring.

        Returns:
            List[Boxer]: The list of boxers in the ring (max 2).
        """
        logger.info(f"Retrieving current boxers in the ring: {[b.name for b in self.ring]}")
        return self.ring
    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates a boxer's fighting skill using an arbitrary formula.

        Args:
            boxer (Boxer): The boxer to evaluate.

        Returns:
            float: The calculated skill score.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        logger.debug(f"Calculated skill for {boxer.name}: {skill}")
        return skill
