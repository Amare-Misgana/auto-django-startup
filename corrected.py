
import keyword
import os
import subprocess
import platform


class AutoDjango:
    def __init__(self, project_name):
        self.project_name = project_name
        self.project_dir = os.getcwd()
        self.app_list = []
        self.static_dirs = ["css", "js", "images", "videos"]
        self.register_app = None
        self.base = """<!DOCTYPE html>  
<html>  
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{% block title %}Base{% endblock %}</title>  
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    {% block head %} {% endblock %}  
</head>  
<body>  
    {% block content %}{% endblock %}  
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block script %}{% endblock %}
</body>  
</html>  
"""
    def create_base_html(self):
        with open(os.path.join(self.project_dir, "templates", "base.html"), "w") as base_html:
            base_html.write(self.base)

          
    def edit_file(self, file, target, values, folder, insert_point=None, position="bottom", concatenate=False, insert=False):
        file_path = os.path.join(self.project_dir, folder, file)

        with open(file_path, "r") as file:
            files = file.readlines()

        files_list = []
        if concatenate:
            files_list += files
            files_list += ["\n"]
            files_list += values
        else:
            for line_number, line in enumerate(files):
                if target in line:
                    if insert and insert_point:
                        if insert_point in line:
                            index = line.index(insert_point) + len(insert_point)
                            line = line[:index] + "".join(values) + line[index:]
                            files_list.append(line)
                    else:
                        if position == "top":
                            files_list.extend(f"{value}\n" for value in values)
                            files_list.append(line)
                        elif position == "bottom":
                            files_list.append(line)
                            files_list.extend(f"{value}\n" for value in values)
                        elif position == "left":
                            for value in values:
                                files_list.append(f"{value} {line}")
                        elif position == "right":
                            files_list.append(f"{line.strip()} {' '.join(values)}\n")
                else:
                    files_list.append(line)

        with open(file_path, "w") as file:
            file.writelines(files_list)
    def get_file(self, file, start, end, folder, round_in=False):
        file_path = os.path.join(self.project_dir, folder, file)
        with open(file_path, "r") as f:
            files = f.readlines()
            start_point = None
            end_point = None
            
            for line_number, line in enumerate(files):
                if start in line:
                    start_point = line_number
                if start_point is not None and end.strip() in line.strip():
                    end_point = line_number
                    break
            
            if start_point is not None and end_point is not None:
                target_list = [value.strip() for value in files[start_point:end_point + 1]]
                if round_in:
                    new_list = target_list[1:-1]
                    return new_list
                else:
                    return target_list
            else:
                return f"Couldn't find the start: '{start}' or end: '{end}' in the file."
    def remove_value(self, lists, value_to_remove):
        for remove_value in value_to_remove:
            while remove_value in lists: 
                lists.remove(remove_value)
        return lists

    def run_cmd(self, cmd):
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
    def make_dir(self, type=None, registration_folder=None):
        if type == "static":
            os.makedirs(os.path.join(self.project_dir, type), exist_ok=True)
            for dir in self.static_dirs:
                os.makedirs(os.path.join(self.project_dir, type, dir), exist_ok=True)
            for app in self.app_list:
                for dir in self.static_dirs:
                    os.makedirs(os.path.join(self.project_dir, app, type, app, dir), exist_ok=True)

        elif type == "templates":
            os.makedirs(os.path.join(self.project_dir, type, "fragments"), exist_ok=True)
            for app in self.app_list:
                os.makedirs(os.path.join(self.project_dir, app, type, app), exist_ok=True)
        elif type == "registration":
            if registration_folder:
                os.makedirs(os.path.join(self.project_dir, registration_folder, "templates", "registration"))
            else:
                os.makedirs(os.path.join(self.project_dir, "registration"))
        elif type == "media":
            os.makedirs(os.path.join(self.project_dir, type), exist_ok=True)
    def create_file(self, files, values,  is_forapp=False):
        if is_forapp:
            for app in self.app_list:
                for file in files:
                    with open(os.path.join(self.project_dir, f"{file}.py"), "w") as django_file:
                        django_file.write(values.get(file))
        else:
            for file in files:
                with open(os.path.join(self.project_dir, f"{file}.py"), "w") as django_file:
                    django_file.write(values.get(file))
    def settings_add_apps(self, apps=None):
        if apps is None:
            apps = self.app_list
        for app in apps:
            self.edit_file(file="settings.py", folder=self.project_name,target="INSTALLED_APPS", values=[f"    '{app}',"])

    def settings_add_static(self):
        app_list = self.app_list
        static = ["\nSTATICFILES_DIRS = [\n","    BASE_DIR / 'static',\n"]
        for app in app_list:
            static.append(f"    BASE_DIR / '{app}' / 'static',\n")
        static.append("]")
        self.edit_file(file="settings.py", folder=self.project_name, target='', values=static, concatenate=True)
    def settings_add_templates(self):
        app_list = self.app_list
        templates = ["\n            BASE_DIR / 'templates',\n"]
        for app in app_list:
            templates.append(f"            BASE_DIR / '{app}' / 'templates',\n")
        self.edit_file(file="settings.py", folder=self.project_name, target="'DIRS': [", values=templates, insert_point="'DIRS': [", insert=True)
    def settings_add_registration(self, login_url, login_redirect_url, logout_redirect_url):
        registration = [f"LOGIN_URL = '{login_url}'\n", f"LOGIN_REDIRECT_URL = '{login_redirect_url}'\n", f"LOGOUT_REDIRECT_URL = '{logout_redirect_url}'"]
        self.edit_file(file="settings.py", folder=self.project_name, target="", values=registration, concatenate=True)
    def settings_add_media(self):
        media = ["MEDIA_URL = '/media-url/'", "\nMEDIA_ROOT = BASE_DIR / 'media'"]
        self.edit_file(file="settings.py", folder=self.project_name, target="", values=media, concatenate=True)
    def edit_settings(self, main=True, registration=False, media=False):
        if main:
            self.settings_add_apps()
            self.settings_add_templates()
            self.settings_add_static()
        if registration:
            self.settings_add_registration(login_url="login/", login_redirect_url="/", logout_redirect_url="/")
        if media:
            self.settings_add_media()
    def edit_main_url(self, main=True, registration=False, media_handling=False):
        app_list = self.app_list
        project_name = self.project_name
        if registration:
            self.edit_file(file="urls.py", target="urlpatterns = [", values=["    path('', include('django.contrib.auth.urls')),"], folder=project_name)
        if media_handling:
            self.edit_file(file="urls.py", target=']', position="right",  folder=project_name, values= [" + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"])
            static_fun = "from django.conf.urls.static import static"
            settings = "from django.conf import settings"
            self.edit_file(file="urls.py", target='from django.urls import path', folder=project_name, values=[static_fun, settings])
        if main:
            self.edit_file(file="urls.py", folder=project_name,target="from django.urls import path", values=[", include"], insert_point="from django.urls import path", insert=True)
            for app in app_list:
                self.edit_file(file="urls.py", target="urlpatterns = [", values=[f"    path('', include('{app}.urls')),"], folder=project_name)
    def app_url(self, values=["from django.urls import path", "\nfrom . import views", "\n\n\n", "urlpatterns = [\n\n]"]):
        for app in self.app_list:
            with open(os.path.join(self.project_dir, app, "urls.py"), "w") as url_file:
                url_file.writelines(values)
    def run_venv(self):
        self.run_cmd(["python", "-m", "venv", "venv"])
        if platform.system() == "Windows":
            subprocess.run(["venv\\Scripts\\activate.bat"], shell=True)
            pip_path = "venv\\Scripts\\pip.exe"
        else:
            subprocess.run(["source", "venv/bin/activate"], shell=True)
            pip_path = "venv/bin/pip"
        download_package = inputs("Do you want to install packages: ", yes, no)
        if download_package:
            while True:
                packages_amount = input("How many packages you want to install: ")
                if packages_amount:
                    if packages_amount.isdigit():
                        packages_amount = int(packages_amount)
                        if packages_amount >= 1:
                            break
                        else:
                            print(f"'{packages_amount}' is less than 1! Please enter a proper value.")
                    else:
                        print(f"'{packages_amount}' isn't a number! Please enter an integer.")
                else:
                    print(f"You can't packages amount empty. Try again.")
            for i in range(int(packages_amount)):
                while True:
                    package = input(f"Enter package{i + 1}: ")
                    try:
                        self.run_cmd([pip_path, "install", package])
                        break
                    except:
                        print("Something is wrong. Please try again.")

