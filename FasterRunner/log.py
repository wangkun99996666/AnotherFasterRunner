import logging


class DatabaseLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        from system.models import LogRecord  # 引入上面定义的LogRecord模型
        LogRecord.objects.create(
            request_id=record.request_id,
            level=record.levelname,
            message=self.format(record),
        )
