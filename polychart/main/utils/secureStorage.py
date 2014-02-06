#!/usr/bin/env python

import Padding

from Crypto.Cipher import AES
from base64 import urlsafe_b64encode, urlsafe_b64decode
from django.conf import settings
from os import urandom
from pbkdf2 import PBKDF2

def getEncryptionKey(password, salt):
  assert password
  assert salt

  saltbytes = urlsafe_b64decode(salt.encode('utf-8'))
  hashThing = PBKDF2(password, saltbytes)
  return hashThing.read(32)

DEFAULT_KEY = getEncryptionKey(settings.SECRET_KEY, 'ziIwStZZ')

def encrypt(key, plaintext):
  assert key

  if plaintext == "":
    return ""

  aes = AES.new(key, AES.MODE_CBC, b"Polychart AES IV")
  padded = Padding.appendPadding(plaintext)
  cipherbytes = aes.encrypt(padded)
  return urlsafe_b64encode(cipherbytes)

def decrypt(key, ciphertext):
  assert key

  if ciphertext == "":
    return ""

  aes = AES.new(key, AES.MODE_CBC, b"Polychart AES IV")
  cipherbytes = urlsafe_b64decode(ciphertext.encode('utf-8'))
  padded = aes.decrypt(cipherbytes)
  return Padding.removePadding(padded)

def generateSalt():
  return urlsafe_b64encode(urandom(8))
