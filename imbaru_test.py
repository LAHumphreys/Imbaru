from unittest import TestCase
from imbaru import Statue, State, SymbolType, Statement, SymbolValue, SymbolSet


def make_symbol_set(A, B, C) -> SymbolSet:
    return SymbolValue("A", A), SymbolValue("B", B), SymbolValue("C", C)

CIR=SymbolType.CIRCLE
TRI=SymbolType.TRIANGLE

class StatueTest(TestCase):

    def setUp(self):
        self.statue = Statue(symbols=(
            Statement(symbol="A", type=SymbolType.CIRCLE, state=State.UNKNOWN),
            Statement(symbol="B", type=SymbolType.CIRCLE, state=State.UNKNOWN),
            Statement(symbol="C", type=SymbolType.CIRCLE, state=State.UNKNOWN)))

    def validate_initial_state(self):
        self.assertTrue(self.statue.is_valid())
        self.assertFalse(self.statue.is_resolved())
        self.assertEqual(self.statue.count_states()[State.UNKNOWN], 3)
        self.assertEqual(self.statue.count_states()[State.TRUTH], 0)
        self.assertEqual(self.statue.count_states()[State.LIE], 0)

        self.assertEqual(self.statue.get_possible_solutions(), [
            make_symbol_set(CIR, TRI, TRI),
            make_symbol_set(TRI, CIR, TRI),
            make_symbol_set(TRI, TRI, CIR)
        ])

    def validate_full_resolved(self):
        self.assertTrue(self.statue.is_valid())
        self.assertTrue(self.statue.is_resolved())
        self.assertEqual(self.statue.count_states()[State.UNKNOWN], 0)
        self.assertEqual(self.statue.count_states()[State.TRUTH], 1)
        self.assertEqual(self.statue.count_states()[State.LIE], 2)

    def test_initial_sate(self):
        self.validate_initial_state()


    def test_resolve_true(self):
        self.assertTrue(self.statue.resolve_symbol("A", SymbolType.CIRCLE))
        self.validate_full_resolved()

        self.statue.reset()
        self.validate_initial_state()

    def test_resolve_double_true(self):
        self.assertTrue(self.statue.resolve_symbol("A", SymbolType.CIRCLE))
        self.validate_full_resolved()

        self.assertFalse(self.statue.resolve_symbol("B", SymbolType.CIRCLE))
        self.assertFalse(self.statue.is_valid())
        self.assertEqual(self.statue.get_possible_solutions(), [])

        self.statue.reset()
        self.validate_initial_state()

    def test_resolve_true_then_false(self):
        self.assertTrue(self.statue.resolve_symbol("A", SymbolType.CIRCLE))
        self.validate_full_resolved()

        self.assertFalse(self.statue.resolve_symbol("A", SymbolType.TRIANGLE))
        self.assertFalse(self.statue.is_valid())

        self.statue.reset()
        self.validate_initial_state()

    def test_resolve_false(self):
        self.assertTrue(self.statue.resolve_symbol("A", SymbolType.TRIANGLE))
        self.assertTrue(self.statue.is_valid())
        self.assertFalse(self.statue.is_resolved())
        self.assertEqual(self.statue.count_states()[State.UNKNOWN], 2)
        self.assertEqual(self.statue.count_states()[State.TRUTH], 0)
        self.assertEqual(self.statue.count_states()[State.LIE], 1)

        self.assertEqual(self.statue.get_possible_solutions(), [
            make_symbol_set(TRI, CIR, TRI),
            make_symbol_set(TRI, TRI, CIR)
        ])

        self.assertTrue(self.statue.resolve_symbol("B", SymbolType.TRIANGLE))
        self.assertTrue(self.statue.is_valid())
        self.assertEqual(self.statue.count_states()[State.UNKNOWN], 0)
        self.assertEqual(self.statue.count_states()[State.TRUTH], 1)
        self.assertEqual(self.statue.count_states()[State.LIE], 2)

        self.statue.reset()
        self.validate_initial_state()

    def test_resolve_tripple_false(self):
        self.assertTrue(self.statue.resolve_symbol("A", SymbolType.TRIANGLE))
        self.assertTrue(self.statue.is_valid())
        self.assertEqual(self.statue.count_states()[State.UNKNOWN], 2)
        self.assertEqual(self.statue.count_states()[State.TRUTH], 0)
        self.assertEqual(self.statue.count_states()[State.LIE], 1)

        self.assertTrue(self.statue.resolve_symbol("B", SymbolType.TRIANGLE))
        self.validate_full_resolved()

        self.assertFalse(self.statue.resolve_symbol("C", SymbolType.TRIANGLE))
        self.assertFalse(self.statue.is_valid())

        self.statue.reset()
        self.validate_initial_state()

    def test_resolved_possibilities(self):
        self.assertTrue(self.statue.resolve_symbol("A", SymbolType.CIRCLE))
        self.validate_full_resolved()
        solutions = self.statue.get_possible_solutions()
        self.assertEqual(len(solutions), 1)
        self.assertEqual(solutions[0], make_symbol_set(CIR, TRI, TRI))



