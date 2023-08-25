import os
import pytest
import shutil
import tempfile
import yaml
from src.hooks.wrappers.renderer import RenderEngine

@pytest.fixture
def render_engine():
    path = os.path.join(os.getcwd(), "src", "api", "manifests")
    kustomization_path = os.path.join(os.getcwd(), "tests", "data", "kustomization.yaml")
    service_name = "my-service"
    return RenderEngine(path, kustomization_path, service_name)

def test_retrieve_files_to_render(render_engine):
    files_to_render = render_engine._RenderEngine__retrieve_files_to_render()
    assert len(files_to_render) == 6
    assert "/workspaces/azd-python-p1-service-template/src/api/manifests/namespace.yaml.tmpl" \
        in files_to_render
    assert "/workspaces/azd-python-p1-service-template/src/api/manifests/repository.yaml.tmpl" \
        in files_to_render

def test_add_service_to_kustomization_resources(render_engine):
    with tempfile.TemporaryDirectory() as test_dir:
        # Copy file kustomization_path to test_dir
        test_kustomization_path = shutil.copy(render_engine.kustomization_path, test_dir)
        client = RenderEngine(test_dir, test_kustomization_path, \
            render_engine.service_name)
        client._RenderEngine__add_service_to_kustomization_resources()

        with open(test_kustomization_path, "r", encoding="utf-8") as r_stream:
            yaml_dict = yaml.safe_load(r_stream)
            assert f"./services/{render_engine.service_name}" in yaml_dict["resources"]

def test_render(render_engine):
    def ignore_func(_, files):
        return [f for f in files if f[-5:] != '.tmpl']

    with tempfile.TemporaryDirectory() as test_dir:
        shutil.copytree(render_engine.path, test_dir, ignore=ignore_func, dirs_exist_ok=True)

        client = RenderEngine(test_dir, os.path.join(test_dir, "kustomization.yaml"), \
            render_engine.service_name)
        test_image_name = "testimage:latest"
        os.environ["SERVICE_NAME"] = render_engine.service_name
        os.environ["SERVICE_API_IMAGE_NAME"] = test_image_name
        client.render()
        test_file = f"{test_dir}/values.yaml"
        assert os.path.exists(test_file)

        with open(test_file, "r", encoding="utf-8") as r_stream:
            yaml_dict = yaml.safe_load(r_stream)
            assert yaml_dict["image"]["repository"] == test_image_name
