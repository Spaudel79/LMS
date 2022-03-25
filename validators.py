from django.db.models import FileField
# from django.forms import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


class ModifiedFileField(FileField):

    def __init__(self, *args, **kwargs):
        print("inside init")
        self.file_type = kwargs.pop("file_type", [])
        self.max_file_size = kwargs.pop("max_file_size", 0)

        super(ModifiedFileField, self).__init__(*args, **kwargs)


    #     return data

    def __call__(self, *args, **kwargs):
        print("iam call")
        size = self.max_file_size
        if int(size / 1048576) > 100:
            raise ValidationError("Max file size is 100 MB.")
        pass
