import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from gestao import SistemaGestao
from usuario import UsuarioGestao
import pandas as pd
from datetime import datetime, date


class SistemaInterface:
    def __init__(self, master):
        self.master = master
        self.master.geometry('800x600')  # Define o tamanho da janela
        
        # Carrega a imagem de fundo
        bg_image = Image.open('WhatsApp Image 2024-05-10 at 18.14.49.jpeg')
        bg_image = bg_image.resize((800, 600), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        # Cria um canvas e adiciona a imagem de fundo
        self.bg_canvas = tk.Canvas(master, width=800, height=600)
        self.bg_canvas.pack(fill='both', expand=True)
        self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor='nw')

        self.master.title("Gilmar Snooker Bar")
        self.sistema_usuario = UsuarioGestao("banco_dados.db")
        self.sistema_gestao = SistemaGestao("banco_dados.db")
        self.autenticado = False
        
        # Carrega a imagem
        image_login = Image.open('conecte-se.png')
        image_login = image_login.resize((30, 20), Image.LANCZOS)
        self.icon = ImageTk.PhotoImage(image_login)
        
        image_criar_usuario = Image.open('carteira-de-identidade.png')
        image_criar_usuario = image_criar_usuario.resize((30,20), Image.LANCZOS)
        self.icon2 = ImageTk.PhotoImage(image_criar_usuario)
        
        # Configurando estilos do tema
        style = ttk.Style(master)
        style.theme_use("clam")
        style.configure('TButton', foreground='black', background='white', highlightthickness='20', width=20, padx=10, pady=10)
        
        # Variável de autenticação
        self.autenticado = False
        
        # Criar a interface de login
        self.criar_interface_login()
    
    def criar_interface_login(self):
        # Limpa a janela
        for widget in self.bg_canvas.winfo_children():
            widget.destroy()
        
        self.frame_login = ttk.Frame(self.bg_canvas, borderwidth=2, relief="groove", padding="10")
        self.frame_login_window = self.bg_canvas.create_window(400, 300, window=self.frame_login)

        ttk.Label(self.frame_login, text="Usuário:", font=("Helvetica", 16)).grid(row=0, column=0, pady=5)
        self.usuario_entry = ttk.Entry(self.frame_login, font=("Helvetica", 14))
        self.usuario_entry.grid(row=0, column=1, pady=5)

        ttk.Label(self.frame_login, text="Senha:", font=("Helvetica", 16)).grid(row=1, column=0, pady=5)
        self.senha_entry = ttk.Entry(self.frame_login, show="*", font=("Helvetica", 14))
        self.senha_entry.grid(row=1, column=1, pady=5)

        ttk.Button(self.frame_login, text="Entrar", command=self.autenticar, image=self.icon, compound=tk.LEFT).grid(row=2, column=0, pady=10)
        ttk.Button(self.frame_login, text="Cadastrar Usuário", command=self.cadastrar_usuario, image=self.icon2, compound=tk.LEFT).grid(row=2, column=1, pady=10)
    
    def cadastrar_usuario(self):
        # Cria uma nova janela para cadastrar um novo usuário
        cadastro_janela = tk.Toplevel(self.master)
        cadastro_janela.title("Cadastrar Usuário")

        ttk.Label(cadastro_janela, text="Usuário:").grid(row=0, column=0, pady=5)
        novo_usuario_entry = ttk.Entry(cadastro_janela)
        novo_usuario_entry.grid(row=0, column=1, pady=5)

        ttk.Label(cadastro_janela, text="Senha:").grid(row=1, column=0, pady=5)
        nova_senha_entry = ttk.Entry(cadastro_janela, show="*")
        nova_senha_entry.grid(row=1, column=1, pady=5)

        def cadastrar():
            novo_usuario = novo_usuario_entry.get()
            nova_senha = nova_senha_entry.get()
            if self.sistema_usuario.criar_usuario(novo_usuario, nova_senha):
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
                cadastro_janela.destroy()
            else:
                messagebox.showerror("Erro", "Usuário já existe ou houve um erro ao cadastrar.")

        ttk.Button(cadastro_janela, text="Cadastrar", command=cadastrar).grid(row=2, column=0, columnspan=2, pady=10)

    def autenticar(self):
        # Lógica de autenticação
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()
        if self.sistema_usuario.autenticar_usuario(usuario, senha):
            self.autenticado = True
            messagebox.showinfo("Sucesso", "Bem-vindo!")
            self.criar_interface_principal()  # Chama a interface principal após autenticação
        else:
            messagebox.showerror("Erro", "Credenciais inválidas. Tente novamente.")

    def criar_interface_principal(self):
        # Limpa a janela
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Cria o notebook para as abas
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(padx=10, pady=10)

        # Cria as abas
        self.criar_aba_cadastrar_produto()
        self.criar_aba_estoque()
        self.criar_aba_remover_produto()
        self.criar_aba_caixa()
        self.criar_aba_vendas()
        self.criar_aba_historico_vendas()
        
        ttk.Button(self.master, text="Sair", command=self.voltar_para_login).pack()
        ttk.Button(self.master, text="Definir Valor Inicial do Caixa", command=self.definir_valor_inicial_caixa).pack()
    
    def definir_valor_inicial_caixa(self):
        # Cria uma janela para o usuário inserir o valor inicial do caixa
        janela_valor_inicial_caixa = tk.Toplevel(self.master)
        janela_valor_inicial_caixa.title("Definir Valor Inicial do Caixa")

        ttk.Label(janela_valor_inicial_caixa, text="Valor Inicial do Caixa:").grid(row=0, column=0, pady=5)
        valor_inicial_caixa_entry = ttk.Entry(janela_valor_inicial_caixa)
        valor_inicial_caixa_entry.grid(row=0, column=1, pady=5)

        def definir_valor_inicial():
            valor_inicial = float(valor_inicial_caixa_entry.get())
            self.sistema_gestao.definir_valor_inicial_caixa(valor_inicial)
            self.consultar_caixa()  # Atualiza o rótulo de saldo em caixa
            messagebox.showinfo("Sucesso", "Valor inicial do caixa definido com sucesso!")
            janela_valor_inicial_caixa.destroy()

        ttk.Button(janela_valor_inicial_caixa, text="Definir", command=definir_valor_inicial).grid(row=1, column=0, columnspan=2, pady=10)
            
    def voltar_para_login(self):
        # Limpa a janela e volta para a interface de login
        self.master.destroy()  # Destroi a janela atual
        root = tk.Tk()  # Cria uma nova janela
        app = SistemaInterface(root)  # Cria a interface de login
        root.mainloop()

    def criar_aba_cadastrar_produto(self):
        # Cria a aba para cadastrar produtos
        self.aba_cadastrar_produto = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_cadastrar_produto, text="Cadastrar Produto")

        ttk.Label(self.aba_cadastrar_produto, text="Produto:").grid(row=0, column=0, pady=5)
        self.produto_entry = ttk.Entry(self.aba_cadastrar_produto)
        self.produto_entry.grid(row=0, column=1, pady=5)

        ttk.Label(self.aba_cadastrar_produto, text="Quantidade:").grid(row=1, column=0, pady=5)
        self.quantidade_entry = ttk.Entry(self.aba_cadastrar_produto)
        self.quantidade_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.aba_cadastrar_produto, text="Preço de Compra:").grid(row=2, column=0, pady=5)
        self.preco_compra_entry = ttk.Entry(self.aba_cadastrar_produto)
        self.preco_compra_entry.grid(row=2, column=1, pady=5)

        ttk.Label(self.aba_cadastrar_produto, text="Preço de Venda:").grid(row=3, column=0, pady=5)
        self.preco_venda_entry = ttk.Entry(self.aba_cadastrar_produto)
        self.preco_venda_entry.grid(row=3, column=1, pady=5)

        ttk.Button(self.aba_cadastrar_produto, text="Cadastrar Produto", command=self.adicionar_produto).grid(row=4, column=0, columnspan=2, pady=10)

    def criar_aba_estoque(self):
        # Cria a aba para consulta de estoque
        self.aba_estoque = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_estoque, text="Consultar Estoque")

        ttk.Label(self.aba_estoque, text="Produto:").grid(row=0, column=0, pady=5)
        self.consulta_produto_entry = ttk.Entry(self.aba_estoque)
        self.consulta_produto_entry.grid(row=0, column=1, pady=5)

        self.consultar_button = ttk.Button(self.aba_estoque, text="Consultar Estoque", command=self.consultar_estoque)
        self.consultar_button.grid(row=0, column=2, pady=5)

        self.estoque_label = ttk.Label(self.aba_estoque, text="")
        self.estoque_label.grid(row=1, column=0, columnspan=3, pady=5)

    def criar_aba_remover_produto(self):
        # Cria a aba para listar e remover produtos do estoque
        self.aba_remover_produto = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_remover_produto, text="Remover Produto")

        # Cria a tabela de produtos
        self.lista_produtos = ttk.Treeview(self.aba_remover_produto, columns=("produto", "quantidade", "preco_compra", "preco_venda"), show="headings")
        self.lista_produtos.heading("produto", text="Produto")
        self.lista_produtos.heading("quantidade", text="Quantidade")
        self.lista_produtos.heading("preco_compra", text="Preço de Compra")
        self.lista_produtos.heading("preco_venda", text="Preço de Venda")
        self.lista_produtos.grid(row=0, column=0, pady=5)

        self.atualizar_lista_estoque()

        ttk.Label(self.aba_remover_produto, text="Quantidade a ser removida:").grid(row=1, column=0, pady=5)
        self.quantidade_remover_entry = ttk.Entry(self.aba_remover_produto)
        self.quantidade_remover_entry.grid(row=1, column=1, pady=5)

        ttk.Button(self.aba_remover_produto, text="Remover Produto Selecionado", command=self.remover_produto_selecionado).grid(row=2, column=0, columnspan=2, pady=5)
                    
    def criar_aba_caixa(self):
        # Cria a aba para consultar o saldo em caixa e lucro diário
        self.aba_caixa = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_caixa, text="Caixa")

        self.saldo_label = ttk.Label(self.aba_caixa, text="")
        self.saldo_label.grid(row=0, column=0, pady=5)

        ttk.Button(self.aba_caixa, text="Consultar Caixa", command=self.consultar_caixa).grid(row=1, column=0, pady=5)

    def criar_aba_vendas(self):
        # Cria a aba para iniciar uma nova janela de vendas
        self.aba_vendas = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_vendas, text="Vendas")

        ttk.Button(self.aba_vendas, text="Abrir Janela de Vendas", command=self.abrir_janela_vendas).grid(row=0, column=0, pady=5)

    def abrir_janela_vendas(self):
        # Cria uma nova janela para realizar vendas
        janela_vendas = tk.Toplevel(self.master)
        janela_vendas.title("Realizar Venda")

        ttk.Label(janela_vendas, text="Produto:").grid(row=0, column=0, pady=5)
        vendas_produto_entry = ttk.Entry(janela_vendas)
        vendas_produto_entry.grid(row=0, column=1, pady=5)

        ttk.Label(janela_vendas, text="Quantidade:").grid(row=1, column=0, pady=5)
        vendas_quantidade_entry = ttk.Entry(janela_vendas)
        vendas_quantidade_entry.grid(row=1, column=1, pady=5)

        ttk.Button(janela_vendas, text="Vender", command=lambda: self.realizar_venda(vendas_produto_entry.get(), int(vendas_quantidade_entry.get()))).grid(row=2, column=0, columnspan=2, pady=10)

    def consultar_estoque(self):
        produto = self.consulta_produto_entry.get()
        quantidade = self.sistema_gestao.consultar_estoque(produto)
        self.estoque_label.config(text=f"Quantidade em Estoque de {produto}: {quantidade}")

    def atualizar_lista_estoque(self):
        # Limpa a lista atual
        for i in self.lista_produtos.get_children():
            self.lista_produtos.delete(i)

        # Preenche a lista com produtos em estoque
        produtos = self.sistema_gestao.listar_produtos()
        for produto in produtos:
            self.lista_produtos.insert("", "end", values=(produto["produto"], produto["quantidade"], produto["preco_compra"], produto["preco_venda"]))

    def remover_produto_selecionado(self):
        # Obtém o item selecionado na lista
        item_selecionado = self.lista_produtos.selection()
        if item_selecionado:
            # Obtém os valores do produto selecionado
            valores = self.lista_produtos.item(item_selecionado)["values"]
            produto = valores[0]
            quantidade_remover = int(self.quantidade_remover_entry.get())

            # Verifica se a quantidade a ser removida é válida
            if quantidade_remover <= 0:
                messagebox.showerror("Erro", "A quantidade a ser removida deve ser maior que zero.")
                return

            # Remove a quantidade especificada do produto
            nova_quantidade = valores[1] - quantidade_remover
            if nova_quantidade < 0:
                messagebox.showerror("Erro", "A quantidade a ser removida excede a quantidade atual em estoque.")
                return
            elif nova_quantidade == 0:
                # Se a nova quantidade for zero, remove o produto completamente
                self.sistema_gestao.remover_produto(produto)
            else:
                # Atualiza a quantidade do produto
                self.sistema_gestao.atualizar_quantidade_produto(produto, nova_quantidade)

            # Atualiza a lista
            self.atualizar_lista_estoque()

    def consultar_caixa(self):
        saldo = self.sistema_gestao.consultar_saldo()
        lucro_diario = self.sistema_gestao.lucro_diario
        self.saldo_label.config(text=f"Saldo em Caixa: R${saldo:.2f}\nLucro Diário: R${lucro_diario:.2f}")

    def adicionar_produto(self):
        produto = self.produto_entry.get()
        quantidade = int(self.quantidade_entry.get())
        preco_compra = float(self.preco_compra_entry.get())
        preco_venda = float(self.preco_venda_entry.get())

        self.sistema_gestao.adicionar_produto(produto, quantidade, preco_compra, preco_venda)
        messagebox.showinfo("Sucesso", f"Produto {produto} cadastrado com sucesso!")

        # Limpa os campos após o cadastro
        self.produto_entry.delete(0, tk.END)
        self.quantidade_entry.delete(0, tk.END)
        self.preco_compra_entry.delete(0, tk.END)
        self.preco_venda_entry.delete(0, tk.END)

        # Atualiza a lista de produtos no estoque
        self.atualizar_lista_estoque()

    def realizar_venda(self, produto, quantidade):
        lucro = self.sistema_gestao.vender_produto(produto, quantidade)
        if lucro is not None:
            messagebox.showinfo("Sucesso", f"Venda de {quantidade} unidade(s) de {produto} realizada com sucesso!\nLucro: R${lucro:.2f}")
            self.atualizar_lista_estoque()
            self.atualizar_lista_vendas()
        else:
            messagebox.showerror("Erro", "Não há quantidade suficiente em estoque para realizar a venda.")
    
    def criar_aba_historico_vendas(self):
        # Cria a aba para visualizar o histórico de vendas
        self.aba_historico_vendas = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_historico_vendas, text="Histórico de Vendas")

        # Cria a tabela de vendas
        self.lista_vendas = ttk.Treeview(self.aba_historico_vendas, columns=("produto", "quantidade", "lucro", "data"), show="headings")
        self.lista_vendas.heading("produto", text="Produto")
        self.lista_vendas.heading("quantidade", text="Quantidade")
        self.lista_vendas.heading("lucro", text="Lucro")
        self.lista_vendas.heading("data", text="Data")
        self.lista_vendas.grid(row=0, column=0, pady=5)

        self.atualizar_lista_vendas()
        ttk.Label(self.aba_historico_vendas, text="Data Início:").grid(row=1, column=0, pady=1)
        self.data_inicio_entry = ttk.Entry(self.aba_historico_vendas)
        self.data_inicio_entry.grid(row=1, column=1, pady=5)

        ttk.Label(self.aba_historico_vendas, text="Data Fim:").grid(row=2, column=0, pady=1)
        self.data_fim_entry = ttk.Entry(self.aba_historico_vendas)
        self.data_fim_entry.grid(row=2, column=1, pady=5)

        ttk.Button(self.aba_historico_vendas, text="Gerar Relatório", command=self.gerar_relatorio).grid(row=3, column=0, columnspan=2, pady=10)
    
    def gerar_relatorio(self):
        data_inicio = self.data_inicio_entry.get()
        data_fim = self.data_fim_entry.get()
        print("Gerando relatório...")
        print(f"Data de início: {data_inicio}")
        print(f"Data de fim: {data_fim}")
        
        # Obter dados do relatório
        vendas = self.sistema_gestao.relatorio_vendas(data_inicio, data_fim)
        
        # Verifica se há vendas
        if vendas:
            # Converter para DataFrame
            df = pd.DataFrame(vendas, columns=["id", "produto", "quantidade", "lucro", "data"])
            
            # Salvar relatório em um arquivo Excel
            df.to_excel("relatorio_vendas.xlsx", index=False)
            print("Relatório gerado com sucesso!")
        else:
            print("Nenhuma venda encontrada para o intervalo de datas fornecido.")

    def atualizar_lista_vendas(self):
        # Limpa a lista atual
        for i in self.lista_vendas.get_children():
            self.lista_vendas.delete(i)

        # Preenche a lista com o histórico de vendas
        vendas = self.sistema_gestao.relatorio_vendas()
        for venda in vendas:
            self.lista_vendas.insert("", "end", values=(venda[1], venda[2], venda[3], venda[4]))
    
    def gerar_relatorio_excel(self):
        try:
            # Obtenha os dados do relatório
            data_inicio = self.data_inicio_entry.get()
            data_fim = self.data_fim_entry.get()
            vendas = self.sistema_gestao.relatorio_vendas(data_inicio, data_fim)

            # Verifica se há vendas
            if not vendas:
                messagebox.showinfo("Informação", "Nenhuma venda encontrada para o intervalo de datas fornecido.")
                return

            # Converter para DataFrame
            df = pd.DataFrame(vendas, columns=["id", "produto", "quantidade", "lucro", "data"])

            # Salvar relatório em um arquivo Excel
            df.to_excel("relatorio_vendas.xlsx", index=False)
            messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o relatório: {e}")
            
    def atualizar_produto(self):
        # Obtém os valores dos campos de entrada
        produto = self.produto_entry.get()
        nova_quantidade = int(self.quantidade_entry.get())
        novo_preco_compra = float(self.preco_compra_entry.get())
        novo_preco_venda = float(self.preco_venda_entry.get())

        # Chama o método atualizar_produto da classe SistemaGestao
        self.sistema_gestao.atualizar_produto(produto, nova_quantidade, novo_preco_compra, novo_preco_venda)

        # Limpa os campos após a atualização
        self.produto_entry.delete(0, tk.END)
        self.quantidade_entry.delete(0, tk.END)
        self.preco_compra_entry.delete(0, tk.END)
        self.preco_venda_entry.delete(0, tk.END)

        # Atualiza a lista de produtos no estoque
        self.atualizar_lista_estoque()

 