import logging
import requests
from flask import Flask, request
from models.plate_reader import PlateReader, InvalidImage
from image_provider_client import ImageProviderClient
import io


ALLOWED_IDS = set([10022, 9965])
IMAGES_HOST = 'http://178.154.220.122:7777'

app = Flask(__name__)
# создаем клиент для инференса модели
plate_reader = PlateReader.load_from_file(
    path='./model_weights/plate_reader_model.pth'
)
# создаем клиент для загрузки изображений
provider_client = ImageProviderClient(IMAGES_HOST)


# <url>:8080/readPlateNumber?image_ids=<image_id1,image_id2,...>
# {"9965": "о101но750"}
@app.route('/readPlateNumber')
def read_plate_number():
    # проверяем, что аргумент `image_ids` задан
    if 'image_ids' not in request.args:
        return {'error': 'field "image_ids" is not specified'}, 400
    # разбиваем id изображений по `,`
    image_ids = request.args['image_ids'].split(',')

    answers = {}
    # обрабатываем в цикле все `id`
    for image_id in image_ids:
        # конвертируем id: str -> int
        try:
            image_id = int(image_id)
        except ValueError:
            return {'error': f'image id must be integer: {image_id}'}, 400
        # проверяем, что id является допустимым
        if image_id not in ALLOWED_IDS:
            return {'error': f'image id not found: {image_id}'}, 404
        # загружаем картинку
        try:
            image = provider_client.get_image(image_id)
        except requests.exceptions.Timeout:
            return {'error': 'timeout for accessing the server with images '
                    'has been reached'}, 504
        except Exception:
            return {'error': 'error accessing the server with images'}, 500

        try:
            image = io.BytesIO(image)
        except TypeError:
            return {'error': 'the server with images should return jpeg in '
                    'binary form'}, 500
        # распознаем номер на картинке
        try:
            res = plate_reader.read_text(image)
        except InvalidImage:
            logging.error('invalid image')
            return {'error': 'invalid image'}, 400
        # записываем ответ в словарик
        answers[image_id] = res
    # оправляем ответ (для answers автоматически вызывается jsonify)
    return answers


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, debug=True)
