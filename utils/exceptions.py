class FakeAdGeneratorException(Exception):
    """基础异常类"""
    pass

class LoginFailedException(FakeAdGeneratorException):
    """登录失败异常"""
    pass

class FileNotFoundError(FakeAdGeneratorException):
    """文件未找到异常"""
    pass

class ImageUploadException(FakeAdGeneratorException):
    """图片上传异常"""
    pass

class StatusCheckException(FakeAdGeneratorException):
    """状态检查异常"""
    pass

class ExcelReadException(FakeAdGeneratorException):
    """Excel读取异常"""
    pass

class StudentFolderNotFoundException(FakeAdGeneratorException):
    """学生文件夹未找到异常"""
    pass

class NoImagesFoundException(FakeAdGeneratorException):
    """未找到图片异常"""
    pass 