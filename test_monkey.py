import random
import unittest

from monkey import choose_victim


class ChooseVictimTests(unittest.TestCase):
    def test_returns_none_when_nothing_to_kill(self):
        self.assertIsNone(choose_victim([]))

    def test_picks_one_of_the_given_pids(self):
        pids = [101, 202, 303]
        self.assertIn(choose_victim(pids, random.Random(42)), pids)


if __name__ == "__main__":
    unittest.main()
