from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt_utils as jwt
from db import skills_repository, gold_price
from forecasting import prophet_model

app = FastAPI()

origins = [
    #"http://192.168.100.116:4200"
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
def login(data: LoginRequest):
    if data.email == "ipuwadon@gmail.com" and data.password == "MyNameIsPuw":
        token = jwt.create_access_token({"sub": data.email})
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@app.get("/dashboard")
def dashboard(authorization: str = Header(...)):
    token = authorization.split(" ")[1]

    payload = jwt.verify_token(token, "MyNameIsPuw")
    if payload:
        return {"message": f"Welcome {payload['sub']}!"}
    else:
        return HTTPException(status_code=401, detail="Invalid token")

@app.get("/skills")
def get_skills():
    return skills_repository.get_all_skills()
    #return ["PL/SQL", "SQL", "Python", "Oracle DB", "Oracle Forms", "Oracle Reports", "Sprint boot"]

@app.get("/gold-prices")
def get_gold_prices():
    return gold_price.get_gold_prices()

@app.get("/gold-prices-predictive")
def get_gold_prices_predict(periods: int = Query(10, ge=1, le=365)):
    forecast = prophet_model.forecast_gold_prices(periods)

    return {"forecast": forecast}