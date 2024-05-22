import sqlite3

class UsuarioGestao:
    def __init__(self, banco_dados):
        self.conn = sqlite3.connect(banco_dados)
        self.criar_tabela_usuarios()

    def criar_tabela_usuarios(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def criar_usuario(self, usuario, senha):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO usuarios (usuario, senha)
                VALUES (?, ?)
            ''', (usuario, senha))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Usuário já existe
            return False

    def autenticar_usuario(self, usuario, senha):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM usuarios WHERE usuario = ? AND senha = ?
        ''', (usuario, senha))
        return cursor.fetchone() is not None
