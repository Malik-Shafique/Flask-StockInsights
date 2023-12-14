# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 10:33:00 2020

@author: malik
"""

from flask_wtf import Form
from wtforms import TextField, SubmitField
from wtforms import validators, ValidationError


class ContactForm(Form):
  scripname = TextField("Scrip Name",[validators.Required("Please enter scrip name.")])
  password = TextField("Password:&nbsp&nbsp",[validators.Required("Please enter your Password.")])
  submit = SubmitField("Send")
  