# -*- coding: utf-8 -*-
import random
import unittest

import axelrod
from axelrod import MoranProcess
from axelrod.moran import fitness_proportionate_selection

from hypothesis import given, example, settings
from hypothesis.strategies import integers, lists, sampled_from, random_module, floats


class TestMoranProcess(unittest.TestCase):

    def test_fps(self):
        self.assertEqual(fitness_proportionate_selection([0, 0, 1]), 2)
        random.seed(1)
        self.assertEqual(fitness_proportionate_selection([1, 1, 1]), 0)
        self.assertEqual(fitness_proportionate_selection([1, 1, 1]), 2)

    def test_stochastic(self):
        p1, p2 = axelrod.Cooperator(), axelrod.Cooperator()
        mp = MoranProcess((p1, p2))
        self.assertFalse(mp._stochastic)
        p1, p2 = axelrod.Cooperator(), axelrod.Cooperator()
        mp = MoranProcess((p1, p2), noise=0.05)
        self.assertTrue(mp._stochastic)
        p1, p2 = axelrod.Cooperator(), axelrod.Random()
        mp = MoranProcess((p1, p2))
        self.assertTrue(mp._stochastic)

    def test_exit_condition(self):
        p1, p2 = axelrod.Cooperator(), axelrod.Cooperator()
        mp = MoranProcess((p1, p2))
        mp.play()
        self.assertEqual(len(mp), 1)

    def test_two_players(self):
        p1, p2 = axelrod.Cooperator(), axelrod.Defector()
        random.seed(5)
        mp = MoranProcess((p1, p2))
        mp.play()
        self.assertEqual(len(mp), 5)
        self.assertEqual(mp.winner, str(p2))

    def test_three_players(self):
        players = [axelrod.Cooperator(), axelrod.Cooperator(),
                   axelrod.Defector()]
        random.seed(5)
        mp = MoranProcess(players)
        mp.play()
        self.assertEqual(len(mp), 7)
        self.assertEqual(mp.winner, str(axelrod.Defector()))

    def test_four_players(self):
        players = [axelrod.Cooperator() for _ in range(3)]
        players.append(axelrod.Defector())
        random.seed(10)
        mp = MoranProcess(players)
        mp.play()
        self.assertEqual(len(mp), 9)
        self.assertEqual(mp.winner, str(axelrod.Defector()))

    @given(strategies=lists(sampled_from(axelrod.strategies),
                   min_size=2,  # Errors are returned if less than 2 strategies
                   max_size=5, unique=True),
           rm=random_module())
    @settings(max_examples=5, timeout=0)  # Very low number of examples

    # Two specific examples relating to cloning of strategies
    @example(strategies=[axelrod.BackStabber, axelrod.MindReader],
             rm=random.seed(0))
    @example(strategies=[axelrod.ThueMorse, axelrod.MindReader],
             rm=random.seed(0))
    def test_property_players(self, strategies, rm):
        """Hypothesis test that randomly checks players"""
        players = [s() for s in strategies]
        mp = MoranProcess(players)
        mp.play()
        self.assertIn(mp.winner, [str(p) for p in players])

    def test_reset(self):
        p1, p2 = axelrod.Cooperator(), axelrod.Defector()
        random.seed(8)
        mp = MoranProcess((p1, p2))
        mp.play()
        self.assertEqual(len(mp), 4)
        self.assertEqual(len(mp.score_history), 3)
        mp.reset()
        self.assertEqual(len(mp), 1)
        self.assertEqual(mp.winner, None)
        self.assertEqual(mp.score_history, [])
