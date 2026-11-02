"""Testes automatizados da camada de dados. Execute: python testar_banco.py"""

import tempfile
import unittest
from pathlib import Path

from banco import BancoChamados


class TestesBancoChamados(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.caminho = Path(self.pasta.name) / "teste.db"
        self.banco = BancoChamados(self.caminho)

    def tearDown(self):
        self.pasta.cleanup()

    def criar(self, titulo="Computador sem internet"):
        return self.banco.cadastrar(
            titulo, "Maria", "PC-05", "Laboratório 1",
            "Sem conexão de rede", "Alta"
        )

    def test_cadastro_e_consulta(self):
        numero = self.criar()
        chamado = self.banco.obter(numero)
        self.assertEqual(chamado["titulo"], "Computador sem internet")
        self.assertEqual(chamado["status"], "Aberto")
        self.assertEqual(chamado["prioridade"], "Alta")

    def test_multiplos_ids(self):
        self.assertNotEqual(self.criar(), self.criar("Impressora falhando"))

    def test_campos_vazios(self):
        with self.assertRaises(ValueError):
            self.banco.cadastrar("", "Maria", "PC-05", "Lab", "Falha", "Alta")

    def test_prioridade_invalida(self):
        with self.assertRaises(ValueError):
            self.banco.cadastrar("Problema", "Maria", "PC-05", "Lab", "Falha", "Urgentíssima")

    def test_pesquisa(self):
        self.criar()
        self.criar("Impressora com problema")
        lista = self.banco.listar("impressora")
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0]["titulo"], "Impressora com problema")

    def test_alteracao_de_status(self):
        numero = self.criar()
        self.assertTrue(self.banco.alterar_status(numero, "Em atendimento"))
        self.assertEqual(self.banco.obter(numero)["status"], "Em atendimento")
        self.banco.alterar_status(numero, "Concluído")
        self.assertEqual(self.banco.obter(numero)["status"], "Concluído")

    def test_status_invalido(self):
        numero = self.criar()
        with self.assertRaises(ValueError):
            self.banco.alterar_status(numero, "Desconhecido")

    def test_id_inexistente(self):
        self.assertFalse(self.banco.alterar_status(9999, "Concluído"))
        self.assertIsNone(self.banco.obter(9999))

    def test_persistencia_apos_nova_conexao(self):
        numero = self.criar()
        outro_acesso = BancoChamados(self.caminho)
        self.assertEqual(outro_acesso.obter(numero)["equipamento"], "PC-05")

    def test_busca_trata_texto_literal_com_seguranca(self):
        self.criar()
        self.assertEqual(self.banco.listar("' OR 1=1 --"), [])
        self.assertEqual(len(self.banco.listar()), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
