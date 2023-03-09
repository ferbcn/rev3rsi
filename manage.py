#!/usr/bin/env python
import os
import sys
import uvicorn

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # custom run command for IDE development
    if sys.argv[1] == "runasgi":
        uvicorn.run(
            'mysite.asgi:application',
            host='0.0.0.0',
            port=8000,
            reload=True,
            # ssl_keyfile='cert/key.pem',
            # ssl_certfile='cert/cert.pem',
        )
    else:
        execute_from_command_line(sys.argv)

