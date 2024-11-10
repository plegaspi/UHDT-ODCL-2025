from dotenv import load_dotenv
import os
import roboflow


def initialize_roboflow_project(env_key_id=""):
    project_id = os.environ.get(f"{env_key_id}_PROJ_ID" if env_key_id else "PROJ_ID")
    api_key = os.environ.get(f"{env_key_id}_API_KEY" if env_key_id else "API_KEY")
    rf = roboflow.Roboflow(api_key=api_key)
    workspace = rf.workspace()
    project = workspace.project(project_id)
    return project

def upload_to_roboflow(project, batchname, image_path, annotation_path, annotation_labelmap):
    return project.single_upload(
        batch_name = batchname,
        image_path = image_path,
        annotation_path = annotation_path,
        annotation_labelmap = annotation_labelmap
    )


load_dotenv()
env_key_id = ""
project_id = os.environ.get(f"{env_key_id}_PROJ_ID" if env_key_id else "PROJ_ID")
api_key = os.environ.get(f"{env_key_id}_API_KEY" if env_key_id else "API_KEY")
print(api_key)
rf = roboflow.Roboflow(api_key=api_key)
workspace = rf.workspace()
project = workspace.project(project_id)