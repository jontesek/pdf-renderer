# pdf-renderer

## Installation and usage
* Prepare folders:
```
chmod +x prepare_env.sh 
./prepare_env.sh
```
* `docker-compose up`

The service is then accessible on URL `http://0.0.0.0:5000` and you can use three endpoints:

* POST `/upload`: upload PDF file and convert its pages to images
* GET `/document/<id>`: get document info by its ID
    * example: `http://0.0.0.0:5000/document/1`
* GET `/image/<document_id>/<page_number>`: get desired image file
    * example" `http://0.0.0.0:5000/image/1/1`

More details are available in the generated [Swagger docs](http://0.0.0.0:5000/api/docs).