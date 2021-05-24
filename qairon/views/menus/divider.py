from flask_admin.menu import BaseMenu


class DividerMenu(BaseMenu):
    """
        Bootstrap Menu divider item
    """
    def __init__(self, name, class_name=None, icon_type=None, icon_value=None, target=None):
        super(DividerMenu, self).__init__(name, 'divider', icon_type, icon_value, target)

    def get_url(self):
        pass

    def is_visible(self):
        # Return True/False depending on your use-case
        return True