import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, shutil, webbrowser, zipfile
from datetime import datetime
import config
import data_manager
import fiscal_logic
import pdf_generator
import gui_utils
import tempfile
import subprocess


class VendedoresEditor(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Cadastro de Vendedores")
        self.geometry("450x460")
        self.transient(master)
        self.grab_set()
        self.focus_set()
        self.current_editing_vendedor_idx = None
        self._criar_widgets()
        self._carregar_vendedores_na_tabela()

    def _criar_widgets(self):
        tree_frame = ttk.Frame(self)
        tree_frame.pack(padx=10, pady=10, fill='both', expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=('Nome', 'Código'), show='headings')
        self.tree.heading('Nome', text='Nome do Vendedor')
        self.tree.heading('Código', text='Código')
        self.tree.column('Nome', width=200)
        self.tree.column('Código', width=100, stretch=tk.NO)
        self.tree.pack(fill='both', expand=True, side='left')
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._carregar_para_edicao)
        input_frame = ttk.LabelFrame(self, text="Adicionar/Editar Vendedor")
        input_frame.pack(padx=10, pady=5, fill='x')
        tk.Label(input_frame, text="Nome:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
        self.entry_nome = tk.Entry(input_frame, width=30)
        self.entry_nome.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        tk.Label(input_frame, text="Código:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.entry_codigo = tk.Entry(input_frame, width=10)
        self.entry_codigo.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        tk.Label(input_frame, text="Email:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.entry_email = tk.Entry(input_frame, width=30)
        self.entry_email.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        tk.Label(input_frame, text="Celular/Whats:").grid(row=3, column=0, sticky='e', padx=5, pady=2)
        self.entry_celular = tk.Entry(input_frame, width=30)
        self.entry_celular.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        self.btn_add_save = tk.Button(input_frame, text="Adicionar Vendedor",
                                      command=self._adicionar_ou_salvar_vendedor, bg="#4CAF50", fg="white")
        self.btn_add_save.grid(row=4, column=0, columnspan=2, pady=5, sticky='ew')
        btn_remover = tk.Button(input_frame, text="Remover Vendedor Selecionado", command=self._remover_vendedor,
                                bg="#D62828", fg="white")
        btn_remover.grid(row=5, column=0, columnspan=2, pady=5, sticky='ew')

    def _carregar_vendedores_na_tabela(self):
        self.tree.delete(*self.tree.get_children())
        for vendedor in config.vendedores_cadastrados:
            self.tree.insert('', tk.END, values=(vendedor['nome'], vendedor['codigo']))

    def _adicionar_ou_salvar_vendedor(self):
        nome = self.entry_nome.get().strip()
        codigo = self.entry_codigo.get().strip()
        email = self.entry_email.get().strip()
        celular = self.entry_celular.get().strip()
        if not nome or not codigo:
            messagebox.showerror("Erro", "Nome e Código são obrigatórios.", parent=self)
            return
        vendedor_data = {'nome': nome, 'codigo': codigo, 'email': email, 'celular': celular}
        if self.current_editing_vendedor_idx is not None:
            config.vendedores_cadastrados[self.current_editing_vendedor_idx] = vendedor_data
            self.current_editing_vendedor_idx = None
            self.btn_add_save.config(text="Adicionar Vendedor", bg="#4CAF50")
        else:
            if any(v['codigo'] == codigo for v in config.vendedores_cadastrados):
                messagebox.showerror("Erro", "Código de vendedor já existe.", parent=self)
                return
            config.vendedores_cadastrados.append(vendedor_data)
        data_manager.salvar_tudo()
        self.entry_nome.delete(0, tk.END)
        self.entry_codigo.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_celular.delete(0, tk.END)
        self._carregar_vendedores_na_tabela()

    def _remover_vendedor(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um vendedor para remover.", parent=self)
            return
        if messagebox.askyesno("Confirmar Remoção", "Tem certeza que deseja remover o vendedor selecionado?",
                               parent=self):
            values = self.tree.item(selected_item, 'values')
            config.vendedores_cadastrados[:] = [v for v in config.vendedores_cadastrados if
                                                not (v['nome'] == values[0] and v['codigo'] == values[1])]
            data_manager.salvar_tudo()
            self._carregar_vendedores_na_tabela()
            self.entry_nome.delete(0, tk.END)
            self.entry_codigo.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_celular.delete(0, tk.END)
            self.current_editing_vendedor_idx = None
            self.btn_add_save.config(text="Adicionar Vendedor", bg="#4CAF50")

    def _carregar_para_edicao(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return
        values = self.tree.item(selected_item, 'values')
        vendedor_data = next((v for v in config.vendedores_cadastrados if v['codigo'] == values[1]), None)
        if vendedor_data:
            self.entry_nome.delete(0, tk.END);
            self.entry_nome.insert(0, vendedor_data['nome'])
            self.entry_codigo.delete(0, tk.END);
            self.entry_codigo.insert(0, vendedor_data['codigo'])
            self.entry_email.delete(0, tk.END);
            self.entry_email.insert(0, vendedor_data.get('email', ''))
            self.entry_celular.delete(0, tk.END);
            self.entry_celular.insert(0, vendedor_data.get('celular', ''))
            self.current_editing_vendedor_idx = config.vendedores_cadastrados.index(vendedor_data)
            self.btn_add_save.config(text="Salvar Edição", bg="#0070C0")


class ParametrosNacionaisEditor(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Editar Parâmetros Nacionais (NCM, IPI, IBPT)")
        self.geometry("900x400")
        self.transient(master)
        self.grab_set()
        self.focus_set()
        self.edit_entry = None
        self._create_widgets()
        self._carregar_parametros_na_tabela()

    def _create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(top_frame, text="Validade da Tabela IBPT (AAAA-MM-DD):").pack(side=tk.LEFT, padx=(0, 5))
        self.validade_var = tk.StringVar(value=config.ibpt_validade)
        self.entry_validade = tk.Entry(top_frame, textvariable=self.validade_var, width=12)
        self.entry_validade.pack(side=tk.LEFT)
        tk.Label(top_frame, text="(Dê um duplo-clique na tabela para editar)").pack(side=tk.LEFT, padx=(20, 0))
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.colunas = ('CF', 'Descrição', 'NCM', 'IPI (%)', 'IBPT Fed (%)', 'IBPT Est (%)')
        self.tree = ttk.Treeview(tree_frame, columns=self.colunas, show='headings')
        for col in self.colunas:
            self.tree.heading(col, text=col)
            if col == 'Descrição':
                self.tree.column(col, width=250)
            elif col == 'NCM':
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=80, anchor='center')
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind('<Double-1>', self._on_treeview_double_click)
        btn_salvar_fechar = tk.Button(self, text="Salvar Tudo e Fechar", command=self._salvar_tudo_e_fechar,
                                      bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_salvar_fechar.pack(pady=10)

    def _carregar_parametros_na_tabela(self):
        self.tree.delete(*self.tree.get_children())
        for cf_val in config.cfs:
            self.tree.insert('', tk.END, iid=cf_val, values=(
                cf_val,
                config.descricoes.get(cf_val, ''),
                config.cf_to_ncm.get(cf_val, ''),
                f"{config.cf_dict.get(cf_val, 0.0):.2f}",
                f"{config.ibpt_fed.get(cf_val, 0.0):.2f}",
                f"{config.ibpt_est.get(cf_val, 0.0):.2f}"
            ))

    def _on_treeview_double_click(self, event):
        if self.edit_entry: self.edit_entry.destroy()
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        x, y, width, height = self.tree.bbox(item_id, column_id)
        value = self.tree.set(item_id, column_id)
        column_index = int(column_id.replace('#', '')) - 1
        column_name = self.colunas[column_index]
        self.edit_entry = ttk.Entry(self)
        self.edit_entry.place(x=x, y=y, width=width, height=height)
        self.edit_entry.insert(0, value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus_set()
        self.edit_entry.bind("<Return>", lambda e: self._salvar_edicao(item_id, column_name))
        self.edit_entry.bind("<FocusOut>", lambda e: self._salvar_edicao(item_id, column_name))

    def _salvar_edicao(self, item_id, column_name):
        if not self.edit_entry: return
        try:
            new_value = self.edit_entry.get()
            if column_name in ['IPI (%)', 'IBPT Fed (%)', 'IBPT Est (%)']:
                new_value_float = float(new_value.replace(',', '.'))
                if column_name == 'IPI (%)':
                    config.cf_dict[item_id] = new_value_float
                elif column_name == 'IBPT Fed (%)':
                    config.ibpt_fed[item_id] = new_value_float
                elif column_name == 'IBPT Est (%)':
                    config.ibpt_est[item_id] = new_value_float
                self.tree.set(item_id, column_name, f"{new_value_float:.2f}")
            else:
                if column_name == 'Descrição':
                    config.descricoes[item_id] = new_value
                elif column_name == 'NCM':
                    config.cf_to_ncm[item_id] = new_value
                self.tree.set(item_id, column_name, new_value)
        except (ValueError, KeyError) as e:
            messagebox.showerror("Erro de Edição", f"Valor inválido ou erro ao salvar: {e}", parent=self)
        finally:
            if self.edit_entry: self.edit_entry.destroy(); self.edit_entry = None

    def _salvar_tudo_e_fechar(self):
        config.ibpt_validade = self.validade_var.get()
        data_manager.salvar_tudo()
        messagebox.showinfo("Salvo", "Parâmetros nacionais salvos com sucesso.", parent=self)
        self.destroy()


class ParametrosFiscaisEditor(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Editar Parâmetros Fiscais por UF")
        self.geometry("950x500")
        self.transient(master)
        self.grab_set()
        self.focus_set()
        self.edit_entry = None
        self._create_widgets()
        self._carregar_parametros_na_tabela()

    def _create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(top_frame, text="Selecione a UF para editar:").pack(side=tk.LEFT)
        self.cb_uf = ttk.Combobox(top_frame, values=config.ufs, state='readonly', width=5)
        self.cb_uf.pack(side=tk.LEFT, padx=5)
        self.cb_uf.set(config.ufs[0])
        self.cb_uf.bind("<<ComboboxSelected>>", self._carregar_parametros_na_tabela)
        tk.Label(top_frame, text="(Dê um duplo-clique na célula para editar)").pack(side=tk.LEFT, padx=20)
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.colunas = ('CF', 'MVA', 'ICMS Interno', 'ICMS Interestadual', 'FCP', 'PROTOCOLO', 'MENSAGEM', 'ST ATIVO')
        self.tree = ttk.Treeview(tree_frame, columns=self.colunas, show='headings')
        for col in self.colunas: self.tree.heading(col, text=col)
        self.tree.column('CF', width=40, anchor='center', stretch=tk.NO)
        self.tree.column('MVA', width=80, anchor='e')
        self.tree.column('ICMS Interno', width=110, anchor='e')
        self.tree.column('ICMS Interestadual', width=120, anchor='e')
        self.tree.column('FCP', width=70, anchor='e')
        self.tree.column('PROTOCOLO', width=150)
        self.tree.column('MENSAGEM', width=200)
        self.tree.column('ST ATIVO', width=80, anchor='center')
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        self.tree.grid(row=0, column=0, sticky='nsew');
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1);
        tree_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind('<Double-1>', self._on_treeview_double_click)
        btn_salvar_fechar = tk.Button(self, text="Salvar Tudo e Fechar", command=self._salvar_tudo_e_fechar,
                                      bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_salvar_fechar.pack(pady=10)

    def _carregar_parametros_na_tabela(self, event=None):
        uf_selecionada = self.cb_uf.get()
        self.tree.delete(*self.tree.get_children())
        for cf_val in config.cfs:
            mva = config.mva_dict.get((uf_selecionada, cf_val), 0.0)
            icms_int = config.icms_interno_dict.get((uf_selecionada, cf_val), 18.0)
            icms_inter = config.icms_inter_dict.get((uf_selecionada, cf_val), 12.0)
            fcp = config.fcp_dict.get((uf_selecionada, cf_val), 0.0)
            protocolo = config.protocolo_dict.get((uf_selecionada, cf_val), '')
            mensagem = config.mensagem_dict.get((uf_selecionada, cf_val), '')
            st_ativo = "Sim" if config.st_ativo_dict.get((uf_selecionada, cf_val), False) else "Não"
            self.tree.insert('', tk.END, iid=cf_val, values=(
                cf_val, f"{mva:.2f}", f"{icms_int:.2f}", f"{icms_inter:.2f}",
                f"{fcp:.2f}", protocolo, mensagem, st_ativo
            ))

    def _on_treeview_double_click(self, event):
        if self.edit_entry: self.edit_entry.destroy()
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not item_id or not column_id: return
        x, y, width, height = self.tree.bbox(item_id, column_id)
        value = self.tree.set(item_id, column_id)
        column_name = self.colunas[int(column_id.replace('#', '')) - 1]
        if column_name == 'ST ATIVO':
            self.edit_entry = ttk.Combobox(self, values=["Sim", "Não"], state='readonly')
            self.edit_entry.set(value)
        else:
            self.edit_entry = ttk.Entry(self);
            self.edit_entry.insert(0, value)
        self.edit_entry.place(x=x, y=y, width=width, height=height)
        self.edit_entry.focus_set()
        self.edit_entry.bind("<Return>", lambda e: self._salvar_edicao(item_id, column_name))
        self.edit_entry.bind("<FocusOut>", lambda e: self._salvar_edicao(item_id, column_name))

    def _salvar_edicao(self, item_id, column_name):
        if not self.edit_entry: return
        try:
            new_value = self.edit_entry.get()
            uf_selecionada = self.cb_uf.get()
            if column_name in ['MVA', 'ICMS Interno', 'ICMS Interestadual', 'FCP']:
                new_value_float = float(new_value.replace(',', '.'))
                if column_name == 'MVA':
                    config.mva_dict[(uf_selecionada, item_id)] = new_value_float
                elif column_name == 'ICMS Interno':
                    config.icms_interno_dict[(uf_selecionada, item_id)] = new_value_float
                elif column_name == 'ICMS Interestadual':
                    config.icms_inter_dict[(uf_selecionada, item_id)] = new_value_float
                elif column_name == 'FCP':
                    config.fcp_dict[(uf_selecionada, item_id)] = new_value_float
                self.tree.set(item_id, column_name, f"{new_value_float:.2f}")
            elif column_name == 'ST ATIVO':
                config.st_ativo_dict[(uf_selecionada, item_id)] = (new_value == "Sim")
                self.tree.set(item_id, column_name, new_value)
            else:
                if column_name == 'PROTOCOLO':
                    config.protocolo_dict[(uf_selecionada, item_id)] = new_value
                elif column_name == 'MENSAGEM':
                    config.mensagem_dict[(uf_selecionada, item_id)] = new_value
                self.tree.set(item_id, column_name, new_value)
        finally:
            if self.edit_entry: self.edit_entry.destroy(); self.edit_entry = None

    def _salvar_tudo_e_fechar(self):
        data_manager.salvar_tudo()
        messagebox.showinfo("Salvo", "Parâmetros por UF salvos com sucesso.", parent=self)
        self.destroy()


class PisCofinsEditor(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Editar Alíquotas de PIS/COFINS por Operação")
        self.geometry("500x350")
        self.transient(master)
        self.grab_set()
        self.focus_set()
        self.edit_entry = None
        self._create_widgets()
        self._carregar_aliquotas_na_tabela()

    def _create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(top_frame, text="(Dê um duplo-clique na célula para editar)").pack(side=tk.LEFT, padx=5)
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.colunas = ('Operação', 'PIS (%)', 'COFINS (%)')
        self.tree = ttk.Treeview(tree_frame, columns=self.colunas, show='headings')
        for col in self.colunas:
            self.tree.heading(col, text=col)
            if col == 'Operação':
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=100, anchor='center')
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind('<Double-1>', self._on_treeview_double_click)
        btn_salvar_fechar = tk.Button(self, text="Salvar Tudo e Fechar", command=self._salvar_tudo_e_fechar,
                                      bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_salvar_fechar.pack(pady=10)

    def _carregar_aliquotas_na_tabela(self, event=None):
        self.tree.delete(*self.tree.get_children())
        for op in config.operacoes:
            aliquotas = config.pis_cofins_dict.get(op, {'pis': 0.0, 'cofins': 0.0})
            pis_pct = aliquotas.get('pis', 0.0)
            cofins_pct = aliquotas.get('cofins', 0.0)
            self.tree.insert('', tk.END, iid=op, values=(op, f"{pis_pct:.2f}", f"{cofins_pct:.2f}"))

    def _on_treeview_double_click(self, event):
        if self.edit_entry: self.edit_entry.destroy()
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not item_id or not column_id: return
        x, y, width, height = self.tree.bbox(item_id, column_id)
        value = self.tree.set(item_id, column_id)
        column_name = self.colunas[int(column_id.replace('#', '')) - 1]
        if column_name == 'Operação': return
        self.edit_entry = ttk.Entry(self)
        self.edit_entry.place(x=x, y=y, width=width, height=height)
        self.edit_entry.insert(0, value)
        self.edit_entry.focus_set()
        self.edit_entry.bind("<Return>", lambda e: self._salvar_edicao(item_id, column_name))
        self.edit_entry.bind("<FocusOut>", lambda e: self._salvar_edicao(item_id, column_name))

    def _salvar_edicao(self, item_id, column_name):
        if not self.edit_entry: return
        try:
            new_value_str = self.edit_entry.get().replace(',', '.')
            new_value_float = float(new_value_str)
            if item_id not in config.pis_cofins_dict:
                config.pis_cofins_dict[item_id] = {'pis': 0.0, 'cofins': 0.0}
            if column_name == 'PIS (%)':
                config.pis_cofins_dict[item_id]['pis'] = new_value_float
            elif column_name == 'COFINS (%)':
                config.pis_cofins_dict[item_id]['cofins'] = new_value_float
            self.tree.set(item_id, column_name, f"{new_value_float:.2f}")
        except (ValueError, KeyError) as e:
            messagebox.showerror("Erro de Edição", f"Valor inválido ou erro ao salvar: {e}", parent=self)
        finally:
            if self.edit_entry: self.edit_entry.destroy(); self.edit_entry = None

    def _salvar_tudo_e_fechar(self):
        data_manager.salvar_tudo()
        messagebox.showinfo("Salvo", "Alíquotas de PIS/COFINS salvas com sucesso.", parent=self)
        self.destroy()


class FiscalSimulatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Simulador Fiscal - Sacola Multi-Itens")
        master.geometry("1150x900")
        master.resizable(True, True)
        self.item_em_edicao = None
        self.dados_cotacao_atual = {}
        self._create_widgets()
        self._setup_menu()
        self._load_initial_data()
        self._limpar_sacola_inicio()

    def _create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        main_left_frame = ttk.Frame(self.master)
        main_left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        main_right_frame = ttk.Frame(self.master)
        main_right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=0)
        self.master.grid_rowconfigure(0, weight=1)
        frame_cotacao = tk.LabelFrame(main_left_frame, text="Dados da Cotação", padx=5, pady=5)
        frame_cotacao.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.lbl_cotacao_status = tk.Label(frame_cotacao, text="Cotação: (Apenas Simulação)",
                                           font=("Arial", 9, "italic"))
        self.lbl_cotacao_status.pack(side=tk.LEFT, padx=5, pady=5)
        btn_add_cliente = tk.Button(frame_cotacao, text="Adicionar/Editar Dados do Cliente",
                                    command=self.editar_dados_cotacao)
        btn_add_cliente.pack(side=tk.RIGHT, padx=5, pady=2)
        frame_entrada = tk.LabelFrame(main_left_frame, text="Entrada de Dados do Item", padx=5, pady=5)
        frame_entrada.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        tk.Label(frame_entrada, text="UF Origem:").grid(row=0, column=0, sticky='e', padx=2, pady=2)
        self.cb_uf_origem = ttk.Combobox(frame_entrada, values=config.ufs, state='readonly', width=10)
        self.cb_uf_origem.grid(row=0, column=1, sticky='w', padx=2, pady=2)
        self.cb_uf_origem.set("SP")
        tk.Label(frame_entrada, text="UF Destino:").grid(row=0, column=2, sticky='e', padx=2, pady=2)
        self.cb_uf_destino = ttk.Combobox(frame_entrada, values=config.ufs, state='readonly', width=10)
        self.cb_uf_destino.grid(row=0, column=3, sticky='w', padx=2, pady=2)
        self.cb_uf_destino.set("SP")
        tk.Label(frame_entrada, text="Vendedor:").grid(row=0, column=4, sticky='e', padx=2, pady=2)
        self.cb_vendedor = ttk.Combobox(frame_entrada, values=[], state='readonly', width=25)
        self.cb_vendedor.grid(row=0, column=5, sticky='w', padx=2, pady=2)
        tk.Label(frame_entrada, text="Classificação Fiscal (CF):").grid(row=1, column=0, sticky='e', padx=2, pady=2)
        self.cf_opcoes = [f"{cf} - {config.descricoes.get(cf, 'Descrição não encontrada')}" for cf in config.cfs]
        self.cb_cf = ttk.Combobox(frame_entrada, values=self.cf_opcoes, state='readonly', width=30)
        self.cb_cf.grid(row=1, column=1, columnspan=2, sticky='w', padx=2, pady=2)
        if self.cf_opcoes: self.cb_cf.set(self.cf_opcoes[0])
        tk.Label(frame_entrada, text="Operação:").grid(row=1, column=3, sticky='e', padx=2, pady=2)
        self.cb_operacao = ttk.Combobox(frame_entrada, values=config.operacoes, state='readonly', width=20)
        self.cb_operacao.grid(row=1, column=4, sticky='w', padx=2, pady=2)
        self.cb_operacao.set(config.operacoes[0])
        vcmd_float = (self.master.register(gui_utils.validate_float), '%P')
        tk.Label(frame_entrada, text="Quantidade:").grid(row=2, column=0, sticky='e', padx=2, pady=2)
        self.entry_qtd = tk.Entry(frame_entrada, validate="key", validatecommand=vcmd_float, width=15)
        self.entry_qtd.grid(row=2, column=1, sticky='w', padx=2, pady=2)
        tk.Label(frame_entrada, text="Valor Unitário:").grid(row=2, column=2, sticky='e', padx=2, pady=2)
        self.entry_unitario = tk.Entry(frame_entrada, validate="key", validatecommand=vcmd_float, width=15)
        self.entry_unitario.grid(row=2, column=3, sticky='w', padx=2, pady=2)
        tk.Label(frame_entrada, text="Valor Total:").grid(row=2, column=4, sticky='e', padx=2, pady=2)
        self.entry_valor = tk.Entry(frame_entrada, width=15, state='readonly', takefocus=0)
        self.entry_valor.grid(row=2, column=5, sticky='w', padx=2, pady=2)
        self.entry_qtd.bind("<KeyRelease>", self._atualizar_valor_total)
        self.entry_unitario.bind("<KeyRelease>", self._atualizar_valor_total)
        tk.Label(frame_entrada, text="Descrição Personalizada:").grid(row=3, column=0, sticky='ne', padx=2, pady=2)
        self.entry_desc_user = tk.Text(frame_entrada, height=2, width=60)
        self.entry_desc_user.grid(row=3, column=1, columnspan=4, sticky='ew', padx=2, pady=2)
        self.entry_desc_user.bind("<KeyRelease>", self._to_uppercase)
        self.btn_adicionar = tk.Button(frame_entrada, text="Adicionar Item à Sacola", command=self.adicionar_item,
                                       bg="#E69138", fg="white", width=25, height=2)
        self.btn_adicionar.grid(row=3, column=5, sticky='e', padx=2, pady=2)
        self._set_tab_order(frame_entrada)
        frame_sacola = tk.LabelFrame(main_left_frame, text="Sacola de Itens", padx=5, pady=5)
        frame_sacola.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        self.txt_lista_itens = tk.Text(frame_sacola, height=8, width=100, state='disabled', wrap='word')
        self.txt_lista_itens.pack(fill=tk.BOTH, expand=True)
        frame_acoes_sacola = tk.Frame(main_left_frame, padx=5, pady=5)
        frame_acoes_sacola.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        tk.Label(frame_acoes_sacola, text="Editar Item Nº:").pack(side=tk.LEFT, padx=5)
        self.entry_editar = tk.Entry(frame_acoes_sacola, width=5)
        self.entry_editar.pack(side=tk.LEFT, padx=2)
        self.btn_editar = tk.Button(frame_acoes_sacola, text="Editar", command=self.editar_item, bg="#4096EE",
                                    fg="white")
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        tk.Label(frame_acoes_sacola, text="Remover Item Nº:").pack(side=tk.LEFT, padx=10)
        self.entry_remover = tk.Entry(frame_acoes_sacola, width=5)
        self.entry_remover.pack(side=tk.LEFT, padx=2)
        self.btn_remover = tk.Button(frame_acoes_sacola, text="Remover", command=self.remover_item, bg="#D62828",
                                     fg="white")
        self.btn_remover.pack(side=tk.LEFT, padx=5)
        self.btn_limpar_sacola = tk.Button(frame_acoes_sacola, text="Limpar Sacola", command=self.limpar_sacola,
                                           bg="#FCBF49", fg="black")
        self.btn_limpar_sacola.pack(side=tk.RIGHT, padx=5)
        frame_resultados = tk.LabelFrame(main_left_frame, text="Resultados da Simulação", padx=5, pady=5)
        frame_resultados.grid(row=4, column=0, sticky='nsew', padx=5, pady=5)
        main_left_frame.grid_rowconfigure(4, weight=1)
        main_left_frame.grid_columnconfigure(0, weight=1)
        self.btn_imprimir = tk.Button(frame_resultados, text="Imprimir", command=self._imprimir_simulacao, bg="#A9A9A9",
                                      fg="white")
        self.btn_imprimir.place(relx=1.0, rely=0, anchor='ne', x=-5, y=2)
        self.txt_resultado = tk.Text(frame_resultados, height=15, width=100, state='disabled', wrap='word')
        self.txt_resultado.pack(fill=tk.BOTH, expand=True)
        self.btn_simular = tk.Button(main_right_frame, text="Simular!", command=self.simular_sacola_gui, bg="#4CAF50",
                                     fg="white", font=("Arial", 12, "bold"), width=20, height=2)
        self.btn_simular.pack(anchor='n', pady=5, fill=tk.X)
        btn_copiar = tk.Button(main_right_frame, text="Copiar Simulação", command=self._copiar_simulacao, bg="#E69138",
                               fg="white", font=("Arial", 10))
        btn_copiar.pack(anchor='n', pady=(10, 2), fill=tk.X)
        self.btn_gerar_email = tk.Button(main_right_frame, text="Gerar Texto para E-mail",
                                         command=self.gerar_texto_email, bg="#00BCD4", fg="white", font=("Arial", 10))
        self.btn_gerar_email.pack(anchor='n', pady=2, fill=tk.X)
        self.btn_gerar_pdf = tk.Button(main_right_frame, text="Gerar PDF da Cotação", command=self.gerar_pdf_cotacao,
                                       bg="#0078D7", fg="white", font=("Arial", 10))
        self.btn_gerar_pdf.pack(anchor='n', pady=2, fill=tk.X)
        btn_buscar = tk.Button(main_right_frame, text="Buscar Cotação", command=self.buscar_cotacao, bg="#5C5C5C",
                               fg="white", font=("Arial", 10))
        btn_buscar.pack(anchor='n', pady=2, fill=tk.X)

        btn_abrir_pasta = tk.Button(main_right_frame, text="Abrir Pasta de Cotações",
                                    command=self._abrir_pasta_cotacoes,
                                    bg="#6c757d", fg="white", font=("Arial", 10))
        btn_abrir_pasta.pack(anchor='n', pady=2, fill=tk.X)

        btn_sair = tk.Button(main_right_frame, text="Sair e Salvar", command=self._salvar_e_sair, bg="#D62828",
                             fg="white", font=("Arial", 10, "bold"))
        btn_sair.pack(side=tk.BOTTOM, anchor='s', pady=10, fill=tk.X)

    def _abrir_pasta_cotacoes(self):
        """Abre a pasta onde as cotações são salvas no explorador de arquivos."""
        path = os.path.realpath(config.DIR_COTACOES)
        try:
            os.makedirs(path, exist_ok=True)
            if os.name == 'nt':  # Para Windows
                subprocess.Popen(f'explorer "{path}"')
            elif os.name == 'posix':  # Para Linux/macOS
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta de cotações.\n\nErro: {e}")

    def _setup_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Salvar Tudo", command=self._salvar_tudo_gui)
        menu_arquivo.add_command(label="Carregar Tudo", command=self._carregar_tudo_gui)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Fazer Backup Completo...", command=self._fazer_backup)
        menu_arquivo.add_command(label="Restaurar Backup...", command=self._restaurar_backup)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Editar Dados da Empresa", command=self.editar_empresa)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self._salvar_e_sair)
        menu_config = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Configurações", menu=menu_config)
        menu_config.add_command(label="Parâmetros Nacionais (CF/NCM/IBPT)", command=self.editar_parametros_nacionais)
        menu_config.add_command(label="Parâmetros por UF (ICMS/MVA)", command=self.editar_parametros_uf)
        menu_config.add_command(label="Alíquotas PIS/COFINS", command=self.editar_pis_cofins)
        menu_config.add_separator()
        menu_config.add_command(label="Cadastro de Vendedores", command=self.editar_vendedores)

    def _load_initial_data(self):
        data_manager.carregar_tudo()
        self.atualizar_lista_itens()
        self.atualizar_vendedor_combobox()

    def _limpar_sacola_inicio(self):
        config.itens_sacola.clear()
        self.dados_cotacao_atual.clear()
        self.atualizar_lista_itens()
        if hasattr(self, 'lbl_cotacao_status'):
            self.atualizar_status_cotacao()

    def _set_tab_order(self, container):
        widgets_in_order = [self.entry_qtd, self.entry_unitario, self.entry_desc_user, self.btn_adicionar]
        for widget in widgets_in_order: widget.lift()

    def _to_uppercase(self, event):
        widget = event.widget
        if isinstance(widget, tk.Text):
            content = widget.get("1.0", "end-1c")
            current_pos = widget.index(tk.INSERT)
            widget.delete("1.0", tk.END)
            widget.insert("1.0", content.upper())
            widget.mark_set(tk.INSERT, current_pos)
        elif isinstance(widget, tk.Entry):
            content = widget.get()
            widget.delete(0, tk.END)
            widget.insert(0, content.upper())

    def atualizar_status_cotacao(self):
        if self.dados_cotacao_atual.get("numero"):
            texto = f"Cotação: {self.dados_cotacao_atual['numero']} ({self.dados_cotacao_atual.get('empresa_cliente', 'N/A')})"
            cor = "blue"
            estilo = "bold"
        else:
            texto = "Cotação: (Apenas Simulação)"
            cor = "black"
            estilo = "italic"
        self.lbl_cotacao_status.config(text=texto, fg=cor, font=("Arial", 9, estilo))

    def _fazer_backup(self):
        data_hora = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        nome_arquivo_sugerido = f"backup_assistente_fiscal_{data_hora}.zip"
        file_path = filedialog.asksaveasfilename(initialfile=nome_arquivo_sugerido, defaultextension=".zip",
                                                 filetypes=[("Arquivos ZIP", "*.zip")], title="Salvar Backup Como...")
        if not file_path: return
        try:
            with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(config.CAMINHO_DADOS):
                    for file in files:
                        caminho_completo = os.path.join(root, file)
                        caminho_no_zip = os.path.relpath(caminho_completo, os.path.dirname(config.CAMINHO_DADOS))
                        zipf.write(caminho_completo, caminho_no_zip)
            messagebox.showinfo("Sucesso", f"Backup completo salvo com sucesso em:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro de Backup", f"Ocorreu um erro ao criar o backup:\n{e}")

    def _restaurar_backup(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos ZIP de Backup", "*.zip")],
                                               title="Selecionar Arquivo de Backup para Restaurar")
        if not file_path: return
        if not messagebox.askyesno("Atenção!",
                                   "Isso substituirá TODOS os seus dados atuais (cotações, vendedores, parâmetros) pelos dados do backup.\n\nEsta ação não pode ser desfeita.\n\nDeseja continuar?",
                                   icon='warning'):
            return
        try:
            if os.path.exists(config.CAMINHO_DADOS): shutil.rmtree(config.CAMINHO_DADOS)
            base_path = os.path.dirname(config.CAMINHO_DADOS)
            with zipfile.ZipFile(file_path, 'r') as zipf:
                zipf.extractall(path=base_path)
            messagebox.showinfo("Sucesso",
                                "Backup restaurado com sucesso.\n\nPor favor, reinicie o aplicativo para que as alterações tenham efeito.")
            self.master.quit()
        except Exception as e:
            messagebox.showerror("Erro de Restauração", f"Ocorreu um erro ao restaurar o backup:\n{e}")

    def _imprimir_simulacao(self):
        resultado_texto = self.txt_resultado.get("1.0", tk.END).strip()
        if not resultado_texto or "Nenhum item para simular" in resultado_texto:
            messagebox.showwarning("Aviso", "Não há resultado para imprimir. Simule primeiro.")
            return
        if os.name != 'nt':
            messagebox.showerror("Erro de Compatibilidade",
                                 "A impressão direta só é suportada no sistema operacional Windows.")
            return
        try:
            temp_file_path = ""
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
                temp_file.write(resultado_texto);
                temp_file_path = temp_file.name
            if temp_file_path: os.startfile(temp_file_path, "print")
        except Exception as e:
            messagebox.showerror("Erro de Impressão", f"Não foi possível enviar para a impressora.\nErro: {e}")

    def _copiar_simulacao(self):
        resultado_texto = self.txt_resultado.get("1.0", tk.END).strip()
        if not resultado_texto or "Nenhum item para simular" in resultado_texto:
            self.simular_sacola_gui();
            resultado_texto = self.txt_resultado.get("1.0", tk.END).strip()
        if resultado_texto and "Nenhum item para simular" not in resultado_texto:
            self.master.clipboard_clear();
            self.master.clipboard_append(resultado_texto)
            messagebox.showinfo("Copiado", "O resultado da simulação foi copiado para a área de transferência!")
        else:
            messagebox.showwarning("Aviso", "Não há resultado para copiar. Adicione itens e simule primeiro.")

    def _salvar_dados(self):
        vendedor_selecionado = self.cb_vendedor.get()
        if vendedor_selecionado and ' - Código ' in vendedor_selecionado:
            config.last_selected_vendedor_code = vendedor_selecionado.split(' - Código ')[1]
        else:
            config.last_selected_vendedor_code = ""
        data_manager.salvar_tudo()

    def _salvar_tudo_gui(self):
        self._salvar_dados()
        messagebox.showinfo("Salvo", "Todos os dados foram salvos com sucesso! 💾")

    def _salvar_e_sair(self):
        self._salvar_dados()
        self.master.quit()

    def _carregar_tudo_gui(self):
        data_manager.carregar_tudo()
        self.atualizar_lista_itens()
        self.atualizar_vendedor_combobox()
        self._limpar_sacola_inicio()
        messagebox.showinfo("Carregado", "Todos os dados foram carregados com sucesso! 🔄")

    def _atualizar_valor_total(self, *args):
        try:
            qtd = float(self.entry_qtd.get().replace(",", ".")) if self.entry_qtd.get() else 0.0
            unitario = float(self.entry_unitario.get().replace(",", ".")) if self.entry_unitario.get() else 0.0
            valor = round(qtd * unitario, 2)
            self.entry_valor.config(state='normal');
            self.entry_valor.delete(0, tk.END)
            self.entry_valor.insert(0, f"{valor:.2f}".replace(".", ","));
            self.entry_valor.config(state='readonly')
        except ValueError:
            self.entry_valor.config(state='normal');
            self.entry_valor.delete(0, tk.END)
            self.entry_valor.insert(0, "0,00");
            self.entry_valor.config(state='readonly')

    def adicionar_item(self):
        try:
            uf_origem = self.cb_uf_origem.get();
            uf_destino = self.cb_uf_destino.get()
            cf_descricao = self.cb_cf.get()
            if not uf_origem or not uf_destino or not cf_descricao:
                messagebox.showerror("Erro", "UF de Origem, UF de Destino e CF são campos obrigatórios.");
                return
            cf = cf_descricao.split(' - ')[0] if ' - ' in cf_descricao else cf_descricao
            op = self.cb_operacao.get()
            if not op: messagebox.showerror("Erro", "A Operação é um campo obrigatório."); return
            qtd_str = self.entry_qtd.get().replace(",", ".");
            unitario_str = self.entry_unitario.get().replace(",", ".")
            if not qtd_str or not unitario_str:
                messagebox.showerror("Erro", "Quantidade e Valor Unitário são campos obrigatórios.");
                return
            qtd = float(qtd_str);
            unitario = float(unitario_str)
            if qtd <= 0 or unitario <= 0:
                messagebox.showerror("Erro", "Quantidade e Valor Unitário devem ser maiores que zero.");
                return
            valor = round(qtd * unitario, 2)
            ncm = config.cf_to_ncm.get(cf, 'NCM_N/A');
            descricao = config.descricoes.get(cf, 'Descrição N/A')
            descricao_usuario = self.entry_desc_user.get("1.0", tk.END).strip()
            novo_item = {'uf_origem': uf_origem, 'uf_destino': uf_destino, 'cf': cf, 'operacao': op, 'qtd': qtd,
                         'unitario': unitario, 'valor': valor, 'ncm': ncm, 'descricao': descricao,
                         'descricao_usuario': descricao_usuario}
            if self.item_em_edicao is not None:
                config.itens_sacola[self.item_em_edicao] = novo_item
                self.item_em_edicao = None
                self.btn_adicionar.config(text="Adicionar Item à Sacola", bg="#E69138")
            else:
                config.itens_sacola.append(novo_item)
            self.entry_qtd.delete(0, tk.END);
            self.entry_unitario.delete(0, tk.END)
            self.entry_desc_user.delete("1.0", tk.END);
            self.entry_valor.config(state='normal')
            self.entry_valor.delete(0, tk.END);
            self.entry_valor.config(state='readonly')
            self.cb_cf.set("");
            self.atualizar_lista_itens()
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e/ou Valor Unitário devem ser números válidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao adicionar/editar o item:\n\n{e}")

    def atualizar_lista_itens(self):
        self.txt_lista_itens.config(state='normal');
        self.txt_lista_itens.delete("1.0", tk.END)
        for idx, it in enumerate(config.itens_sacola, 1):
            desc = it.get('descricao_usuario') or it['descricao']
            desc_completa = f"CF: {it['cf']} - {desc}"
            self.txt_lista_itens.insert(tk.END,
                                        f"{idx}. {desc_completa:<40} | Qtd: {it['qtd']} | Unit: {gui_utils.moeda(it['unitario'])} | Op: {it['operacao']}\n")
        self.txt_lista_itens.config(state='disabled')

    def editar_item(self):
        try:
            idx_str = self.entry_editar.get().strip()
            if not idx_str: return
            idx = int(idx_str) - 1
            if 0 <= idx < len(config.itens_sacola):
                it = config.itens_sacola[idx]
                self.cb_uf_origem.set(it['uf_origem']);
                self.cb_uf_destino.set(it['uf_destino'])
                cf_found = False
                for v in self.cf_opcoes:
                    if v.startswith(it['cf']): self.cb_cf.set(v); cf_found = True; break
                if not cf_found: self.cb_cf.set("")
                self.cb_operacao.set(it['operacao'])
                self.entry_qtd.delete(0, tk.END);
                self.entry_qtd.insert(0, str(it['qtd']))
                self.entry_unitario.delete(0, tk.END);
                self.entry_unitario.insert(0, str(it['unitario']))
                self.entry_desc_user.delete("1.0", tk.END);
                self.entry_desc_user.insert(tk.END, it.get('descricao_usuario', it['descricao']))
                self.entry_valor.config(state='normal');
                self.entry_valor.delete(0, tk.END)
                self.entry_valor.insert(0, f"{it['valor']:.2f}");
                self.entry_valor.config(state='readonly')
                self.item_em_edicao = idx
                self.btn_adicionar.config(text="Salvar Edição", bg="#0070C0")
            else:
                messagebox.showerror("Erro", "Índice de item inválido para editar!")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, digite um número válido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao tentar editar o item:\n\n{e}")

    def remover_item(self):
        try:
            idx_str = self.entry_remover.get().strip()
            if not idx_str: return
            idx = int(idx_str) - 1
            if 0 <= idx < len(config.itens_sacola):
                del config.itens_sacola[idx];
                self.atualizar_lista_itens()
            else:
                messagebox.showerror("Erro", "Índice de item inválido!")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, digite um número válido.")

    def limpar_sacola(self):
        if messagebox.askyesno("Limpar Sacola",
                               "Tem certeza que deseja limpar todos os itens da sacola e os dados do cliente?"):
            self._limpar_sacola_inicio()
            self.txt_resultado.config(state='normal')
            self.txt_resultado.delete("1.0", tk.END)
            self.txt_resultado.config(state='disabled')

    def _verificar_validade_ibpt(self):
        try:
            validade_str = config.ibpt_validade
            if not validade_str: return
            data_validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
            data_hoje = datetime.now().date()
            if data_hoje > data_validade:
                messagebox.showwarning("IBPT Vencido",
                                       f"Atenção: A tabela IBPT venceu em {data_validade.strftime('%d/%m/%Y')}.\nAs alíquotas podem estar desatualizadas.")
        except (ValueError, TypeError):
            messagebox.showerror("Data Inválida",
                                 "A data de validade do IBPT está em formato inválido. Use AAAA-MM-DD.")

    def simular_sacola_gui(self):
        self._verificar_validade_ibpt()
        self.txt_resultado.config(state='normal');
        self.txt_resultado.delete("1.0", tk.END)
        if not config.itens_sacola:
            self.txt_resultado.insert(tk.END, "Nenhum item para simular.\n");
            self.txt_resultado.config(state='disabled');
            return
        total_produtos, tot_ipi, tot_icms_st, tot_difal, total_geral, tot_fcp, resumo_text = fiscal_logic.simular_sacola()
        if resumo_text:
            self.txt_resultado.insert(tk.END, resumo_text)
        else:
            self.txt_resultado.insert(tk.END, "Nenhum item para simular.\n")
        self.txt_resultado.config(state='disabled')
        if self.dados_cotacao_atual.get("numero"):
            vendedor_str = self.cb_vendedor.get()
            if not vendedor_str or ' - Código ' not in vendedor_str: return
            vendedor_nome = vendedor_str.split(' - Código ')[0]
            vendedor_codigo = vendedor_str.split(' - Código ')[1]
            dados_completos = {**self.dados_cotacao_atual, "vendedor_nome": vendedor_nome,
                               "vendedor_codigo": vendedor_codigo,
                               "itens": list(config.itens_sacola), "total_produtos": total_produtos,
                               "total_ipi": tot_ipi,
                               "total_icms_st": tot_icms_st, "total_difal": tot_difal, "total_geral": total_geral}
            self._salvar_arquivo_cotacao(dados_completos)

    def _salvar_arquivo_cotacao(self, dados_completos):
        arq_path = os.path.join(config.DIR_COTACOES, f"{dados_completos['numero']}.json")
        while True:
            try:
                with open(arq_path, "w", encoding="utf-8") as f:
                    json.dump(dados_completos, f, ensure_ascii=False,
                              indent=2)
                return True
            except PermissionError:
                resposta = messagebox.askretrycancel("Arquivo em Uso",
                                                     f"Não foi possível salvar a cotação:\n{os.path.basename(arq_path)}\n\nO arquivo provavelmente está aberto em outro programa.\n\nPor favor, feche o arquivo e clique em 'Tentar Novamente'.",
                                                     parent=self.master)
                if not resposta:
                    messagebox.showerror("Falha ao Salvar", "A cotação não foi salva pois o arquivo continua em uso.",
                                         parent=self.master);
                    return False
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro inesperado ao salvar a cotação:\n{e}",
                                     parent=self.master);
                return False

    def editar_empresa(self):
        editor = tk.Toplevel(self.master);
        editor.title("Dados da Empresa Orçamentista")
        editor.geometry("500x300");
        editor.transient(self.master);
        editor.grab_set();
        editor.focus_set()
        campos = ["nome", "cnpj", "endereco", "contato", "fone"]
        entries = {}
        for i, key in enumerate(campos):
            tk.Label(editor, text=f"{key.capitalize()}:").grid(row=i, column=0, sticky='e', padx=4, pady=5)
            e = tk.Entry(editor, width=50);
            e.grid(row=i, column=1, padx=4, pady=5)
            e.insert(0, config.empresa_orcamento.get(key, ""));
            entries[key] = e

        def salvar_emp():
            for key, entry in entries.items(): config.empresa_orcamento[key] = entry.get().strip()
            data_manager.salvar_tudo();
            editor.destroy()

        tk.Button(editor, text="Salvar", command=salvar_emp).grid(row=len(campos), column=1, pady=10)

    def editar_parametros_nacionais(self):
        editor = ParametrosNacionaisEditor(self.master)
        self.master.wait_window(editor)
        self.cf_opcoes = [f"{cf} - {config.descricoes.get(cf, 'N/A')}" for cf in config.cfs]
        self.cb_cf['values'] = self.cf_opcoes

    def editar_parametros_uf(self):
        editor = ParametrosFiscaisEditor(self.master)
        self.master.wait_window(editor)

    def editar_pis_cofins(self):
        editor = PisCofinsEditor(self.master)
        self.master.wait_window(editor)

    def editar_vendedores(self):
        editor = VendedoresEditor(self.master)
        self.master.wait_window(editor)
        self.atualizar_vendedor_combobox()

    def atualizar_vendedor_combobox(self):
        opcoes_vendedores = [f"{v['nome']} - Código {v['codigo']}" for v in config.vendedores_cadastrados]
        self.cb_vendedor['values'] = opcoes_vendedores
        vendedor_encontrado = False
        if config.last_selected_vendedor_code:
            for opt in opcoes_vendedores:
                if opt.endswith(f"Código {config.last_selected_vendedor_code}"):
                    self.cb_vendedor.set(opt);
                    vendedor_encontrado = True;
                    break
        if not vendedor_encontrado and opcoes_vendedores:
            self.cb_vendedor.set(opcoes_vendedores[0])
        elif not opcoes_vendedores:
            self.cb_vendedor.set("")

    def gerar_texto_email(self):
        if not config.itens_sacola: messagebox.showwarning("Aviso", "Não há itens na sacola para gerar o texto.",
                                                           parent=self.master); return
        total_produtos, tot_ipi, tot_icms_st, tot_difal, total_geral, tot_fcp, _ = fiscal_logic.simular_sacola()
        hora_atual = datetime.now().hour
        if 5 <= hora_atual < 12:
            saudacao = "Bom dia"
        elif 12 <= hora_atual < 18:
            saudacao = "Boa tarde"
        else:
            saudacao = "Boa noite"
        nome_contato_completo = self.dados_cotacao_atual.get('cliente', '').strip()
        if nome_contato_completo:
            partes_nome = nome_contato_completo.split()
            if len(partes_nome) > 1 and partes_nome[0].lower().startswith('sr'):
                nome_final = partes_nome[1].capitalize()
            else:
                nome_final = partes_nome[0].capitalize()
            saudacao_nome = f"Sr. {nome_final}"
        else:
            saudacao_nome = "Prezado Cliente"
        texto_final = f"{saudacao_nome},\n{saudacao},\n\nConforme solicitado, segue orçamento:\n"
        texto_final += "─" * 40 + "\n\n"
        for it in config.itens_sacola:
            desc = it.get('descricao_usuario') or it['descricao'];
            texto_final += f"{desc.upper()}\n"
            texto_final += f"Qtd: {it['qtd']} | Unit: {gui_utils.moeda(it['unitario'])}\n"
            # --- ALTERAÇÃO: IPI é sempre exibido ---
            texto_final += f"IPI à incluir: {it.get('ipi_pct', 0):.2f}%\n"
            texto_final += f"NCM: {it['ncm']}\n";
            texto_final += f"Material tem como destino: {it['operacao'].upper()}\n\n"
        observacao = self.dados_cotacao_atual.get('observacao', '').strip()
        if observacao: texto_final += "─" * 40 + "\n"; texto_final += f"OBS.: {observacao}\n"; texto_final += "─" * 40 + "\n\n"
        texto_final += f"Nota Fiscal: {gui_utils.moeda(total_geral)}\n\n"
        primeiro_item = config.itens_sacola[0]
        icms_incluso_pct = config.icms_inter_dict.get((primeiro_item['uf_destino'], primeiro_item['cf']), 0.0)
        texto_final += f"ICMS Incluso {icms_incluso_pct:.2f}%\n"
        texto_final += f"Faturado para: {primeiro_item['uf_destino']}\n"
        if tot_ipi > 0: texto_final += f"IPI: {gui_utils.moeda(tot_ipi)}\n"
        if tot_icms_st > 0: texto_final += f"ICMS ST: {gui_utils.moeda(tot_icms_st)}\n"
        if tot_difal > 0: texto_final += f"DIFAL: {gui_utils.moeda(tot_difal)}\n"
        texto_final += "\n"
        condpag = self.dados_cotacao_atual.get('condpag', '[CONDIÇÃO DE PAGAMENTO]')
        if any(char.isdigit() for char in condpag) and "ddl" not in condpag.lower(): condpag += " DDL"
        texto_final += f"Pagamento: {condpag}\n"
        prazo = self.dados_cotacao_atual.get('prazo', '[PRAZO DE FABRICAÇÃO]')
        if any(char.isdigit() for char in prazo) and "dias" not in prazo.lower(): prazo += " dias úteis"
        texto_final += f"Fabricação: {prazo}\n";
        texto_final += "Material posto em fábrica / Suzano - SP\n"
        vendedor_selecionado_str = self.cb_vendedor.get()
        if vendedor_selecionado_str and ' - Código ' in vendedor_selecionado_str:
            vendedor_codigo = vendedor_selecionado_str.split(' - Código ')[1]
            vendedor_data = next((v for v in config.vendedores_cadastrados if v['codigo'] == vendedor_codigo), None)
            if vendedor_data:
                texto_final += "\n\nAtenciosamente,\n\n";
                texto_final += f"{vendedor_data.get('nome', '')}\n"
                texto_final += "Depto. Comercial\n"
                if vendedor_data.get('email'): texto_final += f"{vendedor_data.get('email')}\n"
                if vendedor_data.get('celular'): texto_final += f"Whats: {vendedor_data.get('celular')}\n"
        top = tk.Toplevel(self.master);
        top.title("Texto para E-mail");
        top.geometry("500x600");
        top.transient(self.master);
        top.grab_set()
        text_widget = tk.Text(top, wrap='word', height=25, width=60, font=("Courier New", 9))
        text_widget.pack(padx=10, pady=10, fill='both', expand=True);
        text_widget.insert('1.0', texto_final)

        def copiar_e_fechar():
            self.master.clipboard_clear();
            self.master.clipboard_append(text_widget.get("1.0", tk.END))
            messagebox.showinfo("Copiado", "Texto copiado para a área de transferência!", parent=top);
            top.destroy()

        btn_copiar = tk.Button(top, text="Copiar Tudo e Fechar", command=copiar_e_fechar, bg="#0078D7", fg="white")
        btn_copiar.pack(pady=10, padx=10, fill='x')

    def editar_dados_cotacao(self):
        vendedor_str = self.cb_vendedor.get()
        if not vendedor_str or ' - Código ' not in vendedor_str:
            messagebox.showerror("Erro", "Por favor, selecione um vendedor antes de adicionar dados do cliente.");
            return
        top = tk.Toplevel(self.master);
        top.title("Dados da Cotação");
        top.geometry("600x450");
        top.transient(self.master);
        top.grab_set()
        main_frame = ttk.Frame(top, padding=10);
        main_frame.pack(fill='both', expand=True)
        campos = [("Empresa (cliente)", "empresa_cliente"), ("Nome do contato", "cliente"), ("Depto", "depto"),
                  ("E-mail", "email"), ("Prazo de fabricação (dias)", "prazo"), ("Condição de pagamento", "condpag")]
        entries = {}
        for i, (lbl, key) in enumerate(campos):
            tk.Label(main_frame, text=lbl).grid(row=i, column=0, sticky='e', padx=4, pady=5)
            e = tk.Entry(main_frame, width=50);
            e.grid(row=i, column=1, padx=4, pady=5, sticky='ew');
            e.insert(0, self.dados_cotacao_atual.get(key, ''))
            if key == "empresa_cliente": e.bind("<KeyRelease>", self._to_uppercase)
            entries[key] = e
        tk.Label(main_frame, text="OBS.:").grid(row=len(campos), column=0, sticky='ne', padx=4, pady=5)
        obs_text = tk.Text(main_frame, width=50, height=4);
        obs_text.grid(row=len(campos), column=1, padx=4, pady=5, sticky='ew')
        obs_text.insert("1.0", self.dados_cotacao_atual.get('observacao', ''));
        entries['observacao'] = obs_text

        def salvar_dados_cliente():
            for key, entry in entries.items():
                if isinstance(entry, tk.Text):
                    self.dados_cotacao_atual[key] = entry.get("1.0", tk.END).strip()
                else:
                    self.dados_cotacao_atual[key] = entry.get().strip()
            is_new = not self.dados_cotacao_atual.get("numero")
            if is_new:
                vendedor_codigo = vendedor_str.split(' - Código ')[1]
                self.dados_cotacao_atual["numero"] = data_manager.gerar_numero_cotacao(vendedor_codigo)
                self.dados_cotacao_atual["data"] = datetime.now().strftime("%d/%m/%Y")
            self.atualizar_status_cotacao()
            vendedor_nome = vendedor_str.split(' - Código ')[0]
            vendedor_codigo = vendedor_str.split(' - Código ')[1]
            dados_completos = {**self.dados_cotacao_atual, "vendedor_nome": vendedor_nome,
                               "vendedor_codigo": vendedor_codigo, "itens": list(config.itens_sacola)}
            if self._salvar_arquivo_cotacao(dados_completos):
                messagebox.showinfo("Salvo", f"Cotação {self.dados_cotacao_atual['numero']} salva com sucesso.",
                                    parent=top);
                top.destroy()

        btn_salvar = tk.Button(main_frame, text="Salvar Dados do Cliente", command=salvar_dados_cliente, bg="#4CAF50",
                               fg="white")
        btn_salvar.grid(row=len(campos) + 1, column=1, pady=18, sticky='e')

    def gerar_pdf_cotacao(self):
        if not self.dados_cotacao_atual.get("numero"):
            messagebox.showerror("Erro", "É necessário adicionar os dados do cliente antes de gerar o PDF.",
                                 parent=self.master)
            if messagebox.askyesno("Adicionar Dados", "Deseja adicionar os dados do cliente agora?",
                                   parent=self.master): self.editar_dados_cotacao()
            return
        if not config.itens_sacola:
            messagebox.showwarning("Aviso", "Não há itens na sacola para gerar o PDF.", parent=self.master);
            return
        total_produtos, tot_ipi, tot_icms_st, tot_difal, total_geral, tot_fcp, _ = fiscal_logic.simular_sacola()
        vendedor_str = self.cb_vendedor.get();
        vendedor_nome = vendedor_str.split(' - Código ')[0]
        vendedor_codigo = vendedor_str.split(' - Código ')[1]
        dados_completos = {**self.dados_cotacao_atual, "vendedor_nome": vendedor_nome,
                           "vendedor_codigo": vendedor_codigo,
                           "itens": list(config.itens_sacola), "total_produtos": total_produtos, "total_ipi": tot_ipi,
                           "total_icms_st": tot_icms_st, "total_difal": tot_difal, "total_geral": total_geral}
        if self._salvar_arquivo_cotacao(dados_completos):
            try:
                pdf_generator.gerar_pdf_cotacao(dados_completos, config.empresa_orcamento)
                messagebox.showinfo("Sucesso", f"PDF da cotação {dados_completos['numero']} gerado com sucesso.",
                                    parent=self.master)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {e}", parent=self.master)

    def buscar_cotacao(self):
        top = tk.Toplevel(self.master);
        top.title("Buscar Cotação");
        top.geometry("850x450")
        top.transient(self.master);
        top.grab_set();
        top.focus_set()
        todas_as_cotacoes = [];
        lista_cotacoes_filtrada = []
        search_frame = ttk.Frame(top, padding=(10, 10, 10, 5));
        search_frame.pack(fill='x')
        tk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        entry_busca = tk.Entry(search_frame, width=50);
        entry_busca.pack(side=tk.LEFT, fill='x', expand=True)
        ver_arquivadas_var = tk.BooleanVar()
        check_arquivadas = ttk.Checkbutton(search_frame, text="Ver Arquivadas", variable=ver_arquivadas_var,
                                           command=lambda: filtrar_lista())
        check_arquivadas.pack(side=tk.LEFT, padx=(10, 0))
        list_frame = ttk.Frame(top, padding=(10, 0, 10, 5));
        list_frame.pack(fill='both', expand=True)
        lb = tk.Listbox(list_frame, width=80, height=15, selectmode=tk.EXTENDED)
        scrollbar_y = ttk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
        lb.configure(yscrollcommand=scrollbar_y.set)
        lb.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill='y')
        button_frame = ttk.Frame(top, padding=(10, 5, 10, 10));
        button_frame.pack(fill='x')
        btn_carregar = tk.Button(button_frame, text="Carregar no simulador", command=lambda: carregar(), bg="#FFB300")
        btn_editar = tk.Button(button_frame, text="Editar Dados da Cotação", command=lambda: abrir_editar_salva(),
                               bg="#4096EE")
        btn_pdf = tk.Button(button_frame, text="Abrir PDF", command=lambda: abrir_pdf(), bg="#8E24AA", fg="white")
        btn_arquivar = tk.Button(button_frame, text="Arquivar/Restaurar", command=lambda: arquivar_desarquivar(),
                                 bg="#777777", fg="white")
        btn_apagar = tk.Button(button_frame, text="Apagar", command=lambda: apagar(), bg="#D62828", fg="white")
        btn_carregar.pack(side=tk.LEFT, padx=2);
        btn_editar.pack(side=tk.LEFT, padx=2);
        btn_pdf.pack(side=tk.LEFT, padx=2)
        btn_arquivar.pack(side=tk.LEFT, padx=(15, 2));
        btn_apagar.pack(side=tk.LEFT, padx=2)

        def get_selected_files():
            selected_indices = lb.curselection()
            if not selected_indices:
                messagebox.showwarning("Aviso", "Nenhuma cotação selecionada.", parent=top);
                return []
            return [lista_cotacoes_filtrada[i] for i in selected_indices]

        def carregar():
            selected_files = get_selected_files()
            if len(selected_files) != 1:
                messagebox.showwarning("Aviso", "Por favor, selecione apenas uma cotação para carregar.", parent=top);
                return
            _nome_arquivo, d, _is_archived = selected_files[0]
            self.dados_cotacao_atual = d
            config.itens_sacola.clear();
            config.itens_sacola.extend(d.get('itens', []))
            self.atualizar_lista_itens();
            self.atualizar_status_cotacao()
            self.txt_resultado.config(state='normal');
            self.txt_resultado.delete("1.0", tk.END);
            self.txt_resultado.config(state='disabled')
            if config.itens_sacola:
                first_item = config.itens_sacola[0]
                self.cb_uf_origem.set(first_item.get('uf_origem', "SP"));
                self.cb_uf_destino.set(first_item.get('uf_destino', config.ufs[0]))
            vendedor_codigo = d.get('vendedor_codigo')
            if vendedor_codigo:
                for opt in self.cb_vendedor['values']:
                    if opt.endswith(f"Código {vendedor_codigo}"): self.cb_vendedor.set(opt); break
            messagebox.showinfo("Carregado", "Cotação carregada no simulador. ✅", parent=top);
            top.destroy()

        def abrir_editar_salva():
            selected_files = get_selected_files()
            if len(selected_files) != 1:
                messagebox.showwarning("Aviso", "Por favor, selecione apenas uma cotação para editar.", parent=top);
                return
            nome_arquivo, dados_cotacao, is_archived = selected_files[0]
            edit_top = tk.Toplevel(self.master);
            edit_top.title(f"Editar Cotação: {dados_cotacao['numero']}")
            edit_top.geometry("400x450");
            edit_top.transient(top);
            edit_top.grab_set();
            edit_top.focus_set()
            campos = [("Empresa (cliente)", "empresa_cliente"), ("Nome do contato", "cliente"), ("Depto", "depto"),
                      ("E-mail", "email"), ("Prazo (dias)", "prazo"), ("Cond. pagamento", "condpag")]
            entries = {}
            for i, (lbl, key) in enumerate(campos):
                tk.Label(edit_top, text=lbl).grid(row=i, column=0, sticky='e', padx=3, pady=5)
                e = tk.Entry(edit_top, width=32);
                e.grid(row=i, column=1, padx=3, pady=5);
                e.insert(0, dados_cotacao.get(key, ""));
                entries[key] = e
            tk.Label(edit_top, text="OBS.:").grid(row=len(campos), column=0, sticky='ne', padx=3, pady=5)
            obs_text = tk.Text(edit_top, width=32, height=5);
            obs_text.grid(row=len(campos), column=1, padx=3, pady=5)
            obs_text.insert("1.0", dados_cotacao.get("observacao", ""))

            def salvar_alteracoes():
                try:
                    for key, entry in entries.items(): dados_cotacao[key] = entry.get().strip()
                    dados_cotacao['observacao'] = obs_text.get("1.0", tk.END).strip()
                    current_dir = config.DIR_ARQUIVADAS if is_archived else config.DIR_COTACOES
                    with open(os.path.join(current_dir, nome_arquivo), "w", encoding="utf-8") as f:
                        json.dump(dados_cotacao, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("Salvo", "Cotação atualizada com sucesso.", parent=edit_top)
                    edit_top.destroy();
                    popular_lista_master()
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}", parent=edit_top)

            tk.Button(edit_top, text="Salvar Alterações", command=salvar_alteracoes, bg="#4CAF50", fg="white").grid(
                row=len(campos) + 1, column=1, pady=10)

        def abrir_pdf():
            selected_files = get_selected_files()
            if len(selected_files) != 1:
                messagebox.showwarning("Aviso", "Por favor, selecione apenas uma cotação para abrir o PDF.",
                                       parent=top);
                return
            _nome_arquivo, dados_cotacao, is_archived = selected_files[0]
            current_dir = config.DIR_ARQUIVADAS if is_archived else config.DIR_COTACOES
            pdf_path = os.path.join(current_dir, f"{dados_cotacao['numero']}_cotacao.pdf")
            if not os.path.exists(pdf_path):
                if messagebox.askyesno("PDF não encontrado",
                                       "O PDF desta cotação não foi encontrado. Deseja gerá-lo agora?", parent=top):
                    try:
                        temp_sacola_original = list(config.itens_sacola)
                        config.itens_sacola = dados_cotacao.get('itens', [])
                        if not config.itens_sacola:
                            messagebox.showwarning("Aviso", "Esta cotação não possui itens para gerar um PDF.",
                                                   parent=top)
                            config.itens_sacola = temp_sacola_original;
                            return
                        total_produtos, tot_ipi, tot_icms_st, tot_difal, total_geral, tot_fcp, _ = fiscal_logic.simular_sacola()
                        dados_completos = {**dados_cotacao, "total_produtos": total_produtos, "total_ipi": tot_ipi,
                                           "total_icms_st": tot_icms_st, "total_difal": tot_difal,
                                           "total_geral": total_geral}
                        pdf_generator.gerar_pdf_cotacao(dados_completos, config.empresa_orcamento, current_dir)
                        config.itens_sacola = temp_sacola_original
                    except Exception as e:
                        messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF:\n{e}", parent=top)
                        config.itens_sacola = temp_sacola_original;
                        return
            try:
                if os.name == 'nt':
                    os.startfile(pdf_path)
                elif os.name == 'posix':
                    webbrowser.open(r'file://' + os.path.realpath(pdf_path))
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o PDF.\nErro: {e}", parent=top)

        def apagar():
            selected_files = get_selected_files()
            if not selected_files: return
            if messagebox.askyesno("Confirmar Exclusão",
                                   f"Tem certeza que deseja apagar {len(selected_files)} cotação(ões) PERMANENTEMENTE?",
                                   icon='warning', parent=top):
                for nome_arquivo, dados, is_archived in selected_files:
                    current_dir = config.DIR_ARQUIVADAS if is_archived else config.DIR_COTACOES
                    try:
                        os.remove(os.path.join(current_dir, nome_arquivo))
                        pdf_path = os.path.join(current_dir, f"{dados['numero']}_cotacao.pdf")
                        if os.path.exists(pdf_path): os.remove(pdf_path)
                    except Exception as e:
                        messagebox.showerror("Erro", f"Não foi possível apagar o arquivo {nome_arquivo}.\nErro: {e}",
                                             parent=top)
                popular_lista_master()

        def arquivar_desarquivar():
            selected_files = get_selected_files()
            if not selected_files: return
            for nome_arquivo, dados, is_archived in selected_files:
                origem_dir = config.DIR_ARQUIVADAS if is_archived else config.DIR_COTACOES
                destino_dir = config.DIR_COTACOES if is_archived else config.DIR_ARQUIVADAS
                os.makedirs(destino_dir, exist_ok=True)
                try:
                    shutil.move(os.path.join(origem_dir, nome_arquivo), os.path.join(destino_dir, nome_arquivo))
                    pdf_path_origem = os.path.join(origem_dir, f"{dados['numero']}_cotacao.pdf")
                    if os.path.exists(pdf_path_origem): shutil.move(pdf_path_origem, os.path.join(destino_dir,
                                                                                                  f"{dados['numero']}_cotacao.pdf"))
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível mover o arquivo {nome_arquivo}.\nErro: {e}",
                                         parent=top)
            popular_lista_master()

        def filtrar_lista(event=None):
            termo = entry_busca.get().lower();
            ver_arquivos = ver_arquivadas_var.get()
            lb.delete(0, tk.END);
            lista_cotacoes_filtrada.clear()
            sorted_items = sorted(todas_as_cotacoes, key=lambda item: datetime.strptime(item[1]['data'], "%d/%m/%Y"),
                                  reverse=True)
            for nome_arquivo, dados, is_archived in sorted_items:
                if is_archived != ver_arquivos: continue
                texto_busca = f"{dados['numero']} {dados['data']} {dados.get('empresa_cliente', '')} {dados.get('vendedor_nome', '')}"
                for item_cotacao in dados.get('itens',
                                              []): texto_busca += f" {item_cotacao.get('descricao_usuario', '')}"
                if termo in texto_busca.lower():
                    display_text = f"{dados['numero']} | {dados['data']} | {dados.get('empresa_cliente', 'N/A')} | Vendedor: {dados.get('vendedor_nome', 'N/A')}"
                    lb.insert(tk.END, display_text)
                    lista_cotacoes_filtrada.append((nome_arquivo, dados, is_archived))

        def popular_lista_master():
            todas_as_cotacoes.clear()
            os.makedirs(config.DIR_COTACOES, exist_ok=True)
            for nome in sorted(os.listdir(config.DIR_COTACOES)):
                if nome.endswith('.json') and not nome.endswith('_cotacao.json'):
                    try:
                        with open(os.path.join(config.DIR_COTACOES, nome), "r", encoding="utf-8") as f:
                            d = json.load(f);
                        todas_as_cotacoes.append((nome, d, False))
                    except Exception:
                        pass
            os.makedirs(config.DIR_ARQUIVADAS, exist_ok=True)
            for nome in sorted(os.listdir(config.DIR_ARQUIVADAS)):
                if nome.endswith('.json') and not nome.endswith('_cotacao.json'):
                    try:
                        with open(os.path.join(config.DIR_ARQUIVADAS, nome), "r", encoding="utf-8") as f:
                            d = json.load(f);
                        todas_as_cotacoes.append((nome, d, True))
                    except Exception:
                        pass
            filtrar_lista()

        entry_busca.bind('<KeyRelease>', filtrar_lista)
        popular_lista_master()
        self.master.wait_window(top)


if __name__ == "__main__":
    root = tk.Tk()
    app = FiscalSimulatorApp(root)
    root.mainloop()