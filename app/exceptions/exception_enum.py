from enum import Enum


class ErrorCode(str, Enum):
    # Auth
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_CREDENTIALS  = "INVALID_CREDENTIALS"
    INVALID_TOKEN        = "INVALID_TOKEN"
    TOKEN_EXPIRED        = "TOKEN_EXPIRED"

    # Users
    USER_NOT_FOUND       = "USER_NOT_FOUND"

    # General
    VALIDATION_ERROR     = "VALIDATION_ERROR"
    INTERNAL_ERROR       = "INTERNAL_ERROR"

    # Questions
    QUESTION_NOT_FOUND       = "QUESTION_NOT_FOUND"

    # Questions
    CHOICE_NOT_FOUND       = "CHOICE_NOT_FOUND"