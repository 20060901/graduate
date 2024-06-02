from django import forms

from app01.models import Class


class BootStrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            # 字段中有属性，保留原来的属性，没有属性，才增加。
            if field.widget.attrs:
                if name == 'bid' or name == 'rid' or name == 'status':
                    field.widget.attrs["readonly"] = "readonly"
                    continue
                field.widget.attrs.update({
                    " ": "required",
                    "class": "form-control",
                    "placeholder": field.label
                })

            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label
                }




class BootStrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环ModelForm中的所有字段，给每个字段的插件设置
        for name, field in self.fields.items():
            # 字段中有属性，保留原来的属性，没有属性，才增加。
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
                field.widget.attrs["autocomplete"] = 'off'
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label,
                    "autocomplete": 'off'
                }
