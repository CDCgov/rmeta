from django.contrib import admin
from .models import DataStream, Transaction, TransactionHistory, Origin


class OriginAdmin(admin.ModelAdmin):
    list_display = ('name', 'ori','description', 'application', 'url', 'date_created', 'date_updated')
    search_fields = ('code', 'name', 'description')


admin.site.register(Origin, OriginAdmin)

class TransactionHistoryAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'status', 'date_created', 'date_updated')


admin.site.register(TransactionHistory, TransactionHistoryAdmin)


class DataStreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',) 


admin.site.register(DataStream, DataStreamAdmin)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('tcn', 'tcr', 'response_tcn' , 'ori', 'cri_1', 'cri_2',
                    'status_url', 'status', 'date_created', 'date_updated')


admin.site.register(Transaction, TransactionAdmin)
