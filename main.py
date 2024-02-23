from fastapi import FastAPI, Form
import pandas as pd
from fastapi.responses import *
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def to_pie(df:pd.DataFrame,col,title=""):
    plt.figure()
    plt.rc('font', family='Malgun Gothic') 
    plt.pie(df[col].values[0],labels=col, autopct='%1.1f%%')
    plt.title(title,fontsize=20)
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=80)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')
app=FastAPI()

with open('data.txt') as f:
    URL=f.read()
data=pd.read_csv(URL)
@app.get("/")
async def index():
    return FileResponse('index.html')

@app.post("/table")
async def table(name:str=Form(default=""),type:str=Form(default=""),make:str=Form(default=""),city1:str=Form(default=""),city2:str=Form(default="")):

    if city1=='전체':
        city1=""
    if city2=='전체':
        city2=""
    df=data.sort_values(by='남은 장학금',ascending=False)
    df=df[['학교명','학제','설립구분','시','지역']]
    df['학교명']=df['학교명'].apply(lambda x : f'<button type="submit" value="{x}" name="name">{x}</button>')
    df=df[df['학교명'].str.contains(name)&df['학제'].str.contains(type)&df['설립구분'].str.contains(make)&df['시'].str.contains(city1)&df['지역'].str.contains(city2)]
    return HTMLResponse("<center><form target='_top' action='school' method='post'>"+df.to_html(index=False,escape=False).replace('style="text-align: right;"','style="text-align: center;"')+"</form></center>")

@app.get("/table")
async def table():
    df=data.sort_values(by='남은 장학금',ascending=False)
    df=df[['학교명','학제','설립구분','시','지역']]
    df['학교명']=df['학교명'].apply(lambda x : f'<button type="submit" value="{x}" name="name">{x}</button>')
    return HTMLResponse("<center><form target='_top' action='school' method='post'>"+df.to_html(index=False,escape=False).replace('style="text-align: right;"','style="text-align: center;"')+"</form></center>")

@app.post("/school")
async def school(name:str=Form(...)):
    df=data[data['학교명']==name]
    inmoney=to_pie(df,df.columns[7:12],'교내 장학금 비율')
    money = to_pie(df,['교내장학금','교외장학금'],'장학금 비율')
    result=to_pie(df,['등록금','전체 장학금'],'등록금 장학금 차이')
    return HTMLResponse(f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}학교 정보</title>
</head>
<body>
    <center>
    <h1>{name}정보</h1>
    <a href="https://{df['학교홈페이지'].values[0]}" target="_blank">{name}홈페이지</a><br>
    <img style="width: 30%;" src="data:image/png;base64,{inmoney}">
    {df[data.columns[7:12]].to_html(index=False,escape=False)}
    <img style="width: 30%;" src="data:image/png;base64,{money}">
    {df[['교내장학금','교외장학금']].to_html(index=False,escape=False)}
    <img style="width: 30%;" src="data:image/png;base64,{result}">
    {df[['등록금','전체 장학금']].to_html(index=False,escape=False)}
    <button type="button" onclick="window.location.href='/'">처음으로</button>
    </center>
    
</body>
</html>''')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="44.226.145.213", port=8000, reload=True)

