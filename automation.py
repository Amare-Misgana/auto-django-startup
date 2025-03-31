import keyword
import os
import subprocess
import sys


class DjangoAuto:
    def __init__(self, project_name):
        self.project_name = project_name
        self.current_dir = os.getcwd()
        self.app_list = []
        self.static_dirs = ["css", "js", "images", "videos"]

    def create_project(self):
        if os.path.exists(os.path.join(self.current_dir, "manage.py")):
            print(
                "Error: A Django project already exists in this directory. Aborting project creation."
            )
            sys.exit(1)

        subprocess.run(
            ["django-admin", "startproject", self.project_name, "."], check=True
        )

    def make_app_dirs(self, app):
        os.makedirs(os.path.join(self.current_dir, app, "static", app), exist_ok=True)
        os.makedirs(
            os.path.join(self.current_dir, app, "templates", app), exist_ok=True
        )
        for dir in self.static_dirs:
            os.makedirs(
                os.path.join(self.current_dir, app, "static", app, dir), exist_ok=True
            )

    def make_dirs(self):
        os.makedirs(
            os.path.join(self.current_dir, "templates", "fragments", "header.html"),
            exist_ok=True,
        )
        for dir in self.static_dirs:
            os.makedirs(os.path.join(self.current_dir, "static", dir), exist_ok=True)
        base_html_path = os.path.join(self.current_dir, "templates", "base.html")
        with open(base_html_path, "w") as base_html:
            base_html.write(
                """<!DOCTYPE html>  
<html>  
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{% block title %}Base{% endblock %}</title>  
    {% block head %} {% endblock %}  
</head>  
<body>  
    {% block content %}{% endblock %}  
</body>  
</html>  
"""
            )

    def modify_app_file(self):
        for app in self.app_list:
            urls_path = os.path.join(self.current_dir, app, "urls.py")
            with open(urls_path, "w") as url_file:
                url_file.writelines(
                    f"""
from django.urls import path
from . import views

urlpatterns = [
    path("{app}/", views.{app}, name="{app}_url"),
    ]
                    """
                )
            views_path = os.path.join(self.current_dir, app, "views.py")
            with open(views_path, "r+") as views_file:
                view_list = views_file.readlines()
                appended_list = [
                    f"""
def {app}(request):
    return render(request, '{app}/{app}.html')
"""
                ]
                view_list += appended_list
                views_file.seek(0)
                views_file.writelines(view_list)

    def create_app(self):
        for app in self.app_list:
            subprocess.run(["django-admin", "startapp", app])
        for app in self.app_list:
            self.make_app_dirs(app)

    def edit_main_url(self):
        with open(
            os.path.join(self.current_dir, self.project_name, "urls.py"), "r+"
        ) as main_url:
            main_url_list = main_url.readlines()

            new_urlpatterns = [
                "",
                "urlpatterns = [\n",
                "    path('admin/', admin.site.urls),\n",
            ]
            for line_number, line in enumerate(main_url_list):
                if line.strip() == "from django.urls import path":
                    main_url_list[line_number] = (
                        "from django.urls import path, include\n"
                    )
                if "urlpatterns" in line:

                    main_url_list[line_number:] = new_urlpatterns
                    break
            for app in self.app_list:
                new_urlpatterns.append(f"    path('{app}/', include('{app}.urls')),\n")
            new_urlpatterns.append("]\n")

            main_url.seek(0)
            main_url.truncate()
            main_url.writelines(main_url_list)

    def edit_settings(self):
        templates_dirs = ["         'DIRS': [\n         BASE_DIR / 'templates',\n"]
        for app in self.app_list:
            templates_dirs.append(
                f"                BASE_DIR / '{app}' / 'templates',\n"
            )
        templates_dirs.append("             ],\n")

        static_dirs = ["STATICFILES_DIRS = [\n    BASE_DIR / 'static',\n"]
        for app in self.app_list:
            static_dirs.append(f"    BASE_DIR / '{app}' / 'static',\n")
        static_dirs.append("]\n")

        with open(
            os.path.join(self.current_dir, self.project_name, "settings.py"), "r+"
        ) as settings_file:
            settings = settings_file.readlines()

            for line_number, line in enumerate(settings):
                if "INSTALLED_APPS" in line:
                    line_number += 1
                    for app in self.app_list:
                        settings.insert(line_number, f"    '{app}',\n")
                        line_number += 1
                elif "'DIRS': []" in line:
                    del settings[line_number]
                    settings.insert(line_number, "".join(templates_dirs))

            settings += static_dirs
            settings_file.seek(0)
            settings_file.truncate()
            settings_file.writelines(settings)

    def excution(self):
        self.create_project()
        self.create_app()
        self.make_dirs()
        self.modify_app_file()
        self.edit_settings()
        self.edit_main_url()


def get_integer_input(prompt):
    while True:
        user_input = input(prompt)
        try:
            value = int(user_input)
            return value
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def change_directory():
    while True:
        path = input("Please enter the directory path: ").strip()
        if os.path.isdir(path):
            try:
                os.chdir(path)
                print(f"Successfully changed to directory: {os.getcwd()}")
                break
            except OSError as e:
                print(f"Error: {e}")
        else:
            print("Error: The directory does not exist. Please try again.")


def get_valid_name(prompt):
    while True:
        name = input(prompt).strip()
        if not name.isidentifier():
            print(f"Error: '{name}' is not a valid Python identifier.")
        elif keyword.iskeyword(name):
            print(f"Error: '{name}' is a reserved keyword in Python.")
        else:
            return name


def main():
    change_directory()

    project_name = get_valid_name("Enter your Django project name: ")

    app_amount = get_integer_input("Enter the number of apps you want to create: ")
    django_project = DjangoAuto(project_name)

    for i in range(app_amount):
        app_name = get_valid_name(f"Enter app name {i + 1}: ")
        django_project.app_list.append(app_name)

    django_project.excution()


if __name__ == "__main__":
    main()
