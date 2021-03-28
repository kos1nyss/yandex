
1-- Установка пакетов ---
sudo apt-get update
sudo apt install python3-pip --fix-missing
sudo apt install git
sudo apt install postgresql postgresql-contrib --fix-missing
sudo -u postgres createdb delivery
------

2-- Установка пароль к бд ---
sudo -u postgres psql
\password postgres (Пароль ставить Kostya)
\q

3-- Установка репозиторая ---
mkdir project
cd project
git init
git clone https://github.com/kos1nyss/yandex
cd yandex
pip3 install -r requirements.txt

4-- Запуск сервиса ---
файл находится в .../project/yandex/
python3 main.py

--- Запуск тестов ---
очистить бд перед тестами
pytest tests/<название файла из папки>
testAddCouriers.py - тесты для первого обработчика
testAddOrders.py - тесты для третьего обработчика
