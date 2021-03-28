sudo apt-get update
sudo apt install python3-pip --fix-missing
sudo apt install git
sudo apt install postgresql postgresql-contrib --fix-missing
sudo -u postgres createdb delivery

sudo -u postgres psql
\password postgres (Пароль ставить Kostya)
\q

mkdir project
cd project
git init
git clone https://github.com/kos1nyss/yandex
cd yandex
pip3 install -r requirements.txt

python3 main.py


