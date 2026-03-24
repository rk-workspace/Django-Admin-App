from django import forms
# from django.utils.translation import gettext_lazy as _
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Submit
# from .models import RawMaterials, FinishedGoods


# class RawMaterialForm(forms.ModelForm):
#     class Meta:
#         model = RawMaterials
#         fields = '__all__'  
#         labels = {
#             "rm_name": "Grade",
#         }

# def __init__(self, *args, **kwargs):
#     super().__init__(*args, **kwargs)
#     self.helper = FormHelper()
#     self.helper.form_method = 'post'
#     self.helper.add_input(Submit('submit', 'Save'))

# class FinishedGoodsForm(forms.ModelForm):
#     class Meta:
#         model = FinishedGoods
#         fields = '__all__'  
#         labels = {
#             "fg_name": "Grade",
#         }

# def __init__(self, *args, **kwargs):
#     super().__init__(*args, **kwargs)
#     self.helper = FormHelper()
#     self.helper.form_method = 'post'
#     self.helper.add_input(Submit('submit', 'Save'))