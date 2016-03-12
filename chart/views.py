import time
from django.shortcuts import render_to_response
from .models import DataPoint


def linechart(request):
    """
    linewithfocuschart page
    """
    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"},
                   "date_format": tooltip_date}
    template_chartdata = {
        'x': [],
        'model_column1': "bedroom_temperature", #model field name
        'model_column2': "bedroom_humidity" #model field name
    }
    series = {}
    i = 1
    #Create a mapping between series and model_column.
    #{y1: bedroom_temperature, ...}
    chartdata = {}
    for key, val in template_chartdata.iteritems():
        chartdata[key] = val
        if key == "model_column%s" %(str(i), ):
            series[key] = chartdata["model_column%s" %(str(i), )]
            chartdata["name%s" % (str(i), )] = DataPoint._meta.get_field(series[key]).verbose_name
            chartdata["y%s" % (str(i), )] = []
            chartdata["extra%s" % (str(i), )] = extra_serie
            i += 1

    print chartdata
    points = DataPoint.objects.order_by('datetime')
    if len(points) > 0:
        for point in points:
            point_epoch_ms = int(time.mktime(point.datetime.timetuple())) * 1000
            point_ok = True
            for key, val in chartdata.iteritems():
                if "model_column" in key and not point._meta.get_field(val):
                    point_ok = False
            if point_ok:
                chartdata["x"].append(point_epoch_ms)
                for key, val in series.iteritems():
                    print "%s : %s: %s" %(key, val, getattr(point, val))
                    if True:
                        print chartdata[key]
                        chartdata[key].append(getattr(point, val))

    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        'extra': {
            'x_is_date': True,
            'x_axis_format': "%d %b %Y %H"
        }
    }
    return render_to_response('chart/linechart.html', data)
