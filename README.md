# Travail de maturité
## Messagerie en Python axée sur la vie privée

### Requirements
- Django
- MySQL / MariaDB
- Redis

### Installation
```
source .venv/bin/activate
pip install -r requirements.txt
```

### Installer sur une machine locale 
#### (accesible sur 127.0.0.1:8000)

```
python3 manage.py migrate
python3 manage.py runserver
```

### Installer avec Docker