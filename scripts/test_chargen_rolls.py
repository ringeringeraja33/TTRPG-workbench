import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from dicebot import execute, inspect


class ChargenRollTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = Path(temp.name) / 'cards.sqlite'

    def send(self, command, owner='p'):
        revision = inspect(self.db, 's', owner)['revision']
        return execute(self.db, 's', owner, command, str(revision), revision)['result']

    def test_minimum_and_maximum_formulas(self):
        for face, low, high, total in [(0, 15, 40, 195), (5, 90, 90, 720)]:
            with patch('dice.secrets.randbelow', return_value=face):
                candidate = self.send('.coc')['candidates'][0]
            for name in ('STR', 'CON', 'DEX', 'APP', 'POW', 'LUCK'):
                self.assertEqual(candidate['stats'][name], low)
            for name in ('SIZ', 'INT', 'EDU'):
                self.assertEqual(candidate['stats'][name], high)
            self.assertEqual(candidate['total_without_luck'], total)
            self.assertEqual(candidate['total_with_luck'], total + low)
            self.assertEqual(candidate['rolls']['EDU']['raw'], [face + 1] * 2)
            self.assertEqual(candidate['rolls']['EDU']['modifier'], 6)

    def test_bounds_no_randomness_or_state_on_invalid(self):
        with patch('dicebot.roll') as rng:
            for command in ('.coc0', '.coc11', '.coc-1', '.coc1.5'):
                with self.assertRaises(ValueError): self.send(command)
            rng.assert_not_called()
        self.assertEqual(inspect(self.db, 's', 'p')['revision'], 0)

    def test_retry_and_saved_batches(self):
        with patch('dicebot.roll', return_value={'total': 10, 'raw': [3, 3, 4]}) as rng:
            first = execute(self.db, 's', 'p', '.coc5', 'roll', 0)
            self.assertEqual(first, execute(self.db, 's', 'p', '.coc5', 'roll', 0))
            self.assertEqual(rng.call_count, 45)
        self.assertEqual(self.send('.coc show b1'), first['result'])
        self.send('.coc')
        self.assertEqual(self.send('.coc show b1'), first['result'])
        with self.assertRaises(ValueError): self.send('.coc show b1', owner='other')

    def test_selection_preserves_original_and_existing_cards(self):
        rolled = self.send('.coc2')
        self.send('.card new old Original')
        self.send('.st HP12')
        self.send('.coc take b1 2 new 调查员')
        self.assertEqual(self.send('.st show')['stats'], rolled['candidates'][1]['stats'])
        self.send('.st STR=50')
        state = inspect(self.db, 's', 'p')
        self.assertEqual(state['cards']['old']['stats'], {'HP': 12})
        self.assertEqual(state['cards']['new']['creation']['original'], rolled['candidates'][1])
        self.assertEqual(state['chargen_batches']['b1'], rolled)
        for command in ('.coc take b1 1 old Overwrite', '.coc take b1 0 bad Bad', '.coc take b1 3 bad Bad'):
            with self.assertRaises(ValueError): self.send(command)
            self.assertEqual(inspect(self.db, 's', 'p'), state)


if __name__ == '__main__':
    unittest.main()
