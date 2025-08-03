import json
import os

# Define paths and file patterns
manifest_files = ['package.json', 'requirements.txt', 'fxmanifest.lua']

# Load current context from AI_CHECKPOINT.json
with open('.odin/AI_CHECKPOINT.json', 'r') as f:
    checkpoint = json.load(f)
    current_context = checkpoint.get('context', {})

# Detect manifest files
def detect_manifests():
    found_manifests = []
    for root, dirs, files in os.walk('.'):  # Iterate through the repo
        for file in files:
            if file in manifest_files:
                found_manifests.append(os.path.join(root, file))
    return found_manifests

# Infer primary language and framework
def infer_context(manifests):
    context = {
        "language": None,
        "framework": None,
        "architecture": None
    }

    for manifest in manifests:
        if 'package.json' in manifest:
            context['language'] = 'JavaScript'
            context['framework'] = 'Node.js'
        elif 'requirements.txt' in manifest:
            context['language'] = 'Python'
            context['framework'] = 'Flask'  # Example, this should be more intelligent
        elif 'fxmanifest.lua' in manifest:
            context['language'] = 'Lua'
            context['framework'] = 'FiveM'

    # Potentially add logic to determine architecture and hosting targets
    context['architecture'] = 'MVC'  # Example default

    return context

# Check for context drift and update AI_CHECKPOINT.json
def update_checkpoint(new_context):
    changed = False
    for key, value in new_context.items():
        if current_context.get(key) != value:
            current_context[key] = value
            changed = True

    if changed:
        checkpoint['context'] = current_context
        with open('.odin/AI_CHECKPOINT.json', 'w') as f:
            json.dump(checkpoint, f, indent=2)
        trigger_context_guard()

# Trigger ContextGuard (example placeholder)
def trigger_context_guard():
    print("Context drift detected. Triggering ContextGuard review.")

if __name__ == "__main__":
    manifests = detect_manifests()
    new_context = infer_context(manifests)
    update_checkpoint(new_context)

