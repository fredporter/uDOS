LANGUAGE: python
'
' Demo Python uScript
'
print("Hello from Python uScript!")
import json
with open("../vars/env.json") as f:
    env = json.load(f)
print("User:", env["USER"])
