import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pacientes_raspados.db")

def inicializar_banco():
    """
    Cria a conexão com o banco de dados e a tabela 'pacientes' se ela não existir.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id_paciente INTEGER PRIMARY KEY,
                nome_paciente TEXT,
                status TEXT NOT NULL,
                data_verificacao DATETIME NOT NULL
            )
        ''')
        conn.commit()
        print(f"Banco de dados '{DB_FILE}' inicializado e tabela 'pacientes' pronta.")
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def verificar_id_existente(id_paciente):
    """
    Verifica se um ID de paciente já existe no banco de dados.
    Retorna True se existir, False caso contrário.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pacientes WHERE id_paciente = ?", (id_paciente,))
        resultado = cursor.fetchone()
        return resultado is not None
    except Exception as e:
        print(f"Erro ao verificar ID {id_paciente}: {e}")
        return False 
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def registrar_paciente(id_paciente, status, nome_paciente=None):
    """
    Registra o resultado do scraping para um determinado ID de paciente.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        data_atual = datetime.now()
        cursor.execute('''
            INSERT INTO pacientes (id_paciente, nome_paciente, status, data_verificacao)
            VALUES (?, ?, ?, ?)
        ''', (id_paciente, nome_paciente, status, data_atual))
        conn.commit()
        print(f"ID {id_paciente} registrado com status '{status}'.")
    except sqlite3.IntegrityError:
        print(f"ID {id_paciente} já existe no banco. Ignorando inserção duplicada.")
    except Exception as e:
        print(f"Erro ao registrar paciente com ID {id_paciente}: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def obter_maior_id_verificado():
    """
    Encontra o maior ID de paciente já registrado no banco.
    Retorna o ID (int) ou None se o banco estiver vazio.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id_paciente) FROM pacientes")
        resultado = cursor.fetchone()
        return resultado[0] if resultado and resultado[0] is not None else None
    except Exception as e:
        print(f"Erro ao obter o maior ID verificado: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def obter_menor_id_verificado(id_base):
    """
    Encontra o menor ID de paciente já registrado, que seja menor que o ID base.
    Retorna o ID (int) ou None se não houver nenhum.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(id_paciente) FROM pacientes WHERE id_paciente < ?", (id_base,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado and resultado[0] is not None else None
    except Exception as e:
        print(f"Erro ao obter o menor ID verificado: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()
