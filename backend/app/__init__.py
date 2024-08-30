from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Define the IPs you want to block
BLOCKED_IPS = {"192.168.0.121", "192.168.0.202"}

class BlockIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        if client_ip in BLOCKED_IPS:
            # Optionally log the blocked attempt
            print(f"Blocked IP: {client_ip}")
            # Return a simple error message
            return JSONResponse(
                status_code=403,
                content={"status": False, "data": list([]), "message": "Forbidden"}
            )
            
        response = await call_next(request)
        return response

# Add the middleware to the FastAPI app
app.add_middleware(BlockIPMiddleware)



from app.routes import register_routers

register_routers(app)
