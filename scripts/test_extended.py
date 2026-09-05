import unittest
from rules_extended import (coc_volley_plan, coc_volley_hits, dnd_slot_cast,
                            fate_absorb, fate_recovery, blades_vice, blades_downtime_cost)


class ExtendedRules(unittest.TestCase):
    def test_declared_partial_volleys(self):
        p = coc_volley_plan(63, [4, 4, 4], 15, waste=2)
        self.assertEqual((p['spent'], p['remaining']), (14, 1))
        self.assertEqual([x['penalty_dice'] for x in p['volleys']], [0, 1, 2])

    def test_auto_difficulty_and_ammo(self):
        p = coc_volley_plan(60, [3]*7, 21)
        self.assertEqual([x['difficulty'] for x in p['volleys']],
                         ['regular', 'regular', 'regular', 'hard', 'extreme', 'critical', 'impossible'])
        with self.assertRaises(ValueError):
            coc_volley_plan(60, [6, 6], 12, 1)
        with self.assertRaises(ValueError):
            coc_volley_plan(60, [7], 20)

    def test_impale_and_extreme_range(self):
        self.assertEqual(coc_volley_hits(5, 'extreme'), {'normal': 3, 'impaling': 2})
        self.assertEqual(coc_volley_hits(5, 'extreme', 'extreme'), {'normal': 2, 'impaling': 0})
        self.assertEqual(coc_volley_hits(5, 'regular', 'hard')['normal'], 0)
        with self.assertRaises(ValueError):
            coc_volley_hits(5, 'critical')

    def test_spell_turn_not_round(self):
        used = dnd_slot_cast('r1.pc', [], True)
        with self.assertRaises(ValueError):
            dnd_slot_cast('r1.pc', used, True)
        self.assertEqual(dnd_slot_cast('r1.pc', used, False), used)
        self.assertEqual(len(dnd_slot_cast('r1.enemy', used, True)), 2)

    def test_consequences_and_healing(self):
        self.assertFalse(fate_absorb(7, 1, [2, 4])['taken_out'])
        self.assertTrue(fate_absorb(8, 1, [2, 4])['taken_out'])
        self.assertEqual(fate_recovery(4, True), {'difficulty': 6, 'wait_after_treatment': 'one full session'})
        with self.assertRaises(ValueError):
            fate_absorb(4, 0, [2, 2])

    def test_vice_exact_clear_and_overindulgence(self):
        self.assertFalse(blades_vice(3, 3)['overindulgence'])
        self.assertTrue(blades_vice(2, 3)['overindulgence'])
        self.assertEqual(blades_downtime_cost(3), 1)
        self.assertEqual(blades_downtime_cost(3, True), 2)

    def test_no_boolean_numbers(self):
        with self.assertRaises(ValueError):
            blades_vice(True, 3)


if __name__ == '__main__':
    unittest.main()
