import datetime as dt


def year(request):
    this_year = dt.datetime.today().year
    """
    Добавляет переменную с текущим годом.
    """
    return {
      'year':this_year
    }
