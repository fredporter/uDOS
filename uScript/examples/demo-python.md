LANGUAGE: python
'
' Demo Python uScript
'
import os
import json

# Get the directory of the current script file
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, "../vars/env.json")

with open(env_path) as f:
    env = json.load(f)

print("Hello from Python uScript!")
print("User:", env["USER"])
