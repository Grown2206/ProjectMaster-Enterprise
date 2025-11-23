#!/bin/bash
# ================================================================
# ProjectMaster Enterprise - Mac/Linux Starter
# ================================================================

echo ""
echo " ========================================"
echo "  ProjectMaster Enterprise v2.3"
echo " ========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python 3 ist nicht installiert!"
    echo ""
    echo "Bitte installiere Python 3:"
    echo "  - Mac: brew install python3"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - Fedora: sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}[INFO]${NC} Python Version: $PYTHON_VERSION"

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}[TIPP]${NC} Verwende eine venv für saubere Dependencies:"
    echo "       python3 -m venv .venv"
    echo "       source .venv/bin/activate"
    echo "       pip install -r requirements.txt"
    echo ""
fi

# Install dependencies if needed
if [ ! -d ".venv/lib/python*/site-packages/streamlit" ] && [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}[INFO]${NC} Installiere Dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Installation fehlgeschlagen!"
        exit 1
    fi
fi

# Create data directories
mkdir -p data uploads project_images project_docs logs

# Ask to create test data
if [ ! -f "data/projects_data.json" ]; then
    echo ""
    echo -e "${GREEN}[INFO]${NC} Keine Projekte gefunden."
    read -p "Möchtest du Testdaten erstellen? (j/n): " CREATE_TEST
    if [ "$CREATE_TEST" = "j" ] || [ "$CREATE_TEST" = "J" ]; then
        echo -e "${GREEN}[INFO]${NC} Erstelle Testdaten..."
        python3 create_test_data.py
    fi
fi

echo ""
echo -e "${GREEN}[INFO]${NC} Starte ProjectMaster Enterprise..."
echo -e "${GREEN}[INFO]${NC} Die App öffnet sich im Browser unter http://localhost:8501"
echo -e "${GREEN}[INFO]${NC} Drücke CTRL+C zum Beenden"
echo ""

# Start Streamlit
streamlit run project_app.py
