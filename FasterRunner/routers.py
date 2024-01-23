import platform


class AutoChoiceDataBase:
    run_system = platform.system()
    is_windows = run_system == 'Windows'

    def db_for_read(self, model, **hints):
        if self.is_windows:
            return 'default'
        else:
            return 'remote'

    def db_for_write(self, model, **hints):
        if self.is_windows:
            return 'default'
        else:
            return 'remote'
