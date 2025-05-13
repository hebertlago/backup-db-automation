from flask import Flask, request, jsonify
import subprocess
import datetime
import os
import requests
import shutil
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

os.environ["PATH"] += os.pathsep + r"C:\Program Files\PostgreSQL\14\bin"

app = Flask(__name__)

BACKUPS_DIR = "backups"
os.makedirs(BACKUPS_DIR, exist_ok=True)

SCOPES = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
LAST_FILE_ID_PATH = 'last_drive_file.txt'

def authenticate_drive():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def delete_drive_file(file_id):
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"Arquivo do Drive {file_id} excluído com sucesso.")
    except Exception as e:
        print(f"Falha ao excluir arquivo do Drive {file_id}: {e}")

def empty_drive_trash():
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)
    try:
        service.files().emptyTrash().execute()
        print("Lixeira do Drive esvaziada com sucesso.")
    except Exception as e:
        print(f"Falha ao esvaziar lixeira: {e}")

def upload_file_to_drive(file_path, file_name):
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    permission = {'role': 'reader', 'type': 'anyone'}
    service.permissions().create(fileId=file_id, body=permission).execute()

    # Salva o file_id do último backup
    with open(LAST_FILE_ID_PATH, 'w') as f:
        f.write(file_id)

    link = f'https://drive.google.com/file/d/{file_id}/view?usp=sharing'
    return link

@app.route('/backup', methods=['POST'])
def backup():
    if not request.is_json:
        return jsonify({"status": "erro", "mensagem": "Body não é JSON"}), 400

    data = request.get_json()
    host = data.get('host')
    user = data.get('user')
    db = data.get('db')
    password = data.get('password')
    webhook_url = data.get('webhook_url')

    required_fields = ['host', 'user', 'db', 'password', 'webhook_url']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"status": "erro", "mensagem": f"Campo obrigatório faltando: {field}"}), 400

    if shutil.which('pg_dump') is None:
        return jsonify({"status": "erro", "mensagem": "pg_dump não encontrado no servidor"}), 500

    data_atual = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    nome_arquivo = f"backup_{data_atual}.sql"
    caminho_arquivo = os.path.join(BACKUPS_DIR, nome_arquivo)

    comando = [
        "C:/Program Files/PostgreSQL/14/bin/pg_dump.exe",
        "-h", host,
        "-U", user,
        "-F", "c",
        "-b",
        "-f", caminho_arquivo,
        db
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    try:
        result = subprocess.run(comando, check=True, env=env, capture_output=True, text=True)
        print(f"Backup criado com sucesso: {caminho_arquivo}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")

        # Exclui último backup do Drive, se existir
        if os.path.exists(LAST_FILE_ID_PATH):
            with open(LAST_FILE_ID_PATH, 'r') as f:
                last_file_id = f.read().strip()
                if last_file_id:
                    delete_drive_file(last_file_id)

        # Upload para Google Drive e gerar link
        link = upload_file_to_drive(caminho_arquivo, nome_arquivo)
        print(f"Link do Google Drive: {link}")

        # Envia link para o webhook
        payload = {"backup_link": link}
        response = requests.post(webhook_url, json=payload, timeout=30)

        # Limpeza local de backups antigos (após upload)
        backups = sorted(os.listdir(BACKUPS_DIR))
        if len(backups) > 1:
            oldest_backup = backups[0]
            oldest_path = os.path.join(BACKUPS_DIR, oldest_backup)
            try:
                os.remove(oldest_path)
                print(f"Backup antigo removido localmente: {oldest_backup}")
            except PermissionError:
                print(f"Não foi possível remover {oldest_backup}, arquivo ainda está em uso.")

        # ⚠ Opcional: Limpar lixeira do Drive (descomente se quiser)
        empty_drive_trash()

        if 200 <= response.status_code < 300:
            print("Link enviado com sucesso para o webhook.")
            return jsonify({"status": "sucesso", "mensagem": f"Backup enviado para webhook. Status: {response.status_code}"}), 200
        else:
            print(f"Falha ao enviar para webhook. Status: {response.status_code}")
            return jsonify({"status": "erro", "mensagem": f"Falha ao enviar para webhook. Status: {response.status_code}"}), 500

    except subprocess.CalledProcessError as e:
        mensagem = f"Erro ao executar o backup: {e.stderr}"
        print(mensagem)
        return jsonify({"status": "erro", "mensagem": mensagem}), 500

@app.route('/')
def home():
    return jsonify({"mensagem": "Servidor de backup rodando. Envie POST para /backup com JSON contendo host, user, db, password, webhook_url."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1410, debug=True)
