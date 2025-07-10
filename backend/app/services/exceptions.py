# 自定义异常类
class ServiceError(Exception):
    """服务层基础异常"""
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        super().__init__(self.message)

class CourseFullError(ServiceError):
    """课程人数已满异常"""
    def __init__(self, message="课程人数已满"):
        super().__init__(message, 400)

class TimeConflictError(ServiceError):
    """时间冲突异常"""
    def __init__(self, message="课程时间冲突"):
        super().__init__(message, 400)

class AlreadyEnrolledError(ServiceError):
    """已经选课异常"""
    def __init__(self, message="已经选过这门课"):
        super().__init__(message, 400)

class PrerequisiteNotMetError(ServiceError):
    """先修课程未满足异常"""
    def __init__(self, message="先修课程要求未满足"):
        super().__init__(message, 400)

class CourseNotFoundError(ServiceError):
    """课程不存在异常"""
    def __init__(self, message="课程不存在"):
        super().__init__(message, 404)

class StudentNotFoundError(ServiceError):
    """学生不存在异常"""
    def __init__(self, message="学生不存在"):
        super().__init__(message, 404)

class InsufficientPermissionError(ServiceError):
    """权限不足异常"""
    def __init__(self, message="权限不足"):
        super().__init__(message, 403)
