"""
Interactive Menu Mixin for Command Handlers

Provides easy-to-use menu methods for command handlers.
Allows handlers to present users with menus instead of instructions.
"""

from typing import Optional, List, Tuple, Dict, Callable, Any, Union
from core.ui.interactive_menu import InteractiveMenu, MenuItem, MenuBuilder, show_menu, show_confirm


class InteractiveMenuMixin:
    """
    Mixin for command handlers to easily show interactive menus.
    
    Usage in a handler:
        class MyHandler(BaseCommandHandler, InteractiveMenuMixin):
            def handle(self, command, params, grid, parser):
                # Show a simple menu
                choice = self.show_menu(
                    "Choose action",
                    [("Start", "start"), ("Stop", "stop")]
                )
                if choice == "start":
                    return {"status": "success", "message": "Started"}
    """
    
    def show_menu(
        self,
        title: str,
        options: Union[List[Tuple[str, str]], List[Tuple[str, str, str]]],
        allow_cancel: bool = True,
    ) -> Optional[str]:
        """
        Show interactive menu and return selected value.
        
        Args:
            title: Menu title
            options: List of (label, value) or (label, value, help_text) tuples
            allow_cancel: Allow user to cancel
        
        Returns:
            Selected value, or None if cancelled
        
        Example:
            choice = self.show_menu(
                "Action",
                [
                    ("Start Server", "start", "Launch wizard"),
                    ("Stop Server", "stop", "Shutdown"),
                    ("View Logs", "logs", "Recent activity"),
                ]
            )
        """
        # Normalize options format
        items = []
        for opt in options:
            if len(opt) == 2:
                label, value = opt
                help_text = ""
            elif len(opt) == 3:
                label, value, help_text = opt
            else:
                raise ValueError(f"Option must be (label, value) or (label, value, help_text)")
            
            items.append(MenuItem(label=label, value=value, help_text=help_text))
        
        menu = InteractiveMenu(title, items, allow_cancel=allow_cancel)
        return menu.show()
    
    def show_menu_with_actions(
        self,
        title: str,
        items: List[Tuple[str, Callable, str]],
        allow_cancel: bool = True,
    ) -> Optional[str]:
        """
        Show menu with direct action callbacks.
        
        When user selects an option, the action is called immediately.
        
        Args:
            title: Menu title
            items: List of (label, action_callable, help_text) tuples
            allow_cancel: Allow cancel
        
        Returns:
            Label of selected item
        
        Example:
            def start_server():
                print("Starting...")
            
            def stop_server():
                print("Stopping...")
            
            self.show_menu_with_actions(
                "Server Control",
                [
                    ("Start", start_server, "Launch"),
                    ("Stop", stop_server, "Shutdown"),
                ]
            )
        """
        menu_items = [
            MenuItem(label=label, action=action, help_text=help_text)
            for label, action, help_text in items
        ]
        menu = InteractiveMenu(title, menu_items, allow_cancel=allow_cancel)
        return menu.show()
    
    def show_confirm(self, title: str, help_text: str = "") -> bool:
        """
        Show yes/no confirmation.
        
        Args:
            title: Question text
            help_text: Optional help text
        
        Returns:
            True if user chose Yes
        
        Example:
            if self.show_confirm("Delete all files?", "This cannot be undone"):
                # Delete files
                pass
        """
        return show_confirm(title, help_text)
    
    def show_builder_menu(self, builder: MenuBuilder) -> Optional[str]:
        """
        Show menu built with MenuBuilder.
        
        Args:
            builder: MenuBuilder instance
        
        Returns:
            Selected value or None
        
        Example:
            menu = (MenuBuilder("Actions")
                .add_item("Start", "start", "Launch server")
                .add_item("Stop", "stop", "Shutdown")
                .build()
            )
            result = self.show_builder_menu(menu_builder)
        """
        menu = builder.build()
        return menu.show()
    
    def show_multiselect(
        self,
        title: str,
        options: List[Tuple[str, str]],
    ) -> List[str]:
        """
        Show multi-select menu (user chooses multiple items).
        
        Args:
            title: Menu title
            options: List of (label, value) tuples
        
        Returns:
            List of selected values
        
        Note: This is a simplified version. For full multi-select,
        use the InteractiveMenu directly with custom handling.
        """
        # For now, return single selections in a list
        # Full multi-select would require checkbox UI
        result = self.show_menu(title, options, allow_cancel=True)
        return [result] if result else []
