import django.db.utils
from django.core.management.base import BaseCommand
import logging
from datetime import datetime, date
from django.db.models import Max, Min
from django.conf import settings
from store.models import Mapping
from store.models import Categories 
from store.models import Vendor
from store.models import Results
from store.models import History
from store.models import CurrentStatistic
from store.models import CategoriesStatistic
from store.models import ItemStatistic
from store.models import ItemsLibrary

from pyexcel_ods import get_data
import json

class Command(BaseCommand):
	help = "Синхронизация данных из csv по в базу данных"

	def __init__(self):
		super().__init__()
		
		self.mapping_file = settings.BASE_DIR + '/' + 'mapping.csv'
		print('Loading {0}...'.format(self.mapping_file))
		self.mapping_data = get_data(self.mapping_file)
		
		self.result_file = settings.BASE_DIR + '/' + 'result.csv'
		print('Loading {0}...'.format(self.result_file))
		self.result_data = get_data(self.result_file)

		logging.basicConfig(filename="/var/log/ultima_db_syncs", level=logging.INFO)

	def write_history(self):
		print('Writing prices and other history')

		date = History.objects.all().last()
		dont_split = ['a potion keg', 'treasure map', 'runebook']

		search_array = Results.objects.all()

		upload_to_db = {}

		for item in search_array:
			try:
				stackable_items = True if len(search_array.filter(item_name__contains = item.item_name).filter(item_name__contains = ":")) != 0 else False
				ds_result = {True if x in item.item_name else False for x in dont_split}
				if stackable_items and True not in ds_result:
					name = item.item_name.split(" :")[0]
				else:
					name = item.item_name

				library_item, created = ItemsLibrary.objects.get_or_create(name = name)
				if created:
					print("Created new item {0} in items library".format(name))
					library_item.save()
			except Exception as e:
				print(e)
				print("Error while creating record {0} in items library".format(name))
				return 1


		items_from_library = ItemsLibrary.objects.all()
		for item in items_from_library:
			stackable_items = True if len(search_array.filter(item_name__contains = item.name).filter(item_name__contains = ":")) != 0 else False
			ds_result = {True if x in item.name else False for x in dont_split}
			price_list = []
			if stackable_items and True not in ds_result:
				lots = search_array.filter(item_name__contains = item.name)
				for lot in lots:
					if ':' in lot.item_name:
						items_in_stack = int(lot.item_name.split(":")[1].replace(' ',''))
						price_list.append(lot.item_total_price // items_in_stack)
					else:
						price_list.append(lot.item_total_price)
				if len(price_list) == 0:
					continue
				upload_to_db[item.name] = {
										   'max': max(price_list),
										   'min': min(price_list)
										   }
			else:
				lots = search_array.filter(item_name = item.name)
				for lot in lots:
					price_list.append(lot.item_total_price)
				if len(price_list) == 0:
					continue
				upload_to_db[item.name] = {
										   'max': max(price_list),
										   'min': min(price_list)
										   }

			try:
				stat_item, created = ItemStatistic.objects.get_or_create(
					item = item,
					date = date,
					defaults = {
						'max_price': upload_to_db[item.name]['max'],
						'min_price': upload_to_db[item.name]['min'],
					}
				)
				if created:
					stat_item.save()
					print("Created statistic for item {0} {1}".format(item.name, {'max': stat_item.max_price, 'min':stat_item.min_price}))
			except Exception as e:
				print("Error while statistic for item {0} {1}".format(item.name, {'max': stat_item.max_price, 'min':stat_item.min_price}))
				print(e)


	def read_date(self):
		for _, value in self.result_data.items():
			for v in value:
				if v[3] != 'VendorX':
					try:
						date, created = History.objects.get_or_create(date=v[0])
						if created:
							date.save()
						curstat, created = CurrentStatistic.objects.get_or_create(date=date)
						if created:
							curstat.save()
						return date
					except Exception as e:
						print(Exception, e)
						print("From file:{0}".format(v))
						return 1

	def update_categories_mapping(self):
		print('Trying to update mapping and categories...')
		for _, value in self.mapping_data.items():
			for v in value:
				if v[0] != 'ID':
					#Обновление таблицы store_categories
					try:
						obj, created = Categories.objects.get_or_create(name = v[3])
						if created:
							obj.save()
							print('Updated  categories record {0}'.format(v))
					except Exception as e:
						print(e)
						print('Error while updating categories records ', v[0])
					#Обновление таблицы store_mapping
					try:
						obj, created = Mapping.objects.get_or_create(
							item_id_plus_hue = v[0],
							item_id = v[1],
							item_hue = v[2],
							main_category = Categories.objects.get(name = v[3]),
							item_name = v[4],
							)
						if created:
							print('Updated mapping record {0}'.format(v))
							obj.save()
					except Exception as e:
						print(e)
						print('Error while updating mapping records ', v[0])
						return 1

		print('Update successfully')

	def update_vendors_and_products(self):
		date = self.read_date()
		#Запись об истории цен и прочего в таблицу историчности
		#self.write_history()
		#Очистка таблицы с предыдущими результатами
		print('Deleting last results')
		Results.objects.all().delete()
		Vendor.objects.all().delete()
		#date = datatime.datatime.now()

		print('Trying to update vendors and products...')
		for _, value in self.result_data.items():
			for v in value:
				if v[3] != 'VendorX' and v[2] != '':
					try:
						vendor, created = Vendor.objects.get_or_create(
							vendor_x = v[3],
							vendor_y = v[4],
							vendor_z = v[5],
							defaults = {
										'vendor_point_name': v[1],
										'vendor_name': v[2]
										}
						)
						if created:
							print('Creating new Vendor shop: {0} X:{1} Y:{2}'.format(v[2],v[3],v[4]))
							vendor.save()
					except Exception as e:
						print(e)
						print('Error while creating new Vendor record')
						return 1

					_ = Vendor.objects.filter(vendor_name = v[2])
					if _.count() == 0:
						vendor_update = Vendor.objects.get(vendor_x = v[3], vendor_y = v[4], vendor_z = v[5])
						print('Updating vendor_name {0} to {1} in {2}:  X:{3}, Y:{4}, Z:{5}'.format(
							  vendor_update.vendor_name,
							  v[2], v[1], v[3], v[4], v[5]
							 )
						)
						try:
							vendor_update.vendor_name = v[2]
							vendor_update.save()
						except Exception as e:
							print(e)
							print('Error while updating vendor_name {0}'.format(v[2]))
							return 1
					
					try:
						mapping = Mapping.objects.get(item_id = v[10], item_hue = v[11])
					except Exception as e:
						print('Mapping does not exist item_name:{0} item_description:{1} item_id:{2}  item_hue:{3}'.format(v[6],v[7],v[10],v[11]))
						mapping = None

					if v[8] != 'Not for sale.'  and v[6] != '': 
						try:
								result = Results.objects.create(
									vendor = vendor,
									mapping_categories = mapping,
									time_stamp = date,
									item_name = v[6],
									item_description = v[7],
									item_total_price = v[8]
								)
								result.save()
								print('Created item {0}'.format(result.item_name))
						except Exception as e:
							print(e)
							print('Error while creating results records {0}'.format(v))
							return 1


	def aggregate_data(self):
		date = History.objects.all().last

		#Items by categories
		CategoriesStatistic.objects.all().delete()
		for categorie in Categories.objects.all():
			mapping = Mapping.objects.filter(main_category = categorie)
			cs = CategoriesStatistic.objects.create(cat_name = categorie.name,
											   count = Results.objects.filter(mapping_categories__in=mapping).count()
											   )
			cs.save()



	def handle(self, *args, **options):
		self.update_categories_mapping()
		self.update_vendors_and_products()
		self.write_history()
		self.aggregate_data()
