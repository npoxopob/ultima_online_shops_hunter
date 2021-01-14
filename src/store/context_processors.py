from .models import CategoriesStatistic
from .models import History
from .models import Vendor


def sections_processor(request):
    categories = {categorie.cat_name: categorie.count
                  for categorie in CategoriesStatistic.objects.all().order_by('cat_name')}

    date = History.objects.all().order_by('-pk').last().date
    vendors_stat = Vendor.objects.all().count()

    return {'categories': categories, 'date': date, 'vendors_stat': vendors_stat}
