#!/bin/bash

pip install -r requirements.txt --platform manylinux2014_x86_64 --target ./lambda_requirements --only-binary=:all:
cd ./lambda_requirements
zip -r ../open_ai_handler.zip .
cd ../src
zip ../open_ai_handler.zip ./chat_handler.py
cd ..
mv ./open_ai_handler.zip ./cdk
rm -r ./lambda_requirements
cd ./cdk
cdk diff           