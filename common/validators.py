class SerializerValidator:
    """
    Validator that validates dict against another serializer,
    provided in constructor
    """
    def __init__(self, serializer_class):
        self.serializer_class = serializer_class

    def __call__(self, value):
        serializer = self.serializer_class(data=value)
        serializer.is_valid(raise_exception=True)
