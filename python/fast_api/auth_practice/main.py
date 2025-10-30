from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from auth_jwt import create_access_token, decode_access_token, hash_password, verify_password

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake "database" with hashed passwords
fake_users_db = {
    "alice": {"username": "alice", "hashed_password": hash_password("secret123")},
    "bob": {"username": "bob", "hashed_password": hash_password("mypassword")},
}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return {"message": f"Hello {payload['sub']}! You are authenticated."}
