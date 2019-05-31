from django.db import models
import hashlib, binascii, os

class UserManager(models.Manager):
    
    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username and password.
        """
        hash = self._hash_password(password)
        auth_token = self._get_salt()

        user = self.model(username=username, hash=hash, auth_token=auth_token)

        user.save(using=self._db)

        return user

    def _get_salt(self):
        return hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    
    def _hash_password(self, password):
        """Hash a password for storing."""
        salt = self._get_salt()
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def create_user(self, username=None, password=None, **extra_fields):
        return self._create_user(username, password, **extra_fields)