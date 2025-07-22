import streamlit as st
import requests

st.title("Students Score Predictor")

study_time=st.slider("Study Time",0,10,4)
attendance=st.slider("Attendance_days",1,100,30)
gender=st.selectbox("Gender",["Male","Femal"])

gender_Male=1 if gender=="Male" else 0

if (st.button("Predict Score")):
    inp_data={
        "study_time":study_time,
        "attendance":attendance,
        "gender_Male":gender_Male
    }

    response=requests.post("https://student-score-prediction-1.onrender.com/predict",json=inp_data)
    #st.write(result["Predicted_score"])
    result=response.json()
    st.write("Predicted score",result['Predicted_score'])
    
