class MalformedSecret(Exception):
    """Raised when the secret is malformed"""
    pass


class AWSSecret:
    def __init__(self, secret):
        try:
            self.aws_name = secret['Name']
            split_name = self.aws_name.split("/")
            self.env = split_name[0]
            self.name = split_name[1]
        except IndexError:
            raise MalformedSecret
