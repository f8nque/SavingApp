# SavingApp

The App Keep Track of all Daily Spent, You have to add Category Of the things you spend on most. The you can add Daily spent of the category every day The app will calculate the total Spent daily and monthly

There is a Savings and Budget Functionality that keep track of various category and inform the user if the user exceeds the category budget. The budget can be set for an individual category or for a bunch. Savings and debt can also be monitored,you can set a category as savings and it will be adding in the savings total, for debt you have to add a debt category and also a debt paid category to pay your debt in the system.

#future Functionality graphs for category analysis.

#how to install the site.

git clone f8nque/SavingApp.git

cd SavingsApp

pip3 install -r requirements.txt

#navigate to SavingsApp folder and update settings.py
cd SavingsApp/
edit the settings.py
ALLOWED_HOSTS = ['localhost','127.0.0.1'] # add the ip address that you want to use.

python3 manage.py migrate

python3 manage.py createsuperuser

python3 manage.py runserver 127.0.0.1:8080


Go to Browser and login using the password created using the password created using the createsuperuser command.
