from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields import BooleanField, HiddenField, StringField
from wtforms.widgets import HiddenInput
from trackman.forms import BootstrapTextInput, strip_field


class BulkEditForm(FlaskForm):
    edit_from = HiddenField("Edit From")
    submit = BooleanField(
        "Form Submitted",
        validators=[validators.DataRequired()],
        widget=HiddenInput(),
    )
    artist = StringField(
        "Artist",
        filters=[strip_field],
        validators=[validators.Optional()],
        widget=BootstrapTextInput(),
    )
    title = StringField(
        "Title",
        filters=[strip_field],
        validators=[validators.Optional()],
        widget=BootstrapTextInput(),
    )
    album = StringField(
        "Album",
        filters=[strip_field],
        validators=[validators.Optional()],
        widget=BootstrapTextInput(),
    )
    label = StringField(
        "Label",
        filters=[strip_field],
        validators=[validators.Optional()],
        widget=BootstrapTextInput(),
    )
    artist_mbid = StringField(
        "Artist MBID",
        filters=[strip_field],
        validators=[validators.Optional(), validators.UUID()],
        widget=BootstrapTextInput(),
    )
    recording_mbid = StringField(
        "Recording MBID",
        filters=[strip_field],
        validators=[validators.Optional(), validators.UUID()],
        widget=BootstrapTextInput(),
    )
    release_mbid = StringField(
        "Release MBID",
        filters=[strip_field],
        validators=[validators.Optional(), validators.UUID()],
        widget=BootstrapTextInput(),
    )
    releasegroup_mbid = StringField(
        "Release Group MBID",
        filters=[strip_field],
        validators=[validators.Optional(), validators.UUID()],
        widget=BootstrapTextInput(),
    )
