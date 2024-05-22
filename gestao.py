import sqlite3
from datetime import datetime
 
class SistemaGestao:
    def __init__(self, banco_dados):
        self.conn = sqlite3.connect(banco_dados)
        self.criar_tabelas()
        self.lucro_diario = 0.0

    def criar_tabelas(self):
        cursor = self.conn.cursor()
        # Criação das tabelas para estoque e caixa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estoque (
                produto TEXT PRIMARY KEY,
                quantidade INTEGER,
                preco_compra REAL,
                preco_venda REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS caixa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                saldo REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto TEXT,
                quantidade INTEGER,
                lucro REAL,
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def definir_valor_inicial_caixa(self, valor_inicial):
        cursor = self.conn.cursor()
        # Verifica se já existe um registro na tabela caixa
        cursor.execute('SELECT saldo FROM caixa')
        resultado = cursor.fetchone()
        if resultado:
            # Já existe um valor inicial definido, então atualiza o saldo existente
            cursor.execute('UPDATE caixa SET saldo = ?', (valor_inicial,))
        else:
            # Não existe um valor inicial definido, então insere um novo registro
            cursor.execute('INSERT INTO caixa (saldo) VALUES (?)', (valor_inicial,))
            # Atualiza o lucro diário apenas se não houver valor no caixa
            self.lucro_diario = valor_inicial
        self.conn.commit()
    
    def adicionar_produto(self, produto, quantidade, preco_compra, preco_venda):
        cursor = self.conn.cursor()
        # Verifica se o produto já existe e atualiza se necessário
        cursor.execute('''
            SELECT quantidade FROM estoque WHERE produto = ?
        ''', (produto,))
        resultado = cursor.fetchone()
        if resultado:
            # Atualiza a quantidade e os preços
            nova_quantidade = resultado[0] + quantidade
            cursor.execute('''
                UPDATE estoque
                SET quantidade = ?, preco_compra = ?, preco_venda = ?
                WHERE produto = ?
            ''', (nova_quantidade, preco_compra, preco_venda, produto))
        else:
            # Insere um novo produto
            cursor.execute('''
                INSERT INTO estoque (produto, quantidade, preco_compra, preco_venda)
                VALUES (?, ?, ?, ?)
            ''', (produto, quantidade, preco_compra, preco_venda))
        self.conn.commit()

    def consultar_estoque(self, produto):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT quantidade FROM estoque WHERE produto = ?
        ''', (produto,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0

    def listar_produtos(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT produto, quantidade, preco_compra, preco_venda FROM estoque')
        produtos = cursor.fetchall()
        return [{"produto": p[0], "quantidade": p[1], "preco_compra": p[2], "preco_venda": p[3]} for p in produtos]

    def remover_produto(self, produto):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM estoque WHERE produto = ?', (produto,))
        self.conn.commit()
        
    def vender_produto(self, produto, quantidade):
        cursor = self.conn.cursor()
        
        # Obtenha as informações de estoque e preço do produto
        cursor.execute('SELECT quantidade, preco_compra, preco_venda FROM estoque WHERE produto = ?', (produto,))
        resultado = cursor.fetchone()
        
        if resultado:
            quantidade_estoque, preco_compra, preco_venda = resultado
            
            # Verifica se há quantidade suficiente em estoque
            if quantidade_estoque >= quantidade:
                nova_quantidade = quantidade_estoque - quantidade
                
                # Atualize a quantidade em estoque
                cursor.execute('UPDATE estoque SET quantidade = ? WHERE produto = ?', (nova_quantidade, produto))
                self.conn.commit()
                
                # Calcule o lucro
                custo_compra = quantidade * preco_compra  # Custo das compras
                total_venda = quantidade * preco_venda  # Total da venda
                lucro = total_venda - custo_compra  # Lucro é a diferença
                
                # Atualize o lucro diário
                self.lucro_diario += lucro
                
                cursor.execute('''
                    INSERT INTO historico_vendas (produto, quantidade, lucro)
                    VALUES (?, ?, ?)
                ''', (produto, quantidade, lucro))
                self.conn.commit()
                
                # Retorne o lucro
                return lucro
            
        return None
    
    def relatorio_vendas(self, data_inicio=None, data_fim=None):
        cursor = self.conn.cursor()
        
        try:
            # Converte as datas de string para datetime se elas não estiverem vazias
            if data_inicio and data_fim:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
                cursor.execute('''
                    SELECT id, produto, quantidade, lucro, data
                    FROM historico_vendas
                    WHERE data BETWEEN ? AND ?
                ''', (data_inicio, data_fim))
            else:
                cursor.execute('SELECT id, produto, quantidade, lucro, data FROM historico_vendas')
            
            vendas = cursor.fetchall()
            return vendas
        except Exception as e:
            print(f"Erro ao obter vendas: {e}")
            return []
        

    def adicionar_saldo(self, valor):
        cursor = self.conn.cursor()
        # Verifica se já existe um registro na tabela caixa
        cursor.execute('SELECT saldo FROM caixa')
        resultado = cursor.fetchone()
        if resultado:
            # Atualiza o saldo existente
            novo_saldo = resultado[0] + valor
            cursor.execute('''
                UPDATE caixa SET saldo = ?
            ''', (novo_saldo,))
        else:
            # Insere um novo registro de saldo
            cursor.execute('''
                INSERT INTO caixa (saldo) VALUES (?)
            ''', (valor,))
        self.conn.commit()

    def consultar_saldo(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT saldo FROM caixa')
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0
    
    def atualizar_quantidade_produto(self, produto, nova_quantidade):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE estoque SET quantidade = ? WHERE produto = ?', (nova_quantidade, produto))
        self.conn.commit()
