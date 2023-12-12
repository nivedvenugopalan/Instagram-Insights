from fastapi import FastAPI, HTTPException, UploadFile, File
from io import BytesIO
from zipfile import ZipFile, BadZipFile

from analysis import DataAnalyzer
from helpers import parse_raw_data

app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Hello World"}

@app.get("/uploadfile/")
async def uploadfile(file: UploadFile = File(...)):
    # save the uploaded zip file
    contents = await file.read()
    file_io = BytesIO(contents)
    try:
        zip_ = ZipFile(file_io)
    except BadZipFile:
        # tell them that it is a bad zip file
        return HTTPException(status_code=400, detail="Bad zip file")

    parsed_data = parse_raw_data(zip_)
    analyzer = DataAnalyzer(parsed_data)

    data = analyzer.export()
    return data