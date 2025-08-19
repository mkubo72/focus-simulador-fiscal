import unittest
import gui_utils
import fiscal_logic
import config

gui_utils.moeda = lambda v: f"R$ {v:.2f}"

class TestSimuladorFiscalAtual(unittest.TestCase):
    def test_industrializacao_sem_st(self):
        texto, difal, fcp = fiscal_logic.calcular_industrializacao({})
        self.assertIn("não gera ST ou DIFAL", texto)
        self.assertEqual(difal, 0.0)
        self.assertEqual(fcp, 0.0)

if __name__ == "__main__":
    unittest.main()
