from __future__ import unicode_literals

import matplotlib

matplotlib.use("Agg")
from app.hull_white import HWCalculator
from django.http import JsonResponse
from django.shortcuts import render
import mpld3
from pylab import *


def base_home(request):
    return render(request, 'base_home.html')

def home(request):
    hwc = parseRequest(request=request)
    if request.POST:
        if len(hwc.rates) >= hwc.nbr_steps +1 :
            hwc.execute()
            graph = draw_data(hwc)
            return render(request, 'home.html', {"hw": hwc, 'graph': graph})
        else :
            return render(request, 'home_error.html', {"hw": hwc})
    return render(request, 'home_parent.html', {"hw": hwc})


def auto_generate(request):
    hwc = parseRequest(request=request)
    hwc.rates = []
    for i in range(0, hwc.nbr_steps + 1, 1):
        hwc.rates.append(0.08 - 0.05 * math.exp(-0.18 * i))
    hwc.execute()
    graph = draw_data(hwc)
    return render(request, 'test.html', {"hw": hwc, 'graph': graph})

def documentation(request):
    return render(request, 'document.html')


def about(request):
    return render(request, 'about.html')


def api_hullwhite(request):
    hwc = parseRequest(request=request)
    if len(hwc.rates) >= hwc.nbr_steps + 1:
        hwc.execute()
    return JsonResponse(hwc.as_json())

def api_hullwhite_auto(request):
    hwc = HWCalculator()
    hwc.maturity = 5
    hwc.alpha = 0.1
    hwc.volatility = 0.014
    hwc.period ="year"
    hwc.nbr_steps = 5
    hwc.rates = []
    for i in range(0, 6, 1):
        hwc.rates.append(0.08 - 0.05 * math.exp(-0.18 * i))
    hwc.execute()
    return JsonResponse(hwc.as_json())


def draw_data(hw):
    fig, ax = plt.subplots()
    N = hw.nbr_steps
    min_rate = hw.steps[0].nodes[0].rate
    max_rate = min_rate
    for i in range(0, N - 1, 1):
        top_node = min(i, hw.jmax)
        for j in range(-top_node, top_node + 1, 1):
            node = hw.steps[i].nodes[j + top_node]
            if node.rate < min_rate:
                min_rate = node.rate

            if node.rate > max_rate:
                max_rate = node.rate

            up = hw.steps[i + 1].nodes[node.j_up + top_node]
            m = hw.steps[i + 1].nodes[node.j_m + top_node]
            dw = hw.steps[i + 1].nodes[node.j_d + top_node]
            plot([i, i + 1], [node.rate * 100, up.rate * 100])
            plot([i, i + 1], [node.rate * 100, m.rate * 100])
            plot([i, i + 1], [node.rate * 100, dw.rate * 100])

    # get_min_rate

    ax.set_xlim(0, N + 1)
    ax.set_ylim(-min_rate * 100 - 1, max_rate * 100 + 1)
    ax.set_xlabel('Maturity')
    ax.set_ylabel('Rate')
    ax.set_title('Hull White interest rate')
    ax.grid(True)
    html_fig = mpld3.fig_to_html(fig, template_type='general')
    plt.close(fig)
    return html_fig


def parseRequest(request):
    hwc = HWCalculator()
    try:
        maturity = math.fabs(float(request.POST.get('maturity')))
        if maturity < 0.01 or maturity > 100:
            maturity = 5
    except:
        maturity = 5

    hwc.maturity = maturity

    try:
        alpha = math.fabs(float(request.POST.get('alpha')))
        if alpha < 0.001 or alpha > 100:
            alpha = 0.1
    except:
        alpha = 0.1

    hwc.alpha = alpha

    try:
        volatility = math.fabs(float(request.POST.get('volatility')))
        if volatility < 0.0 or volatility > 100:
            volatility = 0.01
    except:
        volatility = 0.01

    hwc.volatility = volatility
    period_name = request.GET.get('period','year')
    period = get_period_value(period_name)
    hwc.nbr_steps = int(maturity * period)
    hwc.period = period_name
    rates_p = request.POST.getlist("rate")
    rate_float = []
    for item in rates_p:
        try:
            rate_float.append(double(item))
        except:
            pass
    hwc.rates = rate_float
    return hwc

def get_period_value(period_param):
    period = str(period_param)
    if period.lower().startswith('d'):
        return 250
    if period.lower().startswith('w'):
        return 52
    if period.lower().startswith('m'):
        return 12
    if period.lower().startswith('s'):
        return 2
    if period.lower().startswith('q'):
        return 4
    return 1
