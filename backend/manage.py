#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    try:
        import dotenv
        # 💡 .env 경로 명시 및 로딩 여부 출력
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        loaded = dotenv.load_dotenv(env_path)
        print(f"DEBUG: Loading .env from {env_path}")
        print(f"DEBUG: Success? {loaded}")
    except ImportError:
        print("DEBUG: python-dotenv library not found.")
        pass
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daylog.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
