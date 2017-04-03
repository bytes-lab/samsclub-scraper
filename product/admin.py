from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render
from django import forms

from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'quantity', 'min_quantity', 
                    'rating', 'review_count', 'updated_at', 'url']
    search_fields = ['title', 'bullet_points']
    actions = ['export_products']
    list_filter = ('category',)

    def export_products(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ids = ','.join([str(item.id) for item in queryset])
        fields = [f.name for f in Product._meta.get_fields() if f.name not in ['updated_at']]
        return render(request, 'product_properties.html', locals())    

    export_products.short_description = "Export products as CSV file"  


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'parent']
    search_fields = ['title', 'url']


class ScrapyTaskForm(forms.ModelForm):
    class Meta:
        model = ScrapyTask
        fields = '__all__'

    def clean(self):
        mode = self.cleaned_data.get('mode')
        category = self.cleaned_data.get('category')
        products = self.cleaned_data.get('products')
        
        if mode == 1:
            if not category:
                raise forms.ValidationError("Category should be provided in " 
                                            + "Category mode.")
        elif mode == 2:
            for item in products.split(','):
                try:
                    a = int(item)
                except Exception, e:
                    raise forms.ValidationError("Products should be comma "
                        + "seperated product id list e.g) 12432, 12424, ...")
        return self.cleaned_data


class ScrapyTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'mode', 'status', 'interval', 'last_run',
                    'created_at']
    search_fields = ['title']
    readonly_fields = ['status', 'last_run']
    form = ScrapyTaskForm


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ScrapyTask, ScrapyTaskAdmin)
