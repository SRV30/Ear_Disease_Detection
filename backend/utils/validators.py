import re
from marshmallow import Schema, fields, validate, ValidationError

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{10,64}$")


class AuthSchema(Schema):
    email = fields.Str(required=True, validate=validate.Length(min=5, max=120))
    password = fields.Str(required=True, validate=validate.Length(min=10, max=64))


class ForgotPasswordSchema(Schema):
    email = fields.Str(required=True, validate=validate.Length(min=5, max=120))


class ResetPasswordSchema(Schema):
    token = fields.Str(required=True, validate=validate.Length(min=16, max=256))
    password = fields.Str(required=True, validate=validate.Length(min=10, max=64))


class ProfileSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(min=1, max=80))
    avatar = fields.Url(required=False)


def validate_auth_payload(payload):
    if not payload:
        raise ValidationError("JSON body is required")

    data = AuthSchema().load(payload)
    email = data["email"].strip().lower()
    password = data["password"]

    if not EMAIL_RE.match(email):
        raise ValidationError("Invalid email format")
    if not PASSWORD_RE.match(password):
        raise ValidationError("Password must be 10-64 chars with letter, number, and special char")

    return {"email": email, "password": password}


def parse_positive_int(value, default, minimum=1, maximum=100):
    try:
        num = int(value)
    except (TypeError, ValueError):
        return default
    return max(min(num, maximum), minimum)
