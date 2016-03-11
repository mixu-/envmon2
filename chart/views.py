# Create your views here.
import random
import time
from django.shortcuts import render_to_response
from .models import IndoorDataPoint


def linechart(request):
    """
    linewithfocuschart page
    """
    points = IndoorDataPoint.objects.order_by('datetime')
    start_time = IndoorDataPoint.objects.order_by('datetime')[:1][0].datetime
    start_epoch_ms = int(time.mktime(start_time.timetuple())) * 1000

    xdata = [int(time.mktime(d.datetime.timetuple())) * 1000 for d in points]
    ydata = [d.indoor_temperature for d in points]
    ydata2 = [d.indoor_humidity for d in points]

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"},
                   "date_format": tooltip_date}
    chartdata = {
        'x': xdata,
        'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie,
        'name2': 'series 2', 'y2': ydata2, 'extra2': extra_serie
    }
    charttype = "lineWithFocusChart"
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'extra': {
            'x_is_date': True,
            'x_axis_format': "%d %b %Y %H"
        }
    }
    return render_to_response('chart/linechart.html', data)
