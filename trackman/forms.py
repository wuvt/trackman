from flask import current_app
from flask_wtf import FlaskForm
from wtforms import validators, ValidationError
from wtforms.fields import BooleanField, IntegerField, StringField
from wtforms.widgets import Select, TextInput
from .models import DJ
from .view_utils import slugify


class BootstrapWidgetMixin(object):
    def __call__(self, field, **kwargs):
        existing_class = kwargs.pop("class", "") or kwargs.pop("class_", "")
        classes = set(existing_class.split())
        classes.add("form-control")
        if field.errors:
            classes.add("is-invalid")
        kwargs["class"] = " ".join(classes)
        return super().__call__(field, **kwargs)


class BootstrapSelect(BootstrapWidgetMixin, Select):
    pass


class BootstrapTextInput(BootstrapWidgetMixin, TextInput):
    pass


def strip_field(val):
    if isinstance(val, str):
        return val.strip()
    else:
        return val


def slugify_field(val):
    if isinstance(val, str):
        return slugify(val)
    else:
        return val


def artist_validate(form, field):
    if field.data in current_app.config['TRACKMAN_ARTIST_PROHIBITED']:
        raise ValidationError("That artist may not be entered.")


def label_validate(form, field):
    if field.data in current_app.config['TRACKMAN_LABEL_PROHIBITED']:
        raise ValidationError("That label may not be entered.")


class DJRegisterForm(FlaskForm):
    airname = StringField('On-air Name', filters=[strip_field],
                          validators=[validators.Length(min=1, max=255),
                                      validators.DataRequired()])
    name = StringField('Real Name', filters=[strip_field],
                       validators=[validators.Length(min=1, max=255),
                                   validators.DataRequired()])
    email = StringField('Email Address', filters=[strip_field],
                        validators=[validators.Length(min=1, max=255),
                                    validators.Email(),
                                    validators.DataRequired()])
    phone = StringField(
        'Phone Number', filters=[strip_field],
        validators=[validators.Length(min=10, max=12),
                    validators.DataRequired(),
                    validators.Regexp(
                        r'^\d{3}\-\d{3}\-\d{4}$',
                        message="Phone numbers must be of the form "
                                "555-555-5555.")])
    genres = StringField('Genres you can DJ', filters=[strip_field],
                         validators=[validators.Length(min=1, max=255),
                                     validators.DataRequired()])

    def validate_airname(self, field):
        matching = DJ.query.filter(DJ.airname == field.data).count()
        if matching > 0:
            raise ValidationError("Your on-air name must be unique.")


class DJReactivateForm(FlaskForm):
    email = StringField('Email Address', filters=[strip_field],
                        validators=[validators.Length(min=1, max=255),
                                    validators.Email(),
                                    validators.DataRequired()])
    phone = StringField(
        'Phone Number', filters=[strip_field],
        validators=[validators.Length(min=10, max=12),
                    validators.DataRequired(),
                    validators.Regexp(
                        r'^\d{3}\-\d{3}\-\d{4}$',
                        message="Phone numbers must be of the form "
                                "555-555-5555.")])


class DJEditForm(FlaskForm):
    visible = BooleanField('Visible', validators=[validators.Optional()])
    email = StringField('Email Address', filters=[strip_field],
                        validators=[validators.Length(min=1, max=255),
                                    validators.Email(),
                                    validators.Optional()])
    phone = StringField(
        'Phone Number', filters=[strip_field],
        validators=[validators.Length(min=10, max=12),
                    validators.Optional(),
                    validators.Regexp(
                        r'^\d{3}\-\d{3}\-\d{4}$',
                        message="Phone numbers must be of the form "
                                "555-555-5555.")])


class DJAdminEditForm(FlaskForm):
    airname = StringField('On-air Name', filters=[strip_field],
                          validators=[validators.Length(min=1, max=255),
                                      validators.DataRequired()])
    name = StringField('Real Name', filters=[strip_field],
                       validators=[validators.Length(min=1, max=255),
                                   validators.DataRequired()])
    email = StringField('Email Address', filters=[strip_field],
                        validators=[validators.Length(min=1, max=255),
                                    validators.Email(),
                                    validators.Optional()])
    phone = StringField(
        'Phone Number', filters=[strip_field],
        validators=[validators.Length(min=10, max=12),
                    validators.Optional(),
                    validators.Regexp(
                        r'^\d{3}\-\d{3}\-\d{4}$',
                        message="Phone numbers must be of the form "
                                "555-555-5555.")])
    genres = StringField('Genres you can DJ', filters=[strip_field],
                         validators=[validators.Length(min=1, max=255),
                                     validators.Optional()])
    visible = BooleanField('Visible', validators=[validators.Optional()])

    def validate_airname(self, field):
        if self.dj.airname == field.data:
            return

        matching = DJ.query.filter(DJ.airname == field.data).count()
        if matching > 0:
            raise ValidationError("Your on-air name must be unique.")


