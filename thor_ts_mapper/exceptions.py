class Thor2tsError(Exception):
    def __init__(self, error_msg="An error occurred in thor-ts-mapper"):
        self.error_msg = error_msg
        super().__init__(self.error_msg)

#input errors
class InputError(Thor2tsError):
    def __init__(self, error_msg="Input validation error"):
        super().__init__(error_msg)


class FileValidationError(InputError):
    def __init__(self, error_msg="File validation error"):
        super().__init__(error_msg)


class JsonFileNotFoundError(FileValidationError):
    def __init__(self, error_msg="JSON file not found"):
        super().__init__(error_msg)


class JsonFileNotReadableError(FileValidationError):
    def __init__(self, error_msg="JSON file is not readable"):
        super().__init__(error_msg)


class JsonEmptyFileError(FileValidationError):
    def __init__(self, error_msg="JSON file is empty"):
        super().__init__(error_msg)


class JsonInvalidFileExtensionError(FileValidationError):
    def __init__(self, error_msg="Invalid file extension"):
        super().__init__(error_msg)


class JsonValidationError(InputError):
    def __init__(self, error_msg="JSON validation error"):
        super().__init__(error_msg)

class JsonParseError(InputError):
    def __init__(self, error_msg="JSON parsing error"):
        super().__init__(error_msg)

#processing errors

class ProcessingError(Thor2tsError):
    def __init__(self, error_msg="Error processing THOR data"):
        super().__init__(error_msg)


class MappingError(ProcessingError):
    def __init__(self, error_msg="Error mapping THOR data"):
        super().__init__(error_msg)

class JsonFlatteningError(ProcessingError):
    def __init__(self, error_msg="Error flattening JSON log"):
        super().__init__(error_msg)

class VersionError(ProcessingError):
    def __init__(self, error_msg="Unsupported THOR log version"):
        super().__init__(error_msg)


#output errors
class OutputError(Thor2tsError):
    def __init__(self, error_msg="Error writing or sending output"):
        super().__init__(error_msg)


class TimesketchError(OutputError):
    def __init__(self, error_msg="Error connecting to Timesketch"):
        super().__init__(error_msg)