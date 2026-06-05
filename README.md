Django API — Pronto para Render
Estrutura
```
django_render_api/
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── render.yaml
├── .env.example
└── .gitignore
```
Rodar localmente

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Configure o ambiente
cp .env.example .env
# Edite .env e deixe ENVIRONMENT=development

# 3. Suba o servidor
python manage.py runserver
```
Acesse http://localhost:8000 → Swagger UI

Deploy no Render

Opção 1 — via render.yaml (recomendado)
Suba o código no GitHub
No Render, clique em New > Blueprint
Conecte o repositório — o `render.yaml` configura tudo automaticamente

Opção 2 — manual
No Render, clique em New > Web Service
Conecte o repositório
Configure:
Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
Start Command: `gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
Adicione as variáveis de ambiente:
`ENVIRONMENT` = `production`
`SECRET_KEY` = (gere uma chave segura)
`ALLOWED_HOSTS` = `.onrender.com`
Endpoints
Rota	Desenvolvimento	Produção
`/`	Swagger UI	JSON de boas-vindas
`/welcome`	JSON + doc no Swagger	JSON
`/redoc/`	ReDoc UI	—
"# lion-render-django" 
