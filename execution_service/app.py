import uvicorn
from execution_layer import create_app

from prometheus_client import make_asgi_app, Counter, Histogram
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_COUNT = Counter('request_count', 'Total number of requests', ['app_name', 'method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['app_name', 'endpoint'])

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path
        app_name = 'execution_service'
        REQUEST_COUNT.labels(app_name=app_name, method=method, endpoint=endpoint).inc()
        with REQUEST_LATENCY.labels(app_name=app_name, endpoint=endpoint).time():
            response = await call_next(request)
        return response

app = create_app()
app.add_middleware(MetricsMiddleware)
app.mount("/metrics", make_asgi_app())

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8003)
