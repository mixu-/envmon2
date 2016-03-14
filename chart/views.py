import time
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from .models import DataPoint
import re

class InvalidRequest(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(InvalidRequest, self).__init__(message)

@csrf_exempt
def insert_data(request):
    """Push measurement data to database using POST requests."""
    try:
        b_temp = float(request.POST['bedroom_temperature'].replace(",", "."))
        b_hum = float(request.POST['bedroom_humidity'].replace(",", "."))
    except (MultiValueDictKeyError, ValueError):
        return HttpResponseBadRequest("ERROR: Missing or invalid data!")
    datapoint = DataPoint(datetime=timezone.now(),
                          bedroom_temperature=b_temp,
                          bedroom_humidity=b_hum)
    datapoint.save()
    return HttpResponse("OK")

def linechart(request):
    """
    linewithfocuschart page
    """
    temp_tooltip = {"tooltip": {"y_start": "Temperature: ", "y_end": "C"},
                    "date_format": "%d %b %Y %H:%M:%S %p"}

    hum_tooltip = {"tooltip": {"y_start": "Temperature: ", "y_end": "C"},
                   "date_format": "%d %b %Y %H:%M:%S %p"}

    series_map = ["bedroom_temperature", "bedroom_humidity"] #model field names
    series_tooltips = [temp_tooltip, hum_tooltip]
    chartdata = {'x': []}

    i = 1
    for field_name in series_map:
        chartdata["y%s" % (str(i), )] = []
        chartdata["name%s" % (str(i), )] = DataPoint._meta.get_field(field_name).verbose_name
        chartdata["extra%s" % (str(i), )] = series_tooltips[i-1]
        i += 1

    #Chartdata has now been initialized with fields defined in series_map.
    points = DataPoint.objects.order_by('datetime')
    if len(points) > 0:
        for point in points:
            point_epoch_ms = int(time.mktime(point.datetime.timetuple())) * 1000
            #Check that the point has all the data points being plotted.
            #If not, skip the data point.
            point_ok = True
            for key, val in chartdata.iteritems():
                if not str(key).startswith("y"):
                    continue
                #This will throw a ValueError if you screw up series_map.
                y_nr = int(re.search(r'\d+', key).group())
                if not point._meta.get_field(series_map[y_nr-1]):
                    point_ok = False
            if point_ok: #OK to add datapoint to chart and all series.
                chartdata["x"].append(point_epoch_ms)
                for j in xrange(len(series_map)):
                    chartdata["y%s" % (str(j+1), )].append(getattr(point, series_map[j]))

    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        'extra': {
            'x_is_date': True,
            'x_axis_format': "%d.%m.%Y %H:%M"
        }
    }
    return render_to_response('chart/linechart.html', data)
