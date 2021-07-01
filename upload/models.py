# class TextIndex(
#     fields=(),
#     name=None,
#     unique=False,
#     background=False,
#     partialFilterExpression=None,
#     weights=None, 
#     default_language='english', 
#     language_override=None, 
#     textIndexVersion=None)
# from djongo.models.indexes import TextIndex
import os
from djongo import models

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create your models here.
class Document(models.Model):
    FileName = models.CharField(max_length=255)
    FilePath = models.FilePathField(path = os.path.join(BASE_DIR,"media"))
    Content_HTML = models.TextField()
    Content_TEXT = models.TextField()
    Page_no = models.IntegerField()

    # class Meta:
    #     indexes = [
    #         TextIndex(fields=['Content_HTML'])
    #     ]

    def __str__(self):
        return self.FileName