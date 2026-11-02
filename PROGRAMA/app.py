"""SIGESC: interface desktop para acompanhamento de chamados técnicos escolares.

Python 3.10+ | bibliotecas da distribuição padrão (tkinter, sqlite3).
Uso: python app.py [--demo]
"""
import argparse
import csv
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from banco import BancoChamados, PRIORIDADES, STATUS

AZUL = '#123D68'
NAVY = '#0B2847'
BG = '#F2F5F9'
TEXTO = '#192B40'
MUTED = '#5A6C80'
VERDE = '#08745F'

class Aplicativo(tk.Tk):
    def __init__(self, arquivo_banco=None, demonstracao=False):
        super().__init__()
        self.title('SIGESC | Central de Chamados de TI')
        self.geometry('1240x790')
        self.minsize(1020, 760)
        self.configure(bg=BG)
        base = Path(__file__).resolve().parent
        self.banco = BancoChamados(arquivo_banco or (base / ('chamados_demo.db' if demonstracao else 'chamados.db')))
        self.demonstracao = demonstracao
        self.vars = {k:tk.StringVar() for k in ('titulo','solicitante','equipamento','local')}
        self.prioridade = tk.StringVar(value='Média')
        self.pesquisa = tk.StringVar()
        self.filtro_status = tk.StringVar(value='Todos')
        self.status = tk.StringVar(value='Em atendimento')
        self.id_selecionado = None
        self._styles()
        self._layout()
        self.atualizar_lista()

    def _styles(self):
        sty = ttk.Style(self)
        if 'clam' in sty.theme_names(): sty.theme_use('clam')
        sty.configure('TFrame', background=BG)
        sty.configure('TLabel', background=BG, foreground=TEXTO, font=('Arial',10))
        sty.configure('Hint.TLabel', background=BG, foreground=MUTED, font=('Arial',9))
        sty.configure('TEntry', padding=7)
        sty.configure('TCombobox', padding=6)
        sty.configure('Primary.TButton', padding=(14,10), background=AZUL, foreground='white', font=('Arial',10,'bold'), borderwidth=0)
        sty.map('Primary.TButton', background=[('active','#1D5688')], foreground=[('active','white')])
        sty.configure('TButton', padding=(10,8), font=('Arial',9))
        sty.configure('Treeview', rowheight=34, background='white', fieldbackground='white', foreground=TEXTO, font=('Arial',9), borderwidth=0)
        sty.configure('Treeview.Heading', background='#E3EAF2', foreground=NAVY, font=('Arial',9,'bold'), padding=10)
        sty.map('Treeview', background=[('selected', '#D5E6F8')], foreground=[('selected', NAVY)])

    def _layout(self):
        head = tk.Frame(self,bg=NAVY,height=100)
        head.pack(fill='x')
        tk.Label(head,text='SIGESC',fg='white',bg=NAVY,font=('Arial',25,'bold')).pack(side='left',padx=(26,22),pady=24)
        tk.Frame(head,bg='#5F8BB5',width=2,height=47).pack(side='left',pady=22)
        desc=tk.Frame(head,bg=NAVY);desc.pack(side='left',padx=20,pady=18)
        tk.Label(desc,text='CENTRAL DE CHAMADOS DE TI',bg=NAVY,fg='white',font=('Arial',12,'bold')).pack(anchor='w')
        tk.Label(desc,text='Laboratório de Programação • Ambiente escolar simulado',bg=NAVY,fg='#BBD0E4',font=('Arial',9)).pack(anchor='w',pady=(5,0))
        tk.Label(head,text='DADOS FICTÍCIOS  •  DEMONSTRAÇÃO' if self.demonstracao else 'PROJETO ACADÊMICO',bg='#194E78',fg='white',padx=14,pady=7,font=('Arial',8,'bold')).pack(side='right',padx=26)

        kpis=tk.Frame(self,bg=BG);kpis.pack(fill='x',padx=24,pady=(18,14))
        self.kpis={}
        for nome,cor in [('Todos os chamados',AZUL),('Abertos','#B16A10'),('Em atendimento','#20639B'),('Concluídos',VERDE)]:
            card=tk.Frame(kpis,bg='white',highlightbackground='#DEE5ED',highlightthickness=1)
            card.pack(side='left',fill='x',expand=True,padx=(0,11))
            tk.Frame(card,bg=cor,width=5).pack(side='left',fill='y')
            info=tk.Frame(card,bg='white');info.pack(side='left',padx=14,pady=12)
            tk.Label(info,text=nome.upper(),bg='white',fg=MUTED,font=('Arial',8,'bold')).pack(anchor='w')
            numero=tk.Label(info,text='0',bg='white',fg=NAVY,font=('Arial',23,'bold'))
            numero.pack(anchor='w');self.kpis[nome]=numero

        main=tk.Frame(self,bg=BG);main.pack(fill='both',expand=True,padx=24,pady=(0,20))
        main.grid_columnconfigure(1,weight=1)
        main.grid_rowconfigure(0,weight=1)
        form=tk.Frame(main,bg='white',highlightbackground='#DEE5ED',highlightthickness=1)
        form.grid(row=0,column=0,sticky='ns',padx=(0,14));form.grid_columnconfigure(0,weight=1)
        tk.Label(form,text='NOVO CHAMADO',bg='white',fg=NAVY,font=('Arial',13,'bold')).grid(row=0,column=0,sticky='w',padx=18,pady=(18,3))
        tk.Label(form,text='Registre uma solicitação de suporte.',bg='white',fg=MUTED,font=('Arial',9)).grid(row=1,column=0,sticky='w',padx=18,pady=(0,11))
        campos=[('titulo','Título do problema'),('solicitante','Solicitante'),('equipamento','Equipamento'),('local','Sala / localização')]
        r=2
        for chave,rotulo in campos:
            tk.Label(form,text=rotulo,bg='white',fg=TEXTO,font=('Arial',9,'bold')).grid(row=r,column=0,sticky='w',padx=18,pady=(4,2));r+=1
            ttk.Entry(form,textvariable=self.vars[chave],width=31).grid(row=r,column=0,sticky='ew',padx=18);r+=1
        tk.Label(form,text='Prioridade',bg='white',fg=TEXTO,font=('Arial',9,'bold')).grid(row=r,column=0,sticky='w',padx=18,pady=(6,2));r+=1
        ttk.Combobox(form,textvariable=self.prioridade,values=PRIORIDADES,state='readonly',width=28).grid(row=r,column=0,sticky='ew',padx=18);r+=1
        tk.Label(form,text='Descrição do problema',bg='white',fg=TEXTO,font=('Arial',9,'bold')).grid(row=r,column=0,sticky='w',padx=18,pady=(6,2));r+=1
        self.descricao=tk.Text(form,width=29,height=3,wrap='word',font=('Arial',10),relief='solid',bd=1)
        self.descricao.grid(row=r,column=0,sticky='ew',padx=18);r+=1
        ttk.Button(form,text='+  Cadastrar chamado',style='Primary.TButton',command=self.cadastrar).grid(row=r,column=0,sticky='ew',padx=18,pady=(10,4));r+=1
        ttk.Button(form,text='Limpar formulário',command=self.limpar_formulario).grid(row=r,column=0,sticky='ew',padx=18,pady=(0,16))

        panel=tk.Frame(main,bg='white',highlightbackground='#DEE5ED',highlightthickness=1)
        panel.grid(row=0,column=1,sticky='nsew');panel.grid_columnconfigure(0,weight=1);panel.grid_rowconfigure(3,weight=1)
        tk.Label(panel,text='CHAMADOS REGISTRADOS',bg='white',fg=NAVY,font=('Arial',13,'bold')).grid(row=0,column=0,columnspan=2,sticky='w',padx=16,pady=(18,12))
        filtros=tk.Frame(panel,bg='white');filtros.grid(row=1,column=0,columnspan=2,sticky='ew',padx=16,pady=(0,13))
        filtros.grid_columnconfigure(0,weight=1)
        ttk.Entry(filtros,textvariable=self.pesquisa).grid(row=0,column=0,sticky='ew',padx=(0,8))
        ttk.Combobox(filtros,textvariable=self.filtro_status,values=('Todos',)+STATUS,state='readonly',width=18).grid(row=0,column=1,sticky='e')
        tk.Label(panel,text='Pesquise por número, título, solicitante, equipamento ou local',bg='white',fg=MUTED,font=('Arial',8)).grid(row=2,column=0,columnspan=2,sticky='w',padx=17,pady=(0,8))
        cols=('id','titulo','solicitante','equipamento','prioridade','status')
        self.tabela=ttk.Treeview(panel,columns=cols,show='headings',selectmode='browse')
        for chave,nome,largura in zip(cols,('Nº','Problema','Solicitante','Equip.','Prioridade','Situação'),(46,220,125,105,85,125)):
            self.tabela.heading(chave,text=nome)
            self.tabela.column(chave,width=largura,minwidth=45,stretch=chave in ('titulo','solicitante'))
        self.tabela.grid(row=3,column=0,sticky='nsew',padx=(16,0))
        bar=ttk.Scrollbar(panel,orient='vertical',command=self.tabela.yview)
        bar.grid(row=3,column=1,sticky='ns',padx=(0,16))
        self.tabela.configure(yscrollcommand=bar.set)
        self.tabela.bind('<<TreeviewSelect>>',self.selecionar)
        rod=tk.Frame(panel,bg='white');rod.grid(row=4,column=0,columnspan=2,sticky='ew',padx=16,pady=(13,8))
        tk.Label(rod,text='Atualizar situação:',bg='white',fg=TEXTO,font=('Arial',9,'bold')).pack(side='left',padx=(0,8))
        ttk.Combobox(rod,textvariable=self.status,values=STATUS,state='readonly',width=17).pack(side='left')
        ttk.Button(rod,text='Salvar status',command=self.salvar_status).pack(side='left',padx=7)
        ttk.Button(rod,text='Ver detalhes',command=self.ver_detalhes).pack(side='left')
        rod2=tk.Frame(panel,bg='white');rod2.grid(row=5,column=0,columnspan=2,sticky='ew',padx=16,pady=(0,12))
        self.contador=tk.Label(rod2,text='',bg='white',fg=MUTED,font=('Arial',9));self.contador.pack(side='left')
        ttk.Button(rod2,text='Exportar CSV',command=self.exportar_csv).pack(side='right')
        self.pesquisa.trace_add('write',lambda *_:self.atualizar_lista())
        self.filtro_status.trace_add('write',lambda *_:self.atualizar_lista())

    def cadastrar(self):
        dados={k:v.get() for k,v in self.vars.items()}
        try:
            numero=self.banco.cadastrar(titulo=dados['titulo'],solicitante=dados['solicitante'],equipamento=dados['equipamento'],local=dados['local'],descricao=self.descricao.get('1.0','end-1c'),prioridade=self.prioridade.get())
        except ValueError as e:
            messagebox.showwarning('Dados incompletos',str(e));return
        except Exception as e:
            messagebox.showerror('Erro no banco de dados',str(e));return
        self.limpar_formulario();self.atualizar_lista()
        messagebox.showinfo('Cadastro realizado',f'Chamado #{numero:04d} cadastrado com sucesso!')

    def limpar_formulario(self):
        for v in self.vars.values():v.set('')
        self.prioridade.set('Média');self.descricao.delete('1.0','end')

    def atualizar_lista(self):
        if not hasattr(self,'tabela'):return
        self.id_selecionado=None
        for item in self.tabela.get_children():self.tabela.delete(item)
        all_rows=self.banco.listar(); termo=self.pesquisa.get().strip()
        filt=self.filtro_status.get()
        rows=self.banco.listar(termo)
        if filt!='Todos':rows=[r for r in rows if r['status']==filt]
        for row in rows:
            self.tabela.insert('','end',values=(f"{row['id']:04d}",row['titulo'],row['solicitante'],row['equipamento'],row['prioridade'],row['status']))
        self.contador.config(text=f'{len(rows)} chamado(s) exibido(s)')
        total=len(all_rows)
        self.kpis['Todos os chamados'].config(text=str(total))
        for status,label in [('Aberto','Abertos'),('Em atendimento','Em atendimento'),('Concluído','Concluídos')]:
            self.kpis[label].config(text=str(sum(r['status']==status for r in all_rows)))

    def selecionar(self,_ev=None):
        sel=self.tabela.selection()
        if not sel: self.id_selecionado=None;return
        self.id_selecionado=int(self.tabela.item(sel[0],'values')[0])
        c=self.banco.obter(self.id_selecionado)
        if c:self.status.set(c['status'])

    def salvar_status(self):
        if self.id_selecionado is None:
            messagebox.showwarning('Atenção','Selecione um chamado na lista.');return
        try: ok=self.banco.alterar_status(self.id_selecionado,self.status.get())
        except ValueError as e:messagebox.showwarning('Status inválido',str(e));return
        if ok:
            self.atualizar_lista();messagebox.showinfo('Atualizado','Situação do chamado atualizada.')
        else:messagebox.showerror('Não encontrado','Chamado não localizado.')

    def ver_detalhes(self):
        if self.id_selecionado is None:
            messagebox.showwarning('Atenção','Selecione um chamado na lista.');return
        c=self.banco.obter(self.id_selecionado)
        if not c:messagebox.showerror('Não encontrado','Chamado não localizado.');return
        s=(f"CHAMADO #{c['id']:04d}\n\nTítulo: {c['titulo']}\nSolicitante: {c['solicitante']}\nEquipamento: {c['equipamento']}\nLocal: {c['local']}\nPrioridade: {c['prioridade']}\nSituação: {c['status']}\nAbertura: {c['criado_em']}\nÚltima atualização: {c['atualizado_em']}\n\nDESCRIÇÃO\n{c['descricao']}")
        win=tk.Toplevel(self);win.title(f"Chamado #{c['id']:04d} | Detalhes");win.geometry('620x460')
        txt=tk.Text(win,wrap='word',padx=18,pady=16,font=('Arial',11));txt.pack(fill='both',expand=True)
        txt.insert('1.0',s);txt.config(state='disabled')
        ttk.Button(win,text='Fechar',command=win.destroy).pack(pady=10)

    def exportar_csv(self):
        rows=self.banco.listar(self.pesquisa.get())
        if self.filtro_status.get()!='Todos': rows=[r for r in rows if r['status']==self.filtro_status.get()]
        if not rows:messagebox.showwarning('Sem registros','Nenhum chamado para exportar.');return
        nome=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('Arquivos CSV','*.csv')],initialfile='chamados_sigesc.csv')
        if not nome:return
        with open(nome,'w',encoding='utf-8-sig',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=list(rows[0].keys()),delimiter=';')
            wr.writeheader();wr.writerows(rows)
        messagebox.showinfo('Exportação concluída','Arquivo CSV salvo.')

if __name__=='__main__':
    cli=argparse.ArgumentParser()
    cli.add_argument('--demo',action='store_true',help='Usar banco de dados fictício da demonstração')
    a=cli.parse_args()
    Aplicativo(demonstracao=a.demo).mainloop()
