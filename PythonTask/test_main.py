from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_file():
    with open("abc.csv", "rb") as f:
        response = client.post("/uploadfile/", files={"file": ("filename", f, "text/csv")})
    assert response.status_code == 200

def test_upload_file_invalid_file():
    with open("invalidfile.pdf", "rb") as f:
        response = client.post("/uploadfile/", files={"file": ("filename", f, "application/pdf")})
    assert response.status_code == 200
    assert response.json() == {'415': "Unsupported media type"}

def test_upload_file_invalid_filecontent():
    with open("invalidcontent.csv", "rb") as f:
        response = client.post("/uploadfile/", files={"file": ("filename", f, "text/csv")})
    assert response.status_code == 200
    assert response.json() == {'500': "Make sure the file content is in the correct format."}