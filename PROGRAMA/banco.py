"""Camada de dados do SIGESC: SQLite e regras básicas dos chamados."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

PRIORIDADES = ("Baixa", "Média", "Alta")
STATUS = ("Aberto", "Em atendimento", "Concluído")


class BancoChamados:
    def __init__(self, arquivo="chamados.db"):
        self.arquivo = str(Path(arquivo))
        self.criar_tabela()

    @contextmanager
    def conectar(self):
        conexao = sqlite3.connect(self.arquivo)
        conexao.row_factory = sqlite3.Row
        try:
            with conexao:
                yield conexao
        finally:
            conexao.close()

    def criar_tabela(self):
        with self.conectar() as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS chamados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    solicitante TEXT NOT NULL,
                    equipamento TEXT NOT NULL,
                    local TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    prioridade TEXT NOT NULL
                        CHECK (prioridade IN ('Baixa', 'Média', 'Alta')),
                    status TEXT NOT NULL DEFAULT 'Aberto'
                        CHECK (status IN ('Aberto', 'Em atendimento', 'Concluído')),
                    criado_em TEXT NOT NULL,
                    atualizado_em TEXT NOT NULL
                )
            """)

    @staticmethod
    def agora():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def cadastrar(self, titulo, solicitante, equipamento, local, descricao, prioridade):
        campos = [titulo, solicitante, equipamento, local, descricao]
        if not all(isinstance(valor, str) and valor.strip() for valor in campos):
            raise ValueError("Preencha todos os campos obrigatórios.")
        if prioridade not in PRIORIDADES:
            raise ValueError("Prioridade inválida.")

        instante = self.agora()
        with self.conectar() as conexao:
            cursor = conexao.execute("""
                INSERT INTO chamados
                (titulo, solicitante, equipamento, local, descricao,
                 prioridade, status, criado_em, atualizado_em)
                VALUES (?, ?, ?, ?, ?, ?, 'Aberto', ?, ?)
            """, (
                titulo.strip(), solicitante.strip(), equipamento.strip(),
                local.strip(), descricao.strip(), prioridade, instante, instante
            ))
            return cursor.lastrowid

    def listar(self, pesquisa=""):
        termo = pesquisa.strip()
        with self.conectar() as conexao:
            if termo:
                filtro = f"%{termo}%"
                linhas = conexao.execute("""
                    SELECT * FROM chamados
                    WHERE CAST(id AS TEXT) LIKE ? OR titulo LIKE ?
                       OR solicitante LIKE ? OR equipamento LIKE ? OR local LIKE ?
                    ORDER BY id DESC
                """, (filtro, filtro, filtro, filtro, filtro)).fetchall()
            else:
                linhas = conexao.execute(
                    "SELECT * FROM chamados ORDER BY id DESC"
                ).fetchall()
        return [dict(linha) for linha in linhas]

    def obter(self, numero):
        with self.conectar() as conexao:
            linha = conexao.execute(
                "SELECT * FROM chamados WHERE id = ?", (numero,)
            ).fetchone()
        return dict(linha) if linha else None

    def alterar_status(self, numero, novo_status):
        if novo_status not in STATUS:
            raise ValueError("Status inválido.")
        with self.conectar() as conexao:
            cursor = conexao.execute("""
                UPDATE chamados
                SET status = ?, atualizado_em = ?
                WHERE id = ?
            """, (novo_status, self.agora(), numero))
            return cursor.rowcount > 0
