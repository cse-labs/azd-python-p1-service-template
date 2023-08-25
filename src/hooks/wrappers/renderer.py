import os
import subprocess

import yaml


class RenderEngine:
    """
    The RenderEngine class provides functionality to render K8 templates
    and add a service to a kustomization file.
    """

    def __init__(self, path, kustomization_path, service_name):
        """
        Initializes a new instance of the RenderEngine class.

        Args:
            path (str): The path to the directory containing the templates to render.
            kustomization_path (str): The path to the kustomization file.
            service_name (str): The name of the service to add to the kustomization file.
        """
        self.path = path
        self.service_name = service_name
        self.kustomization_path = kustomization_path
        self.remove_template_file = True

    def __retrieve_files_to_render(self):
        """
        Retrieves a list of files to render.

        Returns:
            A list of files to render.
        """
        files_to_render = []
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".tmpl"):
                    files_to_render.append(os.path.join(root, file))
        return files_to_render

    def render(self):
        """
        Renders the templates and adds the service to the kustomization file.
        """
        files_to_render = self.__retrieve_files_to_render()
        for file in files_to_render:
            print(f"Rendering {file}")
            self.__run_command(f"envsubst < {file} > {file[:-5]}")

            if self.remove_template_file:
                os.remove(file)

        self.__add_service_to_kustomization_resources()

    def __run_command(self, command):
        """
        Runs a shell command.

        Args:
            command (str): The command to run.

        Returns:
            The output of the command.
        """
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
            return output.strip()
        except subprocess.CalledProcessError as ex:
            print(f"Error: {ex.output}")
            return None

    def __add_service_to_kustomization_resources(self):
        """
        Adds the service to the kustomization file.
        """
        # verify that the kustomization file exists
        if not os.path.exists(self.kustomization_path):
            raise ValueError(f"The kustomization file {self.kustomization_path} does not exist.")

        with open(self.kustomization_path, encoding="utf-8") as r_stream:
            yaml_dict = yaml.safe_load(r_stream)
            # check if the resources key exists

            if "resources" not in yaml_dict:
                raise ValueError("No resources found in kustomization yaml file.")

            # Check if the service already exists in the resources
            if f"./services/{self.service_name}" not in yaml_dict["resources"]:
                yaml_dict["resources"].append(f"./services/{self.service_name}")
                # Write the updated yaml to the kustomization file\
                with open(self.kustomization_path, "w", encoding="utf-8") as w_stream:
                    print(f"Adding {self.service_name} to {self.kustomization_path}")
                    yaml.safe_dump(yaml_dict, w_stream, default_flow_style=False, sort_keys=False)

    def __run_command(self, command):
        """
        Runs a shell command.

        Args:
            command (str): The command to run.

        Returns:
            The output of the command.
        """
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
            return output.strip()
        except subprocess.CalledProcessError as ex:
            print(f"Error: {ex.output}")
            return None
