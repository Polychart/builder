from django.core.management.base import BaseCommand, CommandError
from getpass import getpass

from polychart.main.views.account import createUser

class Command(BaseCommand):
  def handle(self, *args, **kwargs):
    userParams = {
      'first_name': _prompt('First name: '),
      'last_name': _prompt('Last name: '),
      'username': _prompt('Username: '),
      'password': _prompt('Password: ', maskInput=True),
    }

    createUser(userParams)

def _prompt(msg, maskInput=False):
  while True:
    if maskInput:
      result = getpass(msg)
    else:
      result = raw_input(msg)

    result = result.strip()

    if result:
      return result
