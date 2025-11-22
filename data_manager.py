import json
import os
import uuid
from datetime import datetime

class ProjectManager:
    FILE_PATH = "projects_data.json"
    USERS_PATH = "users_data.json"
    EXP_PATH = "experiments_data.json"

    def __init__(self):
        self.projects = self.load_data()
        self.users = self.load_users()
        self.experiments = self.load_experiments()

    # --- BASE LOADERS ---
    def load_json(self, path, default=[]):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f: json.dump(default, f)
            return default
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except: return default

    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=4, ensure_ascii=False)

    def load_users(self):
        return self.load_json(self.USERS_PATH, [{"username": "admin", "password": "123", "role": "Admin", "name": "Administrator"}])
    
    def save_users(self): self.save_json(self.USERS_PATH, self.users)
    def add_user(self, u, p, r, n):
        if any(x['username']==u for x in self.users): return False
        self.users.append({"username":u, "password":p, "role":r, "name":n}); self.save_users(); return True

    # --- PROJECTS ---
    def load_data(self):
        data = self.load_json(self.FILE_PATH)
        for p in data:
            # Ensure fields exist (Legacy support)
            for key in ["images", "risks", "team", "activity_log", "tags", "documents", "decisions", "bugs", "stakeholders", "meetings", "secrets", "okrs", "retros", "wiki_pages", "backlog", "test_cases", "test_runs", "automations"]:
                if key not in p: p[key] = []
            if "budget" not in p: p["budget"] = {"total": 0.0, "currency": "EUR", "expenses": []}
            if "swot" not in p: p["swot"] = {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}
            if "tasks" not in p: p["tasks"] = []
            
            # Deep check tasks
            clean_tasks = []
            for t in p.get("tasks", []):
                if "id" not in t: t["id"] = str(uuid.uuid4())
                if "status" not in t: t["status"] = "Done" if t.get("done") else "To Do"
                if "comments" not in t: t["comments"] = []
                clean_tasks.append(t)
            p["tasks"] = clean_tasks
        return data

    def save_data(self): self.save_json(self.FILE_PATH, self.projects)

    def log_activity(self, pid, action, user="System"):
        p = self.get_project(pid)
        if p:
            p["activity_log"].insert(0, {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": action, "user": user, "project_title": p['title']})
            self.save_data()

    def calculate_health(self, pid):
        return "Gesund", "green" # Simplified logic

    # --- EXPERIMENTS (NEXT LEVEL) ---
    def load_experiments(self):
        data = self.load_json(self.EXP_PATH)
        for e in data:
            # Wichtig: Default Werte setzen, falls Schlüssel fehlen (Fix für KeyError)
            if "matrix_data" not in e: e["matrix_data"] = [] 
            if "matrix_columns" not in e: e["matrix_columns"] = ["Messwert 1"] 
            if "samples" not in e: e["samples"] = [] 
            if "images" not in e: e["images"] = [] 
            if "result_summary" not in e: e["result_summary"] = ""
            if "conclusion" not in e: e["conclusion"] = "Offen"
            if "category" not in e: e["category"] = "Sonstiges"
            if "tester" not in e: e["tester"] = "Unbekannt"
            if "status" not in e: e["status"] = "Geplant"
        return data

    def save_experiments(self): self.save_json(self.EXP_PATH, self.experiments)

    def add_experiment(self, name, description, category, tester, project_id=None):
        exp = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "category": category, 
            "tester": tester,
            "project_id": project_id,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "status": "Geplant",
            "samples": [],
            "matrix_columns": ["Ergebnis"],
            "matrix_data": [],
            "images": [],
            "result_summary": "",
            "conclusion": "Offen"
        }
        self.experiments.append(exp)
        self.save_experiments()
        return exp["id"]

    def update_experiment_matrix(self, exp_id, samples, columns, data):
        for e in self.experiments:
            if e["id"] == exp_id:
                e["samples"] = samples
                e["matrix_columns"] = columns
                e["matrix_data"] = data
                e["status"] = "Laufend"
                self.save_experiments()
                return

    def update_experiment_meta(self, exp_id, summary, conclusion, status):
        for e in self.experiments:
            if e["id"] == exp_id:
                e["result_summary"] = summary
                e["conclusion"] = conclusion
                e["status"] = status
                self.save_experiments()
                return

    def add_experiment_image(self, exp_id, path, caption=""):
        for e in self.experiments:
            if e["id"] == exp_id:
                e["images"].append({"path": path, "caption": caption})
                self.save_experiments()
                return

    def delete_experiment_image(self, exp_id, idx):
        for e in self.experiments:
            if e["id"] == exp_id:
                del e["images"][idx]
                self.save_experiments()
                return

    def get_experiment(self, exp_id):
        return next((e for e in self.experiments if e["id"] == exp_id), None)
    
    def delete_experiment(self, exp_id):
        self.experiments = [e for e in self.experiments if e["id"] != exp_id]
        self.save_experiments()

    # --- PROJECT CRUD ---
    def get_project(self, pid): return next((p for p in self.projects if p["id"] == pid), None)
    def add_project(self, t, d, c, p, dl, g="", tg=[], it=False):
        np = {"id": str(uuid.uuid4()), "title": t, "description": d, "category": c, "priority": p, "deadline": dl, "status": "Idee", "progress": 0, "images": [], "git_url": g, "tags": tg, "is_template": it, "created_at": datetime.now().strftime("%Y-%m-%d"), "activity_log": [], "tasks":[], "budget":{"total":0,"expenses":[]}, "team":[], "risks":[], "test_cases":[], "is_deleted":False}
        self.projects.append(np); self.save_data(); return np["id"]
    def update_project(self, pid, ud): 
        for p in self.projects: 
            if p["id"]==pid: p.update(ud); self.save_data(); return True
    def soft_delete_project(self, pid): self.update_project(pid, {"is_deleted": True})
    def restore_project(self, pid): self.update_project(pid, {"is_deleted": False})
    def delete_project_permanent(self, pid): self.projects=[p for p in self.projects if p['id']!=pid]; self.save_data()
    def duplicate_project(self, tid, nt):
        t=self.get_project(tid); 
        if t: nid=self.add_project(nt, t['description'], t['category'], t['priority'], None, tags=t['tags']); return nid

    # --- Wrappers ---
    def _add_item(self, pid, k, i, m=""): p=self.get_project(pid); p[k].append(i); self.save_data()
    def _del_item(self, pid, k, i): p=self.get_project(pid); del p[k][i]; self.save_data()
    def add_task(self, pid, t, blocked_by=None, assignee=None): self._add_item(pid, "tasks", {"id":str(uuid.uuid4()), "text":t, "status":"To Do", "assignee":assignee, "comments":[]})
    def update_task_status(self, pid, tid, s): 
        p=self.get_project(pid); 
        for t in p['tasks']: 
            if t['id']==tid: t['status']=s; self.save_data(); return
    def delete_task_by_id(self, pid, tid): p=self.get_project(pid); p['tasks']=[t for t in p['tasks'] if t['id']!=tid]; self.save_data()
    def add_task_comment(self, pid, tid, c): 
        p=self.get_project(pid); 
        for t in p['tasks']: 
            if t['id']==tid: t['comments'].append({"text":c, "date":datetime.now().strftime("%Y-%m-%d")}); self.save_data(); return
    
    # Legacy
    def add_image(self, pid, p): self._add_item(pid, "images", p)
    def delete_image(self, pid, i): self._del_item(pid, "images", i)
    def delete_all_images(self, pid): p=self.get_project(pid); p['images']=[]; self.save_data()
    def add_document(self, pid, n, p): self._add_item(pid, "documents", {"name":n, "path":p})
    def delete_document(self, pid, i): self._del_item(pid, "documents", i)
    def set_budget_total(self, pid, v): self.get_project(pid)['budget']['total']=v; self.save_data()
    def add_expense(self, pid, t, a, c): self.get_project(pid)['budget']['expenses'].append({"title":t,"amount":a,"category":c}); self.save_data()
    def delete_expense(self, pid, i): self._del_item(pid["budget"]["expenses"], i)
    def add_risk(self, pid, d, p, i): self._add_item(pid, "risks", {"desc":d,"prob":p,"impact":i})
    def delete_risk(self, pid, i): self._del_item(pid, "risks", i)
    def add_team_member(self, pid, n, r): self._add_item(pid, "team", {"name":n,"role":r})
    def delete_team_member(self, pid, i): self._del_item(pid, "team", i)
    def add_milestone(self, pid, t, d): self._add_item(pid, "milestones", {"title":t,"date":d,"done":False})
    def toggle_milestone(self, pid, i): p=self.get_project(pid); p["milestones"][i]["done"]=not p["milestones"][i]["done"]; self.save_data()
    def delete_milestone(self, pid, i): self._del_item(pid, "milestones", i)
    def add_time_log(self, pid, d, c, h, de): self._add_item(pid, "time_logs", {"date":d,"category":c,"hours":h,"desc":de})
    
    # Extended
    def add_decision(self, p, t, s, r): self._add_item(p, "decisions", {"title":t,"status":s,"rationale":r})
    def delete_decision(self, p, i): self._del_item(p, "decisions", i)
    def add_bug(self, p, t, s): self._add_item(p, "bugs", {"title":t,"severity":s,"status":"Open"})
    def toggle_bug(self, p, i): pr=self.get_project(p); pr["bugs"][i]["status"]="Fixed" if pr["bugs"][i]["status"]=="Open" else "Open"; self.save_data()
    def delete_bug(self, p, i): self._del_item(p, "bugs", i)
    def add_stakeholder(self, p, n, o, i): self._add_item(p, "stakeholders", {"name":n,"org":o,"influence":i})
    def delete_stakeholder(self, p, i): self._del_item(p, "stakeholders", i)
    def add_meeting(self, p, d, t, s): self._add_item(p, "meetings", {"date":d,"title":t,"summary":s})
    def delete_meeting(self, p, i): self._del_item(p, "meetings", i)
    def add_secret(self, p, k, v): self._add_item(p, "secrets", {"key":k,"value":v})
    def delete_secret(self, p, i): self._del_item(p, "secrets", i)
    def add_swot(self, p, c, t): self.get_project(p)["swot"][c].append(t); self.save_data()
    def delete_swot(self, p, c, i): del self.get_project(p)["swot"][c][i]; self.save_data()
    def add_okr(self, p, o): self._add_item(p, "okrs", {"id":str(uuid.uuid4()),"objective":o,"key_results":[]})
    def delete_okr(self, p, i): self._del_item(p, "okrs", i)
    def add_key_result(self, p, oid, t, pr): proj=self.get_project(p); next(o for o in proj["okrs"] if o["id"]==oid)["key_results"].append({"title":t,"progress":pr}); self.save_data()
    def add_retro(self, p, c, t): self._add_item(p, "retros", {"category":c,"text":t})
    def delete_retro(self, p, i): self._del_item(p, "retros", i)
    def add_wiki_page(self, p, t, c): self._add_item(p, "wiki_pages", {"title":t,"content":c})
    def update_wiki_page(self, p, i, t, c): pr=self.get_project(p); pr["wiki_pages"][i]={"title":t,"content":c}; self.save_data()
    def delete_wiki_page(self, p, i): self._del_item(p, "wiki_pages", i)
    def add_backlog_item(self, p, t, pr, n): self._add_item(p, "backlog", {"title":t,"priority":pr})
    def delete_backlog_item(self, p, i): self._del_item(p, "backlog", i)
    def add_test_case(self, p, t, s, e): self._add_item(p, "test_cases", {"id":str(uuid.uuid4()),"title":t,"steps":s,"expected":e,"status":"Untested"})
    def update_test_status(self, p, tid, s): proj=self.get_project(p); next(t for t in proj["test_cases"] if t["id"]==tid)["status"]=s; self.save_data()
    def delete_test_case(self, p, i): self._del_item(p, "test_cases", i)
    def add_automation(self, p, t, a): self._add_item(p, "automations", {"trigger":t,"action":a})
    def delete_automation(self, p, i): self._del_item(p, "automations", i)