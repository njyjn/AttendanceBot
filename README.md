# AttendanceBot
A Telegram bot which helps Caregroup Leaders in Arrow Ministry tabulate their group attendance.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisities

Install pip
```
apt install pip3
```

Install Python
```
apt install python3
```

Install Telepot framework
```
pip install telepot
```

Install MongoDB - instructions vary, refer to your server guide on how to.

Install pymongo
```
pip install pymongo
```

## Deployment

You may use any Python engine to host your bot. I used Digital Ocean with a Linux distro.

1. Run the bot using 
```
python3 main.py
```
&nbsp;
2. Run the database using
```
mongod --dbpath directory/to/database
```
&nbsp;
3. To access your database console at any time, use
```
mongo acglbot 
```
_This assumes you have used **acglbot** as the name of the database._

Highly recommend for to use [screen](https://remysharp.com/2015/04/27/screen) to run main.py in the background. This enables you to switch terminals at anytime while preserving the functionality of the bot, and also prevent you from losing access to your bot in case you lose connection to the terminal.

## Contributors

* **Nicm Lee** - *Telepot* - [nickoala](https://github.com/nickoala/telepot)
* **Darren Wee** - *Code Base* - [darrenwee](https://github.com/darrenwee)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details