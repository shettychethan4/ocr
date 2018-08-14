
from flask import Flask,jsonify,request
from PIL import Image
import pytesseract
import pyzbar.pyzbar as pyzbar
import cv2
import io
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\chethan\Tesseract-OCR\tesseract'

def get_textExtraction(path):
    return pytesseract.image_to_string(path, config='-psm 6')


def get_serialNumber(path):
    def barcode(im):
        # Find barcodes and QR codes
        decodedObjects = pyzbar.decode(im)

        for obj in decodedObjects:
            barcode = 'Data : ', obj.data

        return barcode

    im = cv2.imread(path)
    slno = barcode(im)
    #something for second time

    return slno[1].decode()


def get_modelNumber(path):
    txt = pytesseract.image_to_string(path, config='-psm 6')

    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return "NF"

    model = find_between(txt, "Code: ", " ")

    if model == "NF":
        find_between(txt, "Code: ", " ")

    return model

app = Flask(__name__)
@app.route('/v1/ocr/', methods=['POST'])
def get_details():

    #gets the required details
    required_details = request.get_json()
    requests = required_details['requests']

    #gets features and Image URL
    for i in requests:
        features = i['features']
        imageURL = i['imageUri']

    #lists the required fetures needed
    # Note: Sequence of features should be same as the below order because it is accessing based on index-wise.
    flist = list(features)
    text_detection = flist[0]['TEXT_DETECTION']
    bar_code = flist[1]['BAR_CODE_DETECTION']
    model_number = flist[2]['MODEL_CODE_DETECTION']

    # checks for required features
    if text_detection == 'True':
        extract = get_textExtraction(imageURL)
    else:
        extract = None

    if bar_code == 'True':
        bar = get_serialNumber(imageURL)
    else:
        bar = None

    if model_number == 'True':
        model = get_modelNumber(imageURL)
    else:
        model = None

    return jsonify({'responses': [{
        "textAnnotations": [
            {
                "locale": "en",
                "text_description": extract,
                "boundingPoly": {
                    "vertices": [
                    ]
                }
            }, {
                "locale": "en",
                "barcode_description": bar,
                "boundingPoly": {
                    "vertices": [
                    ]
                }},
            {
                "locale": "en",
                "modelcode_description": model,
                "boundingPoly": {
                    "vertices": [
                    ]
                }
            }
        ]
    }]})


if __name__ == '__main__':
    app.run(debug=True)