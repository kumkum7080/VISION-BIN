from roboflow import Roboflow

try:
    rf = Roboflow(api_key="TY1Yt0QRbvzQtd9lydtI")
    workspace = rf.workspace("kumkums-workspace-wfgjm")
    projects = workspace.projects()
    print("\n=== ROBOFLOW PROJECTS IN YOUR WORKSPACE ===")
    for project in projects:
        print(f"Project Name: {project}")
    print("===========================================\n")
except Exception as e:
    print(f"Error checking projects: {e}")
