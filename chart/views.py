import time, datetime
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from .models import DataPoint
from django.db.models import Avg, Min, Max
import copy

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

    tooltip = {"tooltip": {"y_start": None, "y_end": None},
               "date_format": "%d %b %Y %H:%M:%S %p"}

    series_dict = {
        "bedroom_temperature": {
            "type": "Temperature",
            "unit": "C"
        },
        "bedroom_humidity": {
            "type": "Humidity",
            "unit": "%%RH"
        }
    }
    chartdata = {'x': []}
    i = 1
    for field_name, value in series_dict.iteritems():
        tmp_tooltip = copy.deepcopy(tooltip)
        chartdata["y%s" % (str(i), )] = []
        chartdata["name%s" % (str(i), )] = \
            DataPoint._meta.get_field(field_name).verbose_name

        tmp_tooltip["tooltip"]["y_start"] = value["type"] + " "
        tmp_tooltip["tooltip"]["y_end"] = value["unit"]
        chartdata["extra%s" % (str(i), )] = tmp_tooltip
        i += 1

    #Chartdata has now been initialized with fields defined in series_map.
    points = DataPoint.objects.order_by('datetime')
    accurate_period_ms = 1000 * 3600 * 2 #2 hours of accurate data.
    previous_epoch_ms = 0
    point_interval = 1000 * 900 #Only show a data point every X ms (900s)
    for point in points:
        point_epoch_ms = time.mktime(point.datetime.timetuple()) * 1000
        now_epoch_ms = time.mktime(timezone.now().timetuple()) * 1000
        if point_epoch_ms < now_epoch_ms - accurate_period_ms and \
                point_epoch_ms - previous_epoch_ms < point_interval:
            continue
        previous_epoch_ms = point_epoch_ms
        #Check that the point has all the data points being plotted.
        #If not, skip the data point.
        point_ok = True
        for key, _ in chartdata.iteritems():
            if not str(key).startswith("y"):
                continue
            for serie in series_dict:
                if not point._meta.get_field(serie):
                    point_ok = False
        if point_ok: #OK to add datapoint to chart and all series.
            chartdata["x"].append(point_epoch_ms)
            j=0
            for key, val in series_dict.iteritems():
                chartdata["y%s" % (str(j+1), )].append(\
                    getattr(point, key))
                j += 1


    ############ Summary table starts here ############
    today = timezone.now().date()
    week_ago = today - datetime.timedelta(days=7)
    one_day_metrics = {}
    week_metrics = {}
    for field_name in series_dict:

        one_day_metrics[field_name] = {}
        one_day_metrics[field_name] = DataPoint.objects.filter(
            datetime__gt=today).aggregate(avg=Avg(field_name),
                                          min=Min(field_name),
                                          max=Max(field_name))
        one_day_metrics[field_name]["avg"] = \
            round(one_day_metrics[field_name]["avg"], 1)
        one_day_metrics[field_name]["name"] = DataPoint._meta.get_field(field_name).verbose_name

        week_metrics[field_name] = {}
        week_metrics[field_name] = DataPoint.objects.filter(
            datetime__gt=week_ago).aggregate(avg=Avg(field_name),
                                             min=Min(field_name),
                                             max=Max(field_name))
        week_metrics[field_name]["avg"] = \
            round(week_metrics[field_name]["avg"], 1)
        week_metrics[field_name]["name"] = DataPoint._meta.get_field(field_name).verbose_name


    ###### Piece things together and render. ##########
    data = {
        'charttype': "lineWithFocusChart",
        'chartdata': chartdata,
        'extra': {
            'x_is_date': True,
            'x_axis_format': "%d.%m.%Y %H:%M"
        },
        "one_day_metrics": one_day_metrics,
        "week_metrics": week_metrics,
    }

    return render(request, 'chart/linechart.html', data)
