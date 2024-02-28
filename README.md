# Amazon Klone With Flask + HTMX

----------
##  🎮 Project Overview
----------

This is a small demo project that aims to replicate some of the functionality from Amazon using Flask and HTMX.
A working demo can be found at: https://amazon-klone.onrender.com

NB:  No blueprints were used per the specifications of the assignment and the website takes some time to load using render.

## 🧰 **Requirements**
----------

You can install all the requirements by running the following command from the main project directory:


    pip install -r requirements.txt

In addition, you will also need access to Mongo DB which can be installed following the docs at: https://www.mongodb.com/docs/manual/installation/.

## 🟢 Quick Start
----------

 **After installing** [**requirements**]
First, you need to set up your environment variables in your .env file. 
When running the application for the first time, you must set the FLASK_ENV variable to setup to set up the initial collections in mongo db.

An example is shown below.

    #app config
    SECRET_KEY='123'
    # db config
    DB_URL="sqlite:///amazon-klone.db"
    # mongo db config
    MONGO_URL="mongodb://localhost:27017/"
    
    FLASK_ENV=setup

From here you can run 

    python main.py

Once the project has been set up, you can remove this env variable (or change it to development which enables logging as per assignment specifications)
From the main project directory run:

     flask --app main run