# ================ Global variables ===================

extra_apps_value = []
yes = ["y", "Y", "yes", "YES", "yup"]
no = ["n", "N", "no", "No", "nop"]

def inputs(question, expected_value1, expected_value2):
    while True:
        value = input(question)
        if value in expected_value1:
            return True
            break
        elif value in expected_value2:
            return False
            break
        else:
                print(f"'{value}' is an invalid input. Please try again.")
    
def input_keyword_filter(value):
    if not keyword.iskeyword(value):
        return True
    else:
        print(f"'{value}' is a reserved keyword! Please try again.")
        return False
def set_project_name(obj):
    while True:
        project_name = input("Enter the name of your project: ").strip()
        if project_name:
            if input_keyword_filter(project_name):
                obj.project_name = project_name
                break
        else:
            print("You can't Enter an empty Value! Please try again!")
def set_dir(obj):
    while True:
        path = input("Enter a path to your project or press enter for the current folder: ")
        if os.path.exists(os.path.join(path, "manage.py")):
            print(f"{path} already exists. Overlaying a project into an existing directory won't replace conflicting files.")
        else:
            if path == "":
                obj.project_dir = os.getcwd()
                print(f"You have successfully set the path to: {os.getcwd()}.")
                break
            elif os.path.exists(path):
                obj.project_dir = path
                print(f"You have successfully set the path to: {path}.")
                break
            else:
                print(f"{path}: doesn't exist! Please try again!")
    os.chdir(obj.project_dir)
