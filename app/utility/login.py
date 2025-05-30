import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, LoginManager
import json
import atexit

admin_type = "ADMIN"
user_type = "USER"

user_info = "user_info.json"

class LoginHandler(LoginManager):
    """
    This class handles login for the app, providing the potential for persistent data.
    It currently checks flags in the sessions directory and can be expanded to 
    implement a more secure login system via databases.
    """
    def __init__(self, server, user_dir):
        """
        Initialize the LoginHandler instance.

        :param server: The Flask application instance.
        :param user_dir: The directory where user information is stored.
        """
        super().__init__(server)
        self.init_app(server)
        self.user_info_dir = os.path.join(user_dir, user_info)
        if not os.path.isfile(self.user_info_dir):
            open(self.user_info_dir, "a")
        with open(self.user_info_dir) as f:
            try:
                self.user_data = json.load(f)
            except json.decoder.JSONDecodeError:
                self.user_data = {}
        self.admin = self.get_admin()
        atexit.register(self._save_users)

    def _save_users(self):
        """
        Save user data to a file upon exiting the application.
        """
        if self.user_data == {}:
            return
        with open(self.user_info_dir, 'w') as outfile:
            json.dump(self.user_data, outfile)

    def add_admin(self, username, password):
        """
        Add an admin user.

        :param username: The admin's username.
        :param password: The admin's password.
        :return: The created admin user.
        """
        password = generate_password_hash(password)
        self.admin = User(username, password, self, is_admin=True)
        self._add_user(self.admin)
        return self.admin

    def add_user(self, username, password):
        """
        Add a regular user.

        :param username: The user's username.
        :param password: The user's password.
        :return: The created user.
        """
        password = generate_password_hash(password)
        user = User(username, password, self)
        self._add_user(user)
        return user

    def remove_user(self, username):
        """
        Remove a user.

        :param username: The username of the user to be removed.
        """
        try:
            del self.user_data[username]
        except KeyError:
            pass

    def get_admin(self):
        """
        Retrieve the admin user.

        :return: The admin user if exists, else None.
        """
        for user, details in self.user_data.items():
            if details["user_type"] == admin_type:
                return self._pair_to_user(user, details)

    def get_user(self, username, password):
        """
        Retrieve a user by username and password.

        :param username: The username.
        :param password: The password.
        :return: The user if credentials are correct, else None.
        """
        if (username == self.admin.username and 
        self.admin.check_password(password)):
            return User(username, password, self, is_admin=True)
        user = User(username, password, self)
        if self.is_user(user):
            return user
        return None

    def does_exist(self, username):
        """
        Check if a user exists.

        :param username: The username to check.
        :return: True if user exists, else False.
        """
        if username == self.admin.username:
            return True
        for user in self.get_users():
            existing_user = user
            if username == existing_user.username:
                return True
        return False

    def get_users(self):
        """
        Retrieve all regular users.

        :return: A list of regular users.
        """
        return [self._pair_to_user(un, det) for un, det in 
                self.user_data.items() if det["user_type"] != admin_type]

    def is_user(self, user):
        """
        Check if a user is a regular user.

        :param user: The user to check.
        :return: True if user is a regular user, else False.
        """
        for eu in self.get_users():
            existing_user = eu
            if existing_user == user:
                return True
        return False

    def _pair_to_user(self, username, details):
        """
        Convert user data pair to User object.

        :param username: The username.
        :param details: The user details.
        :return: The User object.
        """
        if admin_type == details["user_type"]:
            u_type = True
        else:
            u_type = False
        return User(username, details["password"], self, is_admin=u_type)

    def _add_user(self, user):
        """
        Add a user to the user data.

        :param user: The user to be added.
        """
        u_type = admin_type if user.is_admin else user_type
        self.user_data[user.username] = {"user_type": u_type, 
                                         "password": user.password}

class User(UserMixin):
    """
    A class representing a user.
    """
    def __init__(self, username, password, manager, is_admin=False):
        """
        Initialize the User instance.

        :param username: The username.
        :param password: The password.
        :param manager: The LoginHandler instance.
        :param is_admin: Boolean indicating if the user is an admin.
        """
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self._manager = manager

    def __eq__(self, other):
        """
        Check equality with another user.

        :param other: The other user.
        :return: True if users are equal, else False.
        """
        if not isinstance(other, User):
            return False
        if other.username == self.username and self.check_password(other.password):
            return True
        return False

    def get_id(self):
        """
        Get the user's ID.

        :return: The username.
        """
        return self.username

    def set_password(self, password):
        """
        Set the user's password.

        :param password: The new password.
        """
        self.password = password

    def check_password(self, password):
        """
        Check the user's password.

        :param password: The password to check.
        :return: True if password is correct, else False.
        """
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        """
        Check if the user is authenticated.

        :return: True if user is authenticated, else False.
        """
        if self.is_admin:
            return True
        if self._manager.is_user(self):
            return True
        return False
