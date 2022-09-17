from django.db import models

# Create your models here.
class Category(models.Model):
    """ """

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Categories"


class Transaction(models.Model):
    """ """

    date = models.DateField()
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    is_income = models.BooleanField()
    is_reimbursement = models.BooleanField()
    notes = models.TextField()

    def __str__(self):
        return f"{self.amount}"