def get_apps_list(obj):
    while True: 
            apps_amount = input("Enter the number of apps you want to have in your project: ")
            if apps_amount:
                if apps_amount.isdigit():
                    apps_amount = int(apps_amount)
                    if apps_amount >= 1:
                        for i in range(apps_amount):
                            while True:
                                app = input(f"Enter app {i + 1}: ")
                                if input_keyword_filter(app):
                                    obj.app_list.append(app)
                                    break
                        break
                    else:
                        print(f"'{apps_amount}' is less than 1! Please enter a proper value.")
                else:
                    print(f"'{apps_amount}' isn't a number! Please enter an integer.")
            else:
                print(f"'{apps_amount}' isn't a number! Please enter an integer.")

def extra_apps(obj):
    while True:
        extra_app = inputs("Do you want to add additional apps: (y/n)", yes, no)
        if extra_app == True:
            break
        elif extra_app == False:
            return
    while True:
        extra_apps_amount = input("Enter the amount of extar apps: ")
        if not extra_apps_amount:
            print("You can't enter an empty value.")
        elif extra_apps_amount.isdigit():
            if int(extra_apps_amount) >= 1:
                break
            else:
                print(f"'{extra_apps_amount}' is less than 1! Please enter a proper value.")
        else:
            print(f"'{extra_apps_amount}' isn't a number! Please enter an integer.")
    for i in range(int(extra_apps_amount)):
        app = input(f"Enter app{i + 1}: ")
        extra_apps_value.append(app)
def set_registration(obj, reslut_regis):
    if reslut_regis:
        while True:
            regis_app = input("Which app do you want to use to create the registration file: ")
            if regis_app: 
                if regis_app in obj.app_list:
                    obj.make_dir("registration", registration_folder=regis_app)
                    break
                else:
                    print(f"ERROR: We can't find {regis_app}!")
            else:
                print(f"ERROR: '{regis_app}' doesn't exits!")
        obj.edit_main_url(main=False, registration=True, media_handling=False)
        obj.edit_settings(main=False, registration=True)
def set_media(obj, result_media):
    if result_media:
        obj.make_dir("media")
        obj.edit_main_url(main=False, registration=False, media_handling=True)
        obj.edit_settings(main=False, media=True)

def set_project(obj):
    # ================ Initialization ================

    set_project_name(obj)
    set_dir(obj)
    get_apps_list(obj)
    extra_apps(obj)
    result_media = inputs("Do you want to have a media in your project. (y/n): ", yes, no)
    reslut_regis = inputs("Do you want to have a registration in your project. (y/n): ", yes, no)
    print("\nCreating Virtual Enviroment...\n")
    # ================ Execution ================
    obj.run_venv()
    obj.run_cmd(["django-admin", "startproject", obj.project_name, "."])
    
    for app in obj.app_list:
        obj.run_cmd(["django-admin", "startapp", app])
    
    obj.make_dir("static")
    obj.make_dir("templates")
    obj.app_url()
    obj.edit_main_url()
    obj.settings_add_apps(extra_apps_value)
    obj.edit_settings()
    obj.create_base_html()
    
    set_registration(obj, reslut_regis)
    set_media(obj, result_media)
    





django = AutoDjango("example")

set_project(django)

