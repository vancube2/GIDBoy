import os

# Load system prompt
SYSTEM_PROMPT = ""
if os.path.exists("system_prompt.txt"):
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()

# Load mode prompts
MODES = {}
MODE_DIR = "modes"

for mode in ["RESEARCH", "OPPORTUNITY", "SIGNAL", "ANALYSIS", "CONTENT", "CAREER", "EXECUTION"]:
    filepath = os.path.join(MODE_DIR, f"{mode.lower()}.txt")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            MODES[mode] = f.read()
    else:
        MODES[mode] = "Respond concisely."