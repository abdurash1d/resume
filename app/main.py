from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from .core.security import JWTAuthBackend
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import logging
from .core.config import settings
from .core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

from . import crud, models, schemas
from .db.base import Base, engine, get_db
from .core.security import get_current_active_user, get_current_user_from_token

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Manager API", version="1.0.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(
    AuthenticationMiddleware,
    backend=JWTAuthBackend()
)

# Include API routers
from .api import auth, resume, health
from .views import resume_views

# Include routers
app.include_router(health.router, prefix="/api")
app.include_router(auth.router)
app.include_router(resume.router, prefix="/api")
app.include_router(resume_views.router)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
import os
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
templates = Jinja2Templates(directory=templates_dir)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = None
    token = request.cookies.get("access_token")
    if token:
        try:
            from .core.security import get_current_user
            from fastapi import Depends
            from fastapi.security import OAuth2PasswordBearer
            from .db.base import get_db
            from jose import JWTError, jwt
            import os
            
            SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
            ALGORITHM = os.getenv("ALGORITHM", "HS256")
            
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email = payload.get("sub")
                if email:
                    db = next(get_db())
                    from .models.user import User
                    user = db.query(User).filter(User.email == email).first()
            except JWTError:
                pass
        except Exception as e:
            print(f"Error getting user: {e}")
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user)
):
    # If we get here, the user is authenticated
    try:
        # Get the user's resumes
        db = next(get_db())
        resumes = db.query(models.Resume).filter(
            models.Resume.user_id == current_user.id
        ).order_by(models.Resume.updated_at.desc()).all()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": current_user,
            "resumes": resumes
        })
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        # If there's an error, redirect to login
        response = RedirectResponse(url="/login")
        response.delete_cookie("access_token")
        return response

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(url="/login")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")

# Create static directory if it doesn't exist
os.makedirs("app/static", exist_ok=True)
