from flask_login import current_user

class UsersPolicy:
    def __init__(self, record):
        self.record = record
    
    def assign_role(self):
        return current_user.is_admin()

    def show(self):
        return True

    def delete(self):
        return current_user.is_admin()

    def create(self):
        return current_user.is_admin()

    def edit(self):
        if current_user.is_admin() or current_user.is_moder():
            return True
        else:
            return False