from django.core.management.base import BaseCommand, CommandError
from divine.models import Compositions, FinishedGoods, RawMaterials

class Command(BaseCommand):
    help = 'Update prices for all Finished Goods'

    def handle(self, *args, **kwargs):
        finished_goods = FinishedGoods.objects.all()
        for finished_good in finished_goods:
            finished_good.price = 0
            total_quantity = 0
            compositions = Compositions.objects.filter(fg_id=finished_good.id)
            for composition in compositions:
                rm_obj = RawMaterials.objects.get(pk=composition.rm_id)
                comp_rm_quantity = float(composition.quantity)
                quantity_multiplier = 1
                unit = composition.unit
                if unit == 'GM':
                    quantity_multiplier = 0.001
                if unit == 'MG':
                    quantity_multiplier = 0.000001
                total_quantity += comp_rm_quantity * quantity_multiplier
                finished_good.price = finished_good.price + rm_obj.price * comp_rm_quantity * quantity_multiplier
            finished_good.price = finished_good.price / total_quantity
            print(finished_good.price)
            finished_good.save()
