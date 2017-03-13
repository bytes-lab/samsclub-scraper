from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render

from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'quantity', 'min_quantity', 
                    'rating', 'review_count', 'updated_at']
    search_fields = ['title', 'bullet_points']
    actions = ['export_products']
    list_filter = ('category',)

    def export_products(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ids = ','.join([str(item.id) for item in queryset])
        fields = [f.name for f in Product._meta.get_fields() if f.name not in ['updated_at']]
        return render(request, 'product_properties.html', locals())    

    export_products.short_description = "Export products as CSV file"  


admin.site.register(Product, ProductAdmin)
