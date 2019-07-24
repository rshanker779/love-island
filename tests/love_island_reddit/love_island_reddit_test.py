import unittest
from love_island_reddit.love_island_data import Constants


class LoveIslandRedditTest(unittest.TestCase):
    def test_regular_expression(self):
        reg_exp = Constants.episode_title_match
        self.assertIsNotNone(reg_exp.match("Episode 1 It kicks off"))
        self.assertIsNotNone(reg_exp.match("Episode 01 more more drama"))
        self.assertIsNotNone(reg_exp.match("Episode 123 Wow so much happens"))
        self.assertIsNone(reg_exp.match("Episode1 what a great show"))
        self.assertIsNone(reg_exp.match("What an Episode "))


if __name__ == "__main__":
    unittest.main()
