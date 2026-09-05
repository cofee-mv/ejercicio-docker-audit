# Ejercicio Docker Audit

Proyecto de auditoría, refactorización y despliegue de una aplicación Flask en AWS EC2 con Docker, CI/CD y monitoreo.

## 🚀 Tecnologías

- **Python** / **Flask** — Aplicación web
- **Docker** / **Docker Compose** — Contenedorización
- **MySQL 8.0** — Base de datos
- **Nginx Proxy Manager** — Proxy inverso
- **Dozzle** — Visor de logs de Docker
- **Uptime Kuma** — Monitoreo de servicios
- **GitHub Actions** — CI/CD (Pytest, Bandit, Trivy)

---

## 🌐 Subdominios (Duck DNS)

| Subdominio | Servicio | Acceso |
|------------|----------|--------|
| [api890.duckdns.org](https://api890.duckdns.org) | Backend / API (Flask) | Público |
| [dozzle987.duckdns.org](https://dozzle987.duckdns.org) | Dozzle (logs Docker) | Público |
| [kumma90.duckdns.org](https://kumma90.duckdns.org) | Uptime Kuma (monitoreo) | Público |
| [manager67.duckdns.org](https://manager67.duckdns.org) | Nginx Proxy Manager (admin) | Público |

> Los subdominios apuntan a la IP pública de la instancia EC2: `3.141.8.126`

### Arquitectura

```text
                        INTERNET
                            │
                            │ HTTPS :443
                            ▼
                    ┌─────────────────────┐
                    │ NGINX PROXY MANAGER │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    api890.duckdns.org  dozzle987.duckdns.org  kumma90.duckdns.org
              │               │               │
              ▼               ▼               ▼
          Backend:5050     Dozzle:8080     Uptime Kuma:3001
              │
              ▼
          MySQL:3306
```
> Además: `manager67.duckdns.org` → Nginx Proxy Manager (admin, puerto 81)

### Puertos expuestos

| Puerto | Servicio | Acceso |
|--------|----------|--------|
| **80** | HTTP → Nginx Proxy Manager | Público |
| **443** | HTTPS → Nginx Proxy Manager | Público |
| 5050 | Backend | Solo interno |
| 3306 | MySQL | Solo interno |
| 3001 | Uptime Kuma | Solo interno |
| 8080 | Dozzle | Solo interno |

---

## 📋 Auditoría de Seguridad — Fase 1

Se realizó una auditoría de seguridad sobre el proyecto utilizando la herramienta **Bandit**, un analizador estático de seguridad para código Python. El análisis cubrió un total de 34 líneas de código y detectó 6 problemas de seguridad directamente, además de 6 problemas adicionales identificados manualmente.

### Tabla de Auditoría Inicial

| # | Vulnerabilidad | Archivo | Severidad | Descripción | Estado |
|---|----------------|---------|-----------|-------------|--------|
| 1 | Credenciales en texto plano | app.py:10 | High | Contraseña de BD hardcodeada. CWE-259. | Corregido |
| 2 | SQL Injection | app.py:25 | High | Concatenación directa de input en query SQL. CWE-89. | Corregido |
| 3 | Flask Debug True | app.py:35 | High | debug=True expone debugger Werkzeug. CWE-94. | Corregido |
| 4 | Bind a todas las interfaces | app.py:35 | Medium | Binding a 0.0.0.0. CWE-605. | Aceptado (Docker) |
| 5 | Generador pseudo-aleatorio inseguro | app.py:30 | Medium | Uso de random.random(). CWE-330. | Corregido |
| 6 | Health check con división por cero | app.py:31 | Medium | División por cero aleatoria en /health. | Corregido |
| 7 | Exposición de errores al cliente | app.py:20 | Medium | Mensaje de excepción retornado al cliente. | Corregido |
| 8 | Sin variables de entorno | app.py:8-11 | Medium | Config sensible en código fuente. | Corregido |
| 9 | Imagen Docker desactualizada | Dockerfile:1 | Medium | Python 3.8 end-of-life. | Corregido |
| 10 | Assert en código de test | test_app.py:7 | Low | Uso de assert. CWE-703. | Aceptado (tests) |
| 11 | Sin requirements.txt | Dockerfile:6 | Low | Dependencias hardcodeadas. | Corregido |
| 12 | Sin .gitignore / .dockerignore | raíz | Low | No existen archivos ignore. | Corregido |

---

## 🔄 CI/CD — GitHub Actions

El pipeline se ejecuta automáticamente en cada push o pull request a `main`:

| Job | Herramienta | Propósito |
|-----|-------------|-----------|
| Tests y Análisis | Pytest | Ejecutar pruebas automatizadas |
| Tests y Análisis | Bandit | Análisis de seguridad Python |
| Escaneo Docker | Trivy (imagen) | Escanear vulnerabilidades del contenedor |
| Escaneo Docker | Trivy (filesystem) | Escanear vulnerabilidades de archivos |
| Despliegue | SSH | Desplegar automáticamente en EC2 |

El despliegue automático solo se ejecuta si los jobs de prueba y seguridad pasan.

### Despliegue automático en EC2

El job `Despliegue en EC2` se conecta por SSH a la instancia y ejecuta:

```bash
cd ~/ejercicio-docker-audit
git pull origin main
sudo docker compose down
sudo docker compose build --no-cache app-backend
sudo docker compose up -d
sudo docker system prune -f
```

---

## 🛠️ Ejecución local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pruebas
python -m pytest test_app.py -v

# Ejecutar análisis de seguridad
python -m bandit -r . -f txt -lll
```

---

## 📄 Estructura del proyecto

```
ejercicio-docker-audit/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline CI/CD
├── app.py                      # Aplicación Flask
├── Dockerfile                  # Imagen Docker
├── docker-compose.yml          # Orquestación Docker
├── requirements.txt            # Dependencias Python
├── test_app.py                 # Pruebas automatizadas
├── .env.example                # Plantilla de variables de entorno
├── .gitignore                  # Archivos excluidos de git
├── .dockerignore               # Archivos excluidos de Docker build
└── .trivyignore                # Vulnerabilidades ignoradas por Trivy
```