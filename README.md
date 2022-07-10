# pdf-renderer

## Installation and usage
* Prepare folders:
```
chmod +x prepare_env.sh 
./prepare_env.sh
```
* `docker-compose up`

The service is then accessible on URL `http://0.0.0.0:5000` and you can use these endpoints:

* POST `/upload`: upload PDF file and convert its pages to images
* GET `/document/<id>`: get document info by its ID
    * example: `http://0.0.0.0:5000/document/1`
* GET `/image/<document_id>/<page_number>`: get desired image file
    * example" `http://0.0.0.0:5000/image/1/1`

More details are available in the generated [Swagger docs](http://0.0.0.0:5000/api/docs).

## Description

### Architecture

The app uses following components:
* API: to serve clients
    * `Flask`
* PostgreSQL DB: to store info about documents
    * `SQLAlchemy`
* Cloud storage: to store input files and converted images
    * client: `boto3`
    * local server: `Minio`, in production S3/GCS
    * why? 
        * files can't be (easily) serialized into Redis for Dramatiq workers
        * Redis could fill up with PDF files :D 
    * paths: 
        * `/documents/<doc_id>/input.pdf` for PDF file
        * `/documents/<doc_id>/<page_number>.png` for images
* Workers: to convert PDF file to images
    * `Dramatiq`
* Redis: worker broker, could be used also for caching

### Scalability

I think the app could scale well. Some comments:

* API: endpoints don't do any heavy work (maybe apart from `/upload`) so there should be no bottleneck
    * improvements: use `FastAPI` with async server and client code
* PostgreSQL: should be ok, only simple data in DB, one index
    * We could use cloud storage instead. I know it sounds weird but for simple apps like this I wouldn't be afraid to do it. IMHO little more work with saving/quering pays in not having to pay for DB instance/take care of instance scaling.
* Cloud storage: basically unlimited scaling
    * in production a retention period would be set for input files and also for images
* Workers: here I find little tricky to set how many worker threads should be in one container. In production this would require some testing to optimize resource usage.

### TODO

* Use `Alembic` for DB migrations
* Properly setup `Datadog` tracing and tracking (`statsd`)
* Use `Dependency injector` package instead of `dependencies.py`
* Some user identification and/or authorization, via headers or basic auth
* Better `app.py` file - use models, blueprints. I don't know Flask very well so it's little messy.
* Use `FastAPI` instead of Flask :D
* Tests - better mocking
* In `1s3_storage` the files are saved as folder, I don't know why, in production it would be better to make sure it's just a file.
* Would be better to use Python 3.10. I used Python 3.9 bcs of some problems with Poetry on my local computer.
