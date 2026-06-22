from roboflow import Roboflow

try:
    rf = Roboflow(api_key="TY1Yt0QRbvzQtd9lydtI")
    workspace = rf.workspace("kumkums-workspace-wfgjm")
    project = workspace.project("vision-bin-127wk")
    print(f"\n[MONITOR] Project Image Count: {project.images}")
except Exception as e:
    print(f"[MONITOR] Error: {e}")
