# Flask Tutorial

This repository contains flask demo applications with Postman documentations.

For all apps, Flask, Docker and MongoDB (local) are utilized.

All materials are covered in [Udemy 
Course](https://www.udemy.com/course/python-rest-apis-with-flask-docker-mongodb-and-aws-devops/)

## Similarity API

This demo app checks 2 texts' similarity using `spacy`

## Image Recognition API

This demo app predicts objects/animals in image being provided as URL. NN model is used from Tensorflow library 
and ResNet50 model. [link](https://keras.io/api/applications/#usage-examples-for-image-classification-models/)

## Setup

Run following command to run apps. Make sure you are inside App's dir location

```
sudo docker-compose build && docker-compose up
```
