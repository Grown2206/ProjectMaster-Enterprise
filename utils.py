import os
import requests
import pandas as pd
from datetime import datetime
from io import StringIO

IMAGE_DIR = "project_images"
DOC_DIR = "project_docs"

def ensure_directories():
    if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)
    if not os.path.exists(DOC_DIR): os.makedirs(DOC_DIR)

def save_uploaded_image(uploaded_file, project_id):
    ensure_directories()
    if uploaded_file is None: return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_ext = os.path.splitext(uploaded_file.name)[1]
    file_name = f"{project_id}_{timestamp}{file_ext}"
    file_path = os.path.join(IMAGE_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def save_uploaded_doc(uploaded_file, project_id):
    ensure_directories()
    if uploaded_file is None: return None
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    original_name = os.path.splitext(uploaded_file.name)[0]
    file_ext = os.path.splitext(uploaded_file.name)[1]
    safe_name = "".join([c for c in original_name if c.isalnum() or c in (' ', '-', '_')]).strip()
    file_name = f"{project_id}_{timestamp}_{safe_name}{file_ext}"
    file_path = os.path.join(DOC_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def parse_csv_tasks(uploaded_file):
    """
    Liest CSV/Excel für Task-Import.
    Erwartet Spalten: 'Task' und optional 'Status'
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        tasks = []
        if 'Task' in df.columns:
            for _, row in df.iterrows():
                status = row['Status'] if 'Status' in row and row['Status'] in ['To Do', 'In Progress', 'Done'] else 'To Do'
                tasks.append({"text": str(row['Task']), "status": status})
        return tasks
    except Exception as e:
        return []

def fetch_git_readme(repo_url):
    if not repo_url: return None
    targets = []
    if "github.com" in repo_url and "raw.githubusercontent" not in repo_url:
        clean_url = repo_url.replace(".git", "")
        parts = clean_url.split("/")
        if len(parts) >= 5:
            user, repo = parts[3], parts[4]
            targets.append(f"https://raw.githubusercontent.com/{user}/{repo}/main/README.md")
            targets.append(f"https://raw.githubusercontent.com/{user}/{repo}/master/README.md")
    targets.append(repo_url)
    
    for url in targets:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200: return r.text
        except: continue
    return None

def calculate_days_left(deadline_str):
    if not deadline_str: return "∞"
    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        delta = (deadline - datetime.now()).days
        if delta < 0: return "Überfällig"
        return f"{delta} Tage"
    except: return "Invalid Date"

def generate_markdown_report(project):
    md = f"# {project['title']}\nImported via Project Master Enterprise.\n"
    md += project.get('readme_content', '') or project['description']
    return md