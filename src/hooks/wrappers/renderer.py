import os
import subprocess
import yaml

class RenderEngine:
    def __init__(self, path, kustomization_path, service_name):
        self.path = path
        self.service_name = service_name
        self.kustomization_path = kustomization_path
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

        self.__add_service_to_kustomization_resources()

    def __run_command(self, command):
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, \
                                             universal_newlines=True, shell=True)
            return output.strip()
        except subprocess.CalledProcessError as ex:
            print(f"Error: {ex.output}")
            return None

    def __add_service_to_kustomization_resources(self):
        # verify that the kustomization file exists
        if not os.path.exists(self.kustomization_path):
            raise ValueError(
                f"The kustomization file {self.kustomization_path} does not exist."
            )

        print(f"Adding {self.service_name} to {self.kustomization_path}")

        with open(self.kustomization_path, "r", encoding="utf-8") as r_stream:
            yaml_dict = yaml.safe_load(r_stream)
            # check if the resources key exists

            if "resources" not in yaml_dict:
                raise ValueError("No resources found in kustomization yaml file.")

            yaml_dict["resources"].append(f"./services/{self.service_name}")
            # Write the updated yaml to the kustomization file\
            with open(self.kustomization_path, "w", encoding="utf-8") as w_stream:
                yaml.safe_dump(yaml_dict, w_stream, default_flow_style=False, sort_keys=False)

    def __run_command(self, command):
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, \
                                             universal_newlines=True, shell=True)
            return output.strip()
        except subprocess.CalledProcessError as ex:
            print(f"Error: {ex.output}")
            return None
