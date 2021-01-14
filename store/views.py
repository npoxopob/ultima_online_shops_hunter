from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views import View
from django.template import RequestContext, Template
from django.db.models import Max, Min
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from store.models import Mapping
from store.models import Categories
from store.models import Vendor
from store.models import Results
from store.models import ItemStatistic


class StoreFront(View):

    def post(self, request, **kwargs):
        return HttpResponse('OK')

    # @method_decorator(login_required)
    def get(self, request, **kwargs):
        context = {}
        static_name = {}
        categories = [{"name": "Aspect Core", "img": "airaspectcorpse.png"},
                      {"name": "Aspect Extract-Distill", "img": "extract-distils.png"},
                      {"name": "Rares", "img": "rares.png", "items": ["a skill mastery orb",
                                                                      "research materials",
                                                                      "arcane essence",
                                                                      "prevalia coins",
                                                                      "mastercrafting diagram",
                                                                      "an ankh token"]},]

        for cat in categories:
            list_items = []
            actual_categories = Categories.objects.filter(name=cat['name'])
            mapping = Mapping.objects.filter(main_category__in=actual_categories)
            for m in mapping:
                if ('items' in cat and m.item_name in cat['items']) or ('items' not in cat):
                    itms = Results.objects.filter(mapping_categories=m)
                    item_lst = []
                    for i in itms:
                        item_total_price = round(i.item_total_price // int(i.item_name.split(":")[1].replace(' ', '')),
                                                 10) if ':' in i.item_name else i.item_total_price
                        item_lst.append(item_total_price)
                    if len(item_lst) != 0:
                        list_items.append(
                            {
                                'item_name': m.item_name,
                                'max': max(item_lst),
                                'min': min(item_lst)
                            }
                        )

                        context[cat['name']] = list_items
                        static_name[cat['name']] = cat['img']

        ss_query = Results.objects.filter(item_name__contains='skill mastery scroll').order_by('-item_name')
        list_items = []
        for record in sorted(
                sorted({s.item_name if ':' not in s.item_name else s.item_name.split(" :")[0] for s in ss_query})):
            itms = Results.objects.filter(item_name__contains=record)
            item_lst = []
            for i in itms:
                item_total_price = round(i.item_total_price // int(i.item_name.split(":")[1].replace(' ', '')),
                                         10) if ':' in i.item_name else i.item_total_price
                item_lst.append(item_total_price)

            list_items.append(
                {
                    'item_name': record,
                    'max': max(item_lst),
                    'min': min(item_lst)
                }
            )
        context['Skill Scrolls'] = list_items
        static_name['Skill Scrolls'] = "ss.png"
        # print(context)
        return render(request, 'store/store_front.html', {'context': context, 'static_name': static_name})


class Result(View):

    # @method_decorator(login_required)
    def get(self, request, **kwargs):
        request_get = request.GET.get('search', None)
        if request_get != None:
            results = Results.objects.filter(item_name__contains=request_get).order_by('-item_total_price').reverse()
            return render(request, 'store/result.html', {'context': results})
        else:
            raise Http404("Does not exist")


class Category(View):

    # @method_decorator(login_required)
    def get(self, request, **kwargs):
        request_get = request.GET.get('category', None)
        if request_get != None:
            # print()
            category = Categories.objects.get(name=request_get)
            mapping = Mapping.objects.filter(main_category=category)
            results_lst = []
            results = [Results.objects.filter(mapping_categories=m).order_by('-item_total_price').reverse()
                       for m in mapping]

            #TODO refactor this
            for rr in results:
                for r in rr:
                    results_lst.append(r)

            return render(request, 'store/category.html', {'context': results_lst, 'category': request_get})
        else:
            raise Http404("Does not exist")


class Itemstatistic(View):

    # @method_decorator(login_required)
    def get(self, request, **kwargs):
        request_get = request.GET.get('item_name', None)
        if request_get != None:
            statistic = ItemStatistic.objects.filter(item__name=request_get)
            results = Results.objects.filter(item_name__contains=request_get).order_by('-item_total_price').reverse()
            return render(request, 'store/item_statistic.html',
                          {'item_name': request_get, 'statistic': statistic, 'context': results})
        else:
            raise Http404("Does not exist")


class Vendors(View):

    # @method_decorator(login_required)
    def get(self, request, **kwargs):
        vendors = Vendor.objects.all().order_by("-vendor_name").reverse()
        return render(request, 'store/vendors.html', {'vendors': vendors})


class VendorProducts(View):

    # @method_decorator(login_required)
    def get(self, request, **kwargs):
        request_get_x = request.GET.get('x', None)
        request_get_y = request.GET.get('y', None)
        request_get_z = request.GET.get('z', None)
        if request_get_x != None and request_get_y != None and request_get_z != None:
            vendor = Vendor.objects.get(vendor_x=request_get_x,
                                        vendor_y=request_get_y,
                                        vendor_z=request_get_z)
            items = Results.objects.filter(vendor=vendor)
            return render(request, 'store/vendor_products.html', {'vendor': vendor, 'items': items})
        else:
            raise Http404("Does not exist")


class ShopLogin(View):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return HttpResponse('Allready log in')
        else:
            return render(request, 'store/login.html')

    def post(self, request, **kwargs):
        user, password = request.POST.get('login', None).replace('"', ''), \
                         request.POST.get('password', None).replace('"', '')
        user = authenticate(request, username=user, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse('success')
        else:
            return HttpResponse('fail')
