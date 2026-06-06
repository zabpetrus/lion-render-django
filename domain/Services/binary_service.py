import base64


class BinaryService:

    def execute(self, data):
        return base64.b64encode(data).decode()