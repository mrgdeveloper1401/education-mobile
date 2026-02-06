from apis.utils.custom_exceptions import VolumeImageExceptions


def max_upload_image_validator(value):
    max_size = 2
    image_size = value.size
    if image_size > max_size * 1024 * 1024:
        raise VolumeImageExceptions()
    return value
