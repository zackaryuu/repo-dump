import io
import base64


def load_base64_img(string: str):
    """
    Load an image from a base64 encoded string.

    Args:
        string (str): The base64 encoded string representing the image.

    Returns:
        Image: The loaded image object.

    This function takes a base64 encoded string as input and loads an image from it. It checks if the string starts with
    "data:image/png;base64," and removes that prefix if it exists. Then, it decodes the base64 string using the
    `base64.b64decode` function and creates an in-memory bytes object using `io.BytesIO`. Finally, it uses the
    `Image.open` function from the Pillow library to open the image from the bytes object and returns the loaded image.
    """

    from PIL import Image

    if string.startswith("data:image/png;base64,"):
        string = string[22:]
    return Image.open(io.BytesIO(base64.b64decode(string)))


def image_to_base64(img):
    """
    Convert an image to a base64 encoded string.

    Args:
        img (Image): The image to be converted to a base64 encoded string.

    Returns:
        str: The base64 encoded string representation of the image.
    """
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def image_to_base64_markdown(img):
    """
    Convert an image to a base64 encoded string with a data URI prefix.

    Args:
        img (Image): The image to be converted to a base64 encoded string.

    Returns:
        str: The base64 encoded string representation of the image with a data URI prefix.
    """
    return "data:image/png;base64," + image_to_base64(img)


def is_base64(string: str):
    try:
        if string.startswith("data:image/png;base64,"):
            string = string[22:]
        base64.b64decode(string, validate=True)
        return True
    except:  # noqa
        return False
