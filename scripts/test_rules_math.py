"""Regression cases for documented examples and cross-system traps."""
import unittest
from fractions import Fraction
from rules_math import (dnd_modifier, dnd_point_cost, dnd_attack_probability,
                        dnd_damage, coc_thresholds, coc_injury, gumshoe_probability)


class RuleExamples(unittest.TestCase):
    def test_negative_modifier_rounding(self):
        self.assertEqual(dnd_modifier(9), -1)
        self.assertEqual(dnd_modifier(17), 3)

    def test_point_buy_budget(self):
        self.assertEqual(dnd_point_cost([15, 14, 13, 12, 10, 8]), 27)
        self.assertGreater(dnd_point_cost([15] * 6), 27)
        with self.assertRaises(ValueError):
            dnd_point_cost([17, 14, 14, 8, 12, 10])

    def test_advantage_and_cancellation(self):
        self.assertEqual(dnd_attack_probability(5, 16), Fraction(1, 2))
        self.assertEqual(dnd_attack_probability(5, 16, advantage=True), Fraction(3, 4))
        self.assertEqual(dnd_attack_probability(5, 16, disadvantage=True), Fraction(1, 4))
        self.assertEqual(dnd_attack_probability(5, 16, advantage=True, disadvantage=True), Fraction(1, 2))

    def test_attack_natural_limits(self):
        self.assertEqual(dnd_attack_probability(100, 1), Fraction(19, 20))
        self.assertEqual(dnd_attack_probability(-100, 100), Fraction(1, 20))

    def test_resistance_order(self):
        self.assertEqual(dnd_damage(23, 4, resistance=True, vulnerability=True), 18)
        self.assertEqual(dnd_damage(2, 4, resistance=True), 0)

    def test_coc_floor_thresholds(self):
        self.assertEqual(coc_thresholds(65), (65, 32, 13))
        self.assertEqual(coc_thresholds(51), (51, 25, 10))

    def test_single_blow_not_accumulation(self):
        hp, major, _ = coc_injury(12, 12, 3)
        self.assertEqual(coc_injury(12, hp, 3, major=major), (6, False, 'injured'))
        self.assertEqual(coc_injury(12, 12, 6), (6, True, 'major_wound_requires_CON'))

    def test_odd_hp_major_boundary(self):
        self.assertFalse(coc_injury(15, 15, 7)[1])
        self.assertTrue(coc_injury(15, 15, 8)[1])

    def test_official_fatal_equality(self):
        self.assertEqual(coc_injury(12, 12, 12)[2], 'dead')

    def test_zero_hp_history(self):
        self.assertEqual(coc_injury(12, 2, 3, major=False)[2], 'unconscious')
        self.assertEqual(coc_injury(12, 2, 3, major=True)[2], 'dying')

    def test_coc_character_budgets(self):
        occupation = [35, 25, 50, 29, 40, 30, 35, 16, 20]
        interest = [10, 0, 10, 0, 10, 20, 10, 14, 0, 25, 31, 20]
        self.assertEqual(sum(occupation), 70 * 4)
        self.assertEqual(sum(interest), 75 * 2)

    def test_gumshoe_spending(self):
        self.assertEqual(gumshoe_probability(5, 0), Fraction(1, 3))
        self.assertEqual(gumshoe_probability(5, 2), Fraction(2, 3))
        self.assertEqual(gumshoe_probability(5, 4), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
