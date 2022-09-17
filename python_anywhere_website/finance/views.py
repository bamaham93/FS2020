from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from logic.queries import TransactionQueries

# Create your views here.
def index(request):
    """ """
    context = {}
    return render(request, "finance/index.html", context)


@login_required
def transactions_by_month(request, month: int = 0):
    """ """
    transaction_query = TransactionQueries()

    this_month = date.today().month
    this_year = date.today().year

    context = {
        "transactions": transaction_query.get_by_month(month=this_month, year=this_year)
    }
    return render(request, "finance/transactions_by_month.html", context)
