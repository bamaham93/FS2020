from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date

try:
    from logic.queries import TransactionQueries
except ModuleNotFoundError:
    pass


# Create your views here.
def index(request):
    """ """
    context = {}
    return render(request, "finance/index.html", context)


@login_required
def transactions_by_month(request, month: int, year: int):
    """ """
    transaction_query = TransactionQueries()

    this_month = date.today().month
    this_year = date.today().year

    context = {
        "transactions": transaction_query.get_by_month(month=month, year=year),
        "year": this_year,
        "month": month,
    }
    return render(request, "finance/transactions_by_month.html", context)
