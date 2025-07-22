from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np 

model =joblib.load("model/score_model.pkl")

class Stu_Data(BaseModel):
    study_time: float
    attendance: float
    gender_Male:int

app=FastAPI()

@app.get("/")
def root():
    return {"Message": "Score Prediction API" }

@app.post("/predict")
def predict_score(data: Stu_Data):
    inp_data=np.array([[data.study_time,data.attendance,data.gender_Male]])
    prediction=model.predict(inp_data)
    return {"Predicted_score":int(prediction[0])}
