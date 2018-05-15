"""
This class handle door controller life cycle.
"""
import requests
import json

class AccessManager:
	
	def __init__(self, secret):
		self.secret = secret
	
	def __str__(self):
		""" Prints out user-friendly string description """
		return "AccessManager : Secret : " str(self.secret) 	 
		
	def validateCredential(self, credential):
		""" Validate credentials """
		
