# error response
class ProvisioningError(Exception):
    def __init__(self, error, status=400):
        self.error = error
        self.status = status
