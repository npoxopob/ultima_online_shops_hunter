from django.db import models


# Create your models here.
class Categories(models.Model):
    name = models.CharField(max_length=255)


class Mapping(models.Model):
    item_id_plus_hue = models.BigIntegerField(primary_key=True, unique=True)
    item_id = models.CharField(max_length=255)
    item_hue = models.CharField(max_length=255)
    main_category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='сategories')
    item_name = models.CharField(max_length=255)


class Vendor(models.Model):
    vendor_name = models.CharField(max_length=255)
    vendor_point_name = models.CharField(max_length=255)
    vendor_x = models.CharField(max_length=255)
    vendor_y = models.CharField(max_length=255)
    vendor_z = models.CharField(max_length=255)


class History(models.Model):
    date = models.DateTimeField(auto_now=False)


class Results(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='to_vendor', null=True)
    mapping_categories = models.ForeignKey(Mapping, on_delete=models.SET_NULL, related_name='to_mapping_categories',
                                           null=True)
    time_stamp = models.ForeignKey(History, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=255, null=True)
    item_description = models.CharField(max_length=255, null=True)
    item_total_price = models.BigIntegerField(default=0)


class CurrentStatistic(models.Model):
    date = models.ForeignKey(History, on_delete=models.SET_NULL, null=True)
    total_vendors = models.CharField(max_length=255, default=None, null=True)


class CategoriesStatistic(models.Model):
    cat_name = models.CharField(max_length=255)
    count = models.CharField(max_length=255)


class ItemsLibrary(models.Model):
    name = models.CharField(max_length=255, null=True)


class ItemStatistic(models.Model):
    date = models.ForeignKey(History, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(ItemsLibrary, on_delete=models.SET_NULL, related_name='to_mapping_categories', null=True)
    max_price = models.BigIntegerField(default=0)
    min_price = models.BigIntegerField(default=0)
