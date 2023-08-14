import os
import subprocess

class RenderEngine:
    def __init__(self, path):
        self.path = path
        self.remove_template_file = True

    def __retrieve_files_to_render(self):
        files_to_render = []
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".tmpl"):
                    files_to_render.append(os.path.join(root, file))
        return files_to_render

    def render(self):
        files_to_render = self.__retrieve_files_to_render()
        for file in files_to_render:
            print(f"Rendering {file}")
            self.__run_command(f"envsubst < {file} > {file[:-5]}")

            if self.remove_template_file:
                os.remove(file)

    def __run_command(self, command):
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, \
                                             universal_newlines=True, shell=True)
            return output.strip()
        except subprocess.CalledProcessError as ex:
            print(f"Error: {ex.output}")
            return None
