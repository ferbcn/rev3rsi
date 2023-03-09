import os
import uvicorn

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

uvicorn.run(
    'mysite.asgi:application',
    host='0.0.0.0',
    port=8000,
    reload=True,
    # ssl_keyfile='cert/key.pem',
    # ssl_certfile='cert/cert.pem',
)