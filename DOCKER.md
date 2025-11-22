# 🐳 Docker Deployment Guide

Dieses Dokument beschreibt, wie Project Master Enterprise mit Docker deployed wird.

## 🚀 Quick Start

### Mit Docker Compose (Empfohlen)

1. **Clone Repository:**
```bash
git clone <repository-url>
cd ProjectMaster-Enterprise
```

2. **Umgebungsvariablen setzen:**
```bash
cp .env.example .env
# Bearbeite .env und setze SECRET_KEY
```

3. **Container starten:**
```bash
docker-compose up -d
```

4. **Zugriff:**
```
http://localhost:8501
```

### Mit Docker

```bash
# Image bauen
docker build -t projectmaster-enterprise .

# Container starten
docker run -d \
  --name projectmaster \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e SECRET_KEY=your-secret-key \
  projectmaster-enterprise
```

## 📋 Voraussetzungen

- Docker 20.10+
- Docker Compose 2.0+
- Mindestens 512MB RAM
- 2GB freier Speicherplatz

## 🔧 Konfiguration

### Umgebungsvariablen

Wichtige Umgebungsvariablen in `.env`:

```env
SECRET_KEY=your-very-secret-key-change-this
APP_ENV=production
DATABASE_TYPE=json
LOG_LEVEL=INFO
ENABLE_BACKUP=true
```

### Volumes

Die folgenden Verzeichnisse werden als Volumes gemountet:

- `./data` - Projektdaten (JSON-Dateien)
- `./logs` - Application Logs
- `./uploads` - Hochgeladene Dateien
- `./project_images` - Projekt-Bilder
- `./project_docs` - Dokumente

### Ports

- `8501` - Streamlit Web-Interface

## 🔒 Production Best Practices

### 1. Secrets Management

**Nicht** das Standard-Passwort verwenden:

```bash
# Generiere sicheren Secret Key
openssl rand -hex 32

# Setze in .env
SECRET_KEY=<generated-key>
```

### 2. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name projectmaster.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### 3. SSL/TLS

Verwende Let's Encrypt mit Certbot:

```bash
sudo certbot --nginx -d projectmaster.yourdomain.com
```

### 4. Backup-Strategie

```bash
# Automatisches Backup (Cron Job)
# /etc/cron.daily/projectmaster-backup

#!/bin/bash
BACKUP_DIR="/backup/projectmaster"
DATE=$(date +%Y%m%d_%H%M%S)

# Data backup
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /path/to/projectmaster/data

# Keep only last 7 days
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +7 -delete
```

## 🎯 Docker Compose Befehle

### Starten
```bash
docker-compose up -d
```

### Stoppen
```bash
docker-compose down
```

### Logs anzeigen
```bash
docker-compose logs -f
```

### Neustart
```bash
docker-compose restart
```

### Status prüfen
```bash
docker-compose ps
```

### Container betreten
```bash
docker-compose exec projectmaster /bin/bash
```

### Updates deployen
```bash
# Neuen Code pullen
git pull

# Rebuild und restart
docker-compose up -d --build
```

## 🔍 Monitoring & Health Checks

### Health Check Status

```bash
docker inspect --format='{{.State.Health.Status}}' projectmaster-enterprise
```

### Container Logs

```bash
# Real-time logs
docker logs -f projectmaster-enterprise

# Last 100 lines
docker logs --tail 100 projectmaster-enterprise
```

### Resource Usage

```bash
docker stats projectmaster-enterprise
```

## 🐛 Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
docker-compose logs

# Port bereits belegt?
lsof -i :8501

# Permissions prüfen
ls -la data/ logs/
```

### Daten werden nicht persistiert

```bash
# Volume prüfen
docker-compose down
docker volume ls
docker volume inspect projectmaster-enterprise_data
```

### Performance-Probleme

```bash
# Resources erhöhen in docker-compose.yml
services:
  projectmaster:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Updates schlagen fehl

```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 Multi-Container Setup (Advanced)

Für größere Deployments mit PostgreSQL:

```yaml
# Decommentiere in docker-compose.yml:
services:
  projectmaster:
    environment:
      - DATABASE_TYPE=postgres
      - DB_HOST=postgres
      - DB_NAME=projectmaster
      - DB_USER=pmuser
      - DB_PASSWORD=${DB_PASSWORD}
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    # ... (siehe docker-compose.yml)
```

## 📊 Production Checklist

- [ ] SECRET_KEY geändert
- [ ] Admin-Passwort geändert
- [ ] Backup-Strategie implementiert
- [ ] SSL/TLS konfiguriert
- [ ] Firewall-Regeln gesetzt
- [ ] Monitoring aufgesetzt
- [ ] Logs rotieren automatisch
- [ ] Health-Checks funktionieren
- [ ] Resource-Limits gesetzt
- [ ] Updates getestet

## 🔄 Update-Strategie

### Rolling Update

```bash
# Pull neue Version
git pull

# Build neues Image
docker-compose build

# Graceful restart
docker-compose up -d --no-deps --build projectmaster
```

### Rollback

```bash
# Zu vorheriger Version
git checkout <previous-commit>
docker-compose up -d --build
```

## 📈 Skalierung

Für horizontale Skalierung:

```yaml
# docker-compose.scale.yml
services:
  projectmaster:
    deploy:
      replicas: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - projectmaster
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

## 📞 Support

Bei Problemen:
- GitHub Issues: [Link]
- Logs: `docker-compose logs`
- Dokumentation: README.md

---

**Happy Dockering! 🐳**
