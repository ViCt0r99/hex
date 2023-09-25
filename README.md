# Hex-ocean
## local run
In order to run project make sure you have docker installed on your local machine,
then clone this repo and create `.env` file using `.env.example` file. Then you're ready to go!
Open terminal in project directory and type following command:
```shell
docker-compose -f docker-compose.yaml up --build --remove-orphans
```
Containers should be running smoothly and without any problem.
Remember to create admin user to proceed with testing
on local. Firstly you have to establish pipenv enviroment on machine:
```shell
cd src
pipenv install -d
pipenv shell
```
After installing all packages you will be able to create django admin with following commands:
```shell
cd src
python manage.py createsuperuser
```
