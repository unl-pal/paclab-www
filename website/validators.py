from django.core.exceptions import ValidationError
from django.conf import settings

def validate_file_size(value):
    filesize = value.size
    
    if filesize > settings.MAX_FILE_UPLOAD:
        raise ValidationError("The maximum file size for profile photos is " + str(settings.MAX_FILE_UPLOAD))
    else:
        return value