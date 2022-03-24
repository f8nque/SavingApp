from django.db import models
from django.conf import settings
# Create your models here.
class Credit(models.Model):
    credit_date = models.DateField()
    credit_agency= models.CharField(max_length=128)
    amount = models.IntegerField()
    credit_service_date= models.DateField()
    comment = models.TextField(null=True,blank=True)
    paid = models.BooleanField(default=False)
    voided = models.IntegerField(default=0)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created= models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.credit_date}-{self.credit_agency}-{self.amount}"


class CreditService(models.Model):
    debt_id = models.ForeignKey(Credit,on_delete=models.CASCADE)
    service_date= models.DateField()
    amount = models.IntegerField()
    comment = models.TextField(null=True,blank=True)
    voided = models.IntegerField(default=0)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created= models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

