import base64
import sys

for key in sys.argv[1:]:
    with open(key, "rb") as image_file:
        # encoded_string = image_file.read().encode('base64')
        encoded_string = base64.b64encode(image_file.read())
        print('"%s": "%s",' % (key, encoded_string))
