# 🚀 Quick Start Guide - ProjectMaster Enterprise

Wähle deine bevorzugte Methode zum Starten der App:

---

## 📱 **Option 1: Smartphone/Tablet (Einfachste Methode)**

### Via Streamlit Cloud:
1. Deploy auf [Streamlit Cloud](https://streamlit.io/cloud) (kostenlos)
2. Erhalte eine URL wie: `https://dein-username-projectmaster.streamlit.app`
3. **Auf iPhone/iPad**: Safari öffnen → URL eingeben → Share → "Zum Home-Bildschirm"
4. **Auf Android**: Chrome öffnen → URL eingeben → Menü (⋮) → "Zum Startbildschirm hinzufügen"

✅ **Jetzt als App-Icon auf deinem Smartphone!**

---

## 💻 **Option 2: Desktop - Einfach Starten (Lokal)**

### Windows:
```bash
# Doppelklick auf:
start_windows.bat
```

### Mac/Linux:
```bash
# Im Terminal:
./start_unix.sh
```

➡️ Browser öffnet automatisch auf `http://localhost:8501`

---

## 🐳 **Option 3: Docker (Professionell)**

### Voraussetzung:
- Docker Desktop installieren: https://docker.com

### Starten:

**Windows:**
```bash
# Doppelklick auf:
start_docker.bat
```

**Mac/Linux:**
```bash
docker-compose up -d
open http://localhost:8501
```

### Stoppen:
```bash
docker-compose stop
```

---

## 🎯 **Option 4: Als EXE (Windows)**

### Build EXE:
```bash
# 1. PyInstaller installieren
pip install pyinstaller

# 2. EXE erstellen
pyinstaller deployment/pyinstaller/projectmaster.spec

# 3. EXE finden in:
dist/ProjectMaster/ProjectMaster.exe
```

### EXE starten:
- Doppelklick auf `ProjectMaster.exe`
- Browser öffnet automatisch

⚠️ **Hinweis**: EXE ist ~600MB groß

---

## 📊 **Testdaten erstellen**

Beim ersten Start fragt die App, ob du Testdaten erstellen möchtest.

Oder manuell:
```bash
python create_test_data.py
```

**Erstellt:**
- ✅ 3 Beispiel-Projekte
- ✅ 3 Beispiel-Experimente
- ✅ 3 Test-User (admin, sarah.chen, lisa.mueller)

---

## 🔑 **Login**

### Standard-Benutzer:
```
Benutzername: admin
Passwort: admin123
```

### Weitere Test-User:
```
sarah.chen / password123
lisa.mueller / password123
```

---

## 🌐 **Remote Zugriff (LAN)**

### Zugriff von anderen Geräten im Netzwerk:

1. **Finde deine IP-Adresse:**
   - Windows: `ipconfig` (z.B. 192.168.1.100)
   - Mac/Linux: `ifconfig` oder `ip addr`

2. **Starte mit Network-Flag:**
   ```bash
   streamlit run project_app.py --server.address 0.0.0.0
   ```

3. **Auf anderen Geräten öffnen:**
   ```
   http://192.168.1.100:8501
   ```

---

## 📱 **Als PWA auf Smartphone installieren**

1. Öffne die App im Browser (Chrome/Safari)
2. Klicke auf "Teilen" / "Menü"
3. Wähle "Zum Home-Bildschirm hinzufügen"
4. **Fertig!** App-Icon auf dem Homescreen

---

## 🆘 **Problemlösung**

### Port 8501 bereits belegt:
```bash
# Ändere den Port in:
.streamlit/config.toml

# Oder starte mit:
streamlit run project_app.py --server.port=8502
```

### Dependencies fehlen:
```bash
pip install -r requirements.txt
```

### Docker Probleme:
```bash
# Container komplett neu bauen
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 📚 **Weitere Infos**

- **Vollständige Deployment-Anleitung**: Siehe `DEPLOYMENT.md`
- **API Dokumentation**: Siehe `docs/API.md`
- **Entwickler-Guide**: Siehe `docs/DEVELOPMENT.md`

---

## 💡 **Tipps**

### Automatischer Start beim Systemstart:

**Windows (Task Scheduler):**
1. Taskplaner öffnen
2. "Einfache Aufgabe erstellen"
3. Trigger: "Beim Anmelden"
4. Aktion: `start_windows.bat` ausführen

**Mac (LaunchAgent):**
```bash
# Siehe deployment/macos/com.projectmaster.plist
cp deployment/macos/com.projectmaster.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.projectmaster.plist
```

**Linux (systemd):**
```bash
sudo cp deployment/systemd/projectmaster.service /etc/systemd/system/
sudo systemctl enable projectmaster
sudo systemctl start projectmaster
```

---

## 🎉 **Los geht's!**

Wähle eine Methode oben und starte durch! 🚀

Bei Fragen: Siehe `DEPLOYMENT.md` für Details.
