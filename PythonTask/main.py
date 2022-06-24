from fastapi import FastAPI, File, UploadFile, status
from fastapi.responses import FileResponse
from typing import Optional
import aiofiles
import uvicorn
import pycountry
import datetime


app = FastAPI()


@app.get("/")
async def home():
    return {"Hello": "World"}


@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    try:
        if file.content_type != "text/csv":
            return {status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "Unsupported media type"}
        out_header = "ID,Release Date,Name,Country,Copies Sold,Copy Price,Total Revenue"
        linechange = "\n"
        out_filename = "outfile.csv"
        content_list = []
        #Reading file content
        async with aiofiles.open(out_filename, 'wb') as f:
            content = await file.read()
            content = content.decode('ascii')
        for c in content.split("\r\n"):
            content_list.append(c)

        #Opening file to write
        f = open(out_filename, "w")
        f.write(out_header+linechange)

        #Reformat data
        #in ::= ID, Release Date (YYYY/MM/DD), Name (in kebab-case), ISO 3166 alpha-3 country code, Copies Sold, Copy Price
        #out ::= ID, Release Date (DD.MM.YYYY),Name (Capitalized), Country name, Copies Sold, Copy Price, Total Revenue (Copies Sold * Copy Price rounded to the nearest ones)
        for ind, line in enumerate(content_list):
            if ind == 0:
                continue
            items = line.split(',')
            id = items[0]
            date = datetime.datetime.strptime(items[1], '%Y/%m/%d').strftime('%d.%m.%y')
            name = (' '.join(items[2].split('-'))).title()
            countryName = pycountry.countries.get(alpha_3=items[3]).name
            copiesSold = items[4]
            price = items[5]
            revenue = str(round(int(copiesSold) * float(price.split(' ')[0]))) + ' USD'
            sequence = (id, date, name, countryName, copiesSold, price, revenue)
            output = ','.join(sequence)
            f.write(output+linechange)
        f.close()
        return FileResponse(path=out_filename, filename=out_filename, media_type='text/csv')


    except Exception as err:
        return {status.HTTP_500_INTERNAL_SERVER_ERROR: "Make sure the file content is in the correct format."}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
