import json
import os

class WorkflowManager:
    def __init__(self, projects_file='projects.json'):
        self.projects_file = projects_file
        self.projects = self.load_projects()

    def load_projects(self):
        if os.path.exists(self.projects_file):
            with open(self.projects_file, 'r') as f:
                return json.load(f)
        return []

    def save_projects(self):
        with open(self.projects_file, 'w') as f:
            json.dump(self.projects, f, indent=4)

    def get_projects(self):
        return self.projects

    def save_project(self, project_data):
        # Check if project exists
        for i, p in enumerate(self.projects):
            if p['name'] == project_data['name']:
                self.projects[i] = project_data
                self.save_projects()
                return True
        
        # If not, add it
        self.projects.append(project_data)
        self.save_projects()
        return True
