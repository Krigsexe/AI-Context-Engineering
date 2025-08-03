from .depguard.depguard import DepGuard
from .contextguard.contextguard import ContextGuard

class PluginAPI:
    def __init__(self, config_path, checkpoint_path):
        self.depguard = DepGuard(config_path)
        self.contextguard = ContextGuard(checkpoint_path)

    def run_plugins(self):
        # Example code to run plugin functions
        self.depguard.load_cve_db()
        context_alert = self.contextguard.alert_on_shift()
        return context_alert

