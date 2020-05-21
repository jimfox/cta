# CTA

This is the maintenance tool for the online Catalog of Teratogenic Agents.

## Deployment

This uses Google App Engine, Google Cloud Storage for a database.

## Database

The 'database' is a single text file with LaTeX markup.  Originally this package (its ancestors, anyway) 
produced a real book.  That was before the internet.  

The LaTeX markup continues, but presently only the online editor is supported.

## Setup to install from new workstation

1. You need the gcloud tools.
2. Setup authn via google cloud services
3. $ gcloud init
    * project: some_app_id
    * login id: your_google_id
    * i use uswest1

4. Install cloud storage library
    1. $ virtualenv env
    2. $ . env/bin/activate
    3. $ mkdir lib
    4. $ pip install GoogleAppEngineCloudStorageClient -t lib

5. Deploy the app
    * $ gcloud app deploy

6. Upload the catalog (catalog.tex) to your app's principla storage bucket.

7. View
    * $ https://your-apps-id.appspot.com/




## Setup to install from new workstation

1. You need the gcloud tools.
2. Setup authn via google cloud services
3. $ gcloud init
    * project: some_app_id
    * login id: your_google_id
    * i use uswest1

4. Install cloud storage library
    1. $ virtualenv env
    2. $ . env/bin/activate
    3. $ mkdir lib
    4. $ pip install GoogleAppEngineCloudStorageClient -t lib
   
5. deploy to google
    * $ gcloud app deploy

6. view
    * $ https://some_app_id.appspot.com/

