# 🛡️ Backup Automático de Banco de Dados com Python + Flask + Google Drive

[![Backup Automation CI](https://github.com/hebertlago/backup-db-automation/actions/workflows/backup.yml/badge.svg)](https://github.com/hebertlago/backup-db-automation/actions/workflows/backup.yml)

[![Google Drive API Enabled](https://img.shields.io/badge/Google%20Drive-API%20Enabled-brightgreen?logo=google-drive&logoColor=white)](https://console.cloud.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Backup-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

## 🚀 Funcionalidades
- Backup automatizado do banco de dados PostgreSQL.
- Upload automático para o Google Drive.
- Controle de versão do último backup.
- Autenticação OAuth2 com Google Drive.
- Estrutura simples e prática com Flask.

## 🛠️ Tecnologias Utilizadas
- Python 3.x
- Flask
- Google Drive API
- PostgreSQL (pg_dump)

## 📦 Instalação
Clone o repositório:
```bash
git clone (https://github.com/hebertlago/backup-db-automation)
cd (backup-db-automation)
```

Instale as dependências:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração
1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/).
2. Habilite a API do Google Drive.
3. Baixe as credenciais (credentials.json) e coloque na raiz do projeto.
4. O token de autenticação será gerado automaticamente na primeira execução.

## 🗄️ Como executar
Certifique-se que o PostgreSQL esteja instalado e acessível no PATH.

Execute o script:
```bash
python backup.py
```

## 📄 Estrutura do Projeto
```
backup_db/
├── backup.py                # Script principal
├── requirements.txt         # Dependências do projeto
├── .gitignore               # Arquivos e pastas ignoradas no Git
└── README.md                # Documentação do projeto
```


## 📝 Licença
Este projeto está licenciado sob a licença MIT.

---

Desenvolvido por [Hebert Lago](https://github.com/hebertlago)