class DJDeleteClaimForm(FlaskForm):
    claim_id = StringField('Claim ID', validators=[validators.DataRequired()])


class TrackAddForm(FlaskForm):
    title = StringField('Title', filters=[strip_field],
                        validators=[validators.DataRequired()])
    artist = StringField('Artist', filters=[strip_field],
                         validators=[artist_validate,
                                     validators.DataRequired()])
    album = StringField('Album', filters=[strip_field],
                        validators=[validators.DataRequired()])
    label = StringField('Label', filters=[strip_field],
                        validators=[label_validate,
                                    validators.DataRequired()])


class AutomationTrackLogForm(FlaskForm):
    password = StringField('Password')
    title = StringField('Title', filters=[strip_field])
    artist = StringField('Artist', filters=[strip_field])
    album = StringField('Album', filters=[strip_field])
    label = StringField('Label', filters=[strip_field])
    dj_id = StringField('DJ ID')


class TrackLogEditForm(FlaskForm):
    title = StringField('Title', filters=[strip_field],
                        validators=[validators.DataRequired()])
    artist = StringField('Artist', filters=[strip_field],
                         validators=[artist_validate,
                                     validators.DataRequired()])
    album = StringField('Album', filters=[strip_field],
                        validators=[validators.DataRequired()])
    label = StringField('Label', filters=[strip_field],
                        validators=[label_validate,
                                    validators.DataRequired()])
    request = BooleanField('Request')
    vinyl = BooleanField('Vinyl')
    new = BooleanField('New')
    rotation = IntegerField('Rotation', default=1)
    played = StringField('Played')


class TrackLogForm(FlaskForm):
    track_id = IntegerField('Track ID')
    djset_id = IntegerField('DJSet ID')
    request = BooleanField('Request')
    vinyl = BooleanField('Vinyl')
    new = BooleanField('New')
    rotation = IntegerField('Rotation', default=1)
    played = StringField('Played')


class TrackLogAddForm(FlaskForm):
    djset_id = IntegerField('DJSet ID')
    title = StringField('Title', filters=[strip_field],
                        validators=[validators.DataRequired()])
    artist = StringField('Artist', filters=[strip_field],
                         validators=[artist_validate,
                                     validators.DataRequired()])
    album = StringField('Album', filters=[strip_field],
                        validators=[validators.DataRequired()])
    label = StringField('Label', filters=[strip_field],
                        validators=[label_validate,
                                    validators.DataRequired()])
    artist_mbid = StringField('Artist MBID',
                              filters=[strip_field],
                              validators=[validators.Optional(),
                                          validators.UUID()])
    release_mbid = StringField('Release MBID',
                               filters=[strip_field],
                               validators=[validators.Optional(),
                                           validators.UUID()])
    releasegroup_mbid = StringField('Release Group MBID',
                                    filters=[strip_field],
                                    validators=[validators.Optional(),
                                                validators.UUID()])
    recording_mbid = StringField('Recording MBID',
                                 filters=[strip_field],
                                 validators=[validators.Optional(),
                                             validators.UUID()])
    request = BooleanField('Request')
    vinyl = BooleanField('Vinyl')
    new = BooleanField('New')
    rotation = IntegerField('Rotation', default=1)
    played = StringField('Played')


class AirLogEditForm(FlaskForm):
    airtime = StringField('Air Time')
    logtype = IntegerField('Log Type', default=0)
    logid = IntegerField('Log ID', default=0)


class AirLogForm(FlaskForm):
    djset_id = IntegerField('DJSet ID')
    airtime = StringField('Air Time')
    logtype = IntegerField('Log Type', default=0)
    logid = IntegerField('Log ID', default=0)


class RotationForm(FlaskForm):
    rotation = StringField('Rotation', filters=[strip_field],
                           validators=[validators.Length(min=1, max=255),
                                       validators.DataRequired()])


class RotationEditForm(FlaskForm):
    visible = BooleanField('Visible', validators=[validators.Optional()])
