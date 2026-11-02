SIGESC - Sistema de Gerenciamento de Chamados Escolares
Projeto Integrador de Laboratório de Programação - UNISA - 2026

REQUISITOS: Python 3.10 ou superior, com Tkinter instalado.
NAO PRECISA INSTALAR BIBLIOTECAS EXTRAS.

COMO ABRIR NO WINDOWS:
1) Extraia o ZIP inteiro em uma pasta comum.
2) Clique duas vezes em ABRIR_DEMONSTRACAO.bat para ver chamados ficticios.
3) Clique duas vezes em INICIAR_SIGESC.bat para trabalhar em um banco novo e vazio.
4) Para executar os testes clique em EXECUTAR_TESTES.bat.

COMO ABRIR NO TERMINAL:
   py app.py --demo
   py app.py
   py -m unittest discover -p "testar_*.py" -v

Os dados de exemplo do modo demonstracao sao 100% ficticios.
As informacoes ficam em chamados.db (uso normal) e chamados_demo.db (demo).
Nunca compartilhe dados reais de outras pessoas sem autorizacao.

ARQUIVOS:
app.py = janelas e interface grafica
banco.py = banco SQLite, consultas e validacoes
testar_banco.py = testes automatizados
chamados_demo.db = 8 registros ficticios apenas para demonstracao

LIMITACOES: e' um prototipo local: nao possui login, rede nem controle de acesso.
Evite dados sensiveis. Nao foi implantado em uma escola real.
