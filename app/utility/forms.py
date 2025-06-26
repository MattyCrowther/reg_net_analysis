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
from wtforms import StringField

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


def save_restore_graph(directory, **kwargs):
    class ModifyTruthGraphForm(FlaskForm):
        class Meta:
            csrf = False

        reset   = SubmitField("Reset")
        rebuild = SubmitField("Rebuild RDF")
        save    = SubmitField("Save")
        restore = SubmitField("Restore")

        filename = StringField(
            "Filename (optional)",
            render_kw={"placeholder": "e.g. backup-2025-06-20"}
        )

    files = []
    if os.path.isdir(directory):
        for c in os.listdir(directory):
            desc = c.split(".")[0]
            files.append((c, desc))

    setattr(ModifyTruthGraphForm, "files", SelectField("Files", choices=files))
    return ModifyTruthGraphForm(**kwargs)
