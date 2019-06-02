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
        return hashlib.sha256(os.urandom(60)).hexdigest()
    
    def _hash_password(self, password):
        """Hash a password for storing."""
        salt = self._get_salt().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def create_user(self, username=None, password=None, **extra_fields):
        return self._create_user(username, password, **extra_fields)


class StationManager(models.Manager):    
    def _create_station(self, name, central, data_token):

        station = self.model(name=name, central=central, data_token=data_token)
        station.save(using=self._db)

        return station

    def create_station(self, name, central, data_token):
        return self._create_station(name, central, data_token)

class CentralManager(models.Manager):    
    def _create_central(self, user, mac_address, **extra_fields):
        central = self.model(owner=user, mac_address=mac_address, automatic_irrigation=False)
        central.save(using=self._db)

        return central

    def create_central(self, user, mac_address):
        return self._create_central(user, mac_address)

class ActuatorManager(models.Manager):
    def _create_actuator(self, name, central, data_token, **extra_fields):

        actuator = self.model(name=name, central=central, data_token=data_token, status=False)
        actuator.save(using=self._db)

        return actuator

    def create_actuator(self, name, central, data_token):
        return self._create_actuator(name, central, data_token)

def verify_password(user=None, provided_password=None):
    """Verify a stored password against one provided by user"""
    if user is None or provided_password is None:
        return False

    salt = user.hash[:64]
    stored_password = user.hash[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
