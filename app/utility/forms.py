import os
import json
import re
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms import FileField
from wtforms import validators
from wtforms import FormField
from wtforms.form import BaseForm
from wtforms import PasswordField
from wtforms import FieldList

class CreateUserForm(FlaskForm):
    class Meta:
        csrf = False
    username = TextAreaField("Username", validators=[validators.InputRequired()])
    password = PasswordField("Password", validators=[validators.InputRequired()])
    submit = SubmitField("Submit")

class CreateAdminForm(FlaskForm):
    class Meta:
        csrf = False
    username = TextAreaField("Username", validators=[validators.InputRequired()])
    password = PasswordField("Password", validators=[validators.InputRequired()])
    submit = SubmitField("Submit")

class RebuildGraph(FlaskForm):
    class Meta:
        csrf = False
    submit = SubmitField('Submit')
    download_data = BooleanField("Re-download Data")
    rebuild_rdf = BooleanField("Rebuild RDF")
