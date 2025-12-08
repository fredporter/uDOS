# uDOS v1.0.31 - Grid System

class Grid:
    """
    Manages a dictionary of text-based "panels" for uDOS.
    """
    def __init__(self):
        self.panels = {"main": ""}
        self.selected_panel = "main"

    def add_panel(self, name, content=""):
        """
        Creates a new panel with optional initial content.
        """
        if name in self.panels:
            return f"❌ ERROR: Panel '{name}' already exists."
        self.panels[name] = content
        return f"✅ SUCCESS: Panel '{name}' created."

    def create_panel(self, name):
        """
        Creates a new, empty panel (alias for add_panel).
        """
        return self.add_panel(name, "")

    def remove_panel(self, name):
        """
        Removes a panel.
        """
        if name == "main":
            return False  # Cannot remove main panel
        if name in self.panels:
            del self.panels[name]
            return True
        return False

    def select_panel(self, name):
        """
        Selects a panel as the active one.
        """
        if name in self.panels:
            self.selected_panel = name
            return True
        return False

    def get_panel(self, name):
        """
        Retrieves the content of a specific panel.
        """
        return self.panels.get(name)

    def get_panel_content(self, name):
        """
        Retrieves the content of a specific panel (alias).
        """
        return self.panels.get(name)

    def set_panel_content(self, name, content):
        """
        Sets the content of a specific panel.
        """
        if name not in self.panels:
            return f"❌ ERROR: Panel '{name}' not found."
        self.panels[name] = content
        return f"✅ SUCCESS: Content set for panel '{name}'."

    def get_panel_names(self):
        """
        Lists all available panel names.
        """
        return list(self.panels.keys())

    def list_panels(self):
        """
        Lists all available panels (alias).
        """
        return list(self.panels.keys())

    def __str__(self):
        """
        String representation of the grid for DISPLAY command.
        """
        result = "=== Grid Status ===\n"
        for name, content in self.panels.items():
            marker = " [SELECTED]" if name == self.selected_panel else ""
            result += f"\nPanel: {name}{marker}\n"
            result += f"Content: {content[:100]}{'...' if len(content) > 100 else ''}\n"
        return result
