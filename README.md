## Ultima Online shops hunter
This repository contains web server application based on Django framework, 
csv files with pulled data from game, database with pulled 
items on vendors(placed by players) and prices statistic for each item for a time period which
allow getting fast search item and estimate offered price if you are not familiars with trends.

Data in result.csv and mapping.csv where scrapped by another application. You can make your method to scrap
data from game. The best way to get data from game is use [Stealth Client](https://stealth.od.ua/), but
not all Ultima Online shards allow to use this application.

This project was made for [UO Outlands](https://uooutlands.com/) shard

### How it's look like

#### Dasboard
![Alt text](static/Dashboard.png?raw=true "Dashboard with categories and items")

#### Item price statistic for all time period
![Alt text](static/item_statistic.png?raw=true "Item price statistic for all time period")

#### Vendor stocks
![Alt text](static/vendor_stock.png?raw=true "Vendor stocks")


## Getting Started

```bash
$ pip install -r src/ultima_online_shops_hunter/requirements.txt
$ cd src/ultima_online_shops_hunter
$ python manage.py runserver
```
or you can run system service
```bash
$ cp ultima_online_shops_hunter.service /etc/systemd/system/
$ systemctl daemon-reload
$ systemctl start ultima_online_shops_hunter.service
```





