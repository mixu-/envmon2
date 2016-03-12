import time
from django.shortcuts import render_to_response
from .models import DataPoint
import re

def linechart(request):
    """
    linewithfocuschart page
    """
    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"},
                   "date_format": tooltip_date}

    series_map = ["bedroom_temperature", "bedroom_humidity"] #model field names
    chartdata = {'x': []}

    i = 1
    for field_name in series_map:
        chartdata["y%s" % (str(i), )] = []
        chartdata["name%s" % (str(i), )] = DataPoint._meta.get_field(field_name).verbose_name
        chartdata["extra%s" % (str(i), )] = extra_serie
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
                    print series_map[j] + " " + str(getattr(point, series_map[j]))
                    chartdata["y%s" % (str(j+1), )].append(getattr(point, series_map[j]))

    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        'extra': {
            'x_is_date': True,
            'x_axis_format': "%d %b %Y %H"
        }
    }
    return render_to_response('chart/linechart.html', data)
