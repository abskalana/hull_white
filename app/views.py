from __future__ import unicode_literals

import matplotlib

matplotlib.use("Agg")
from app.hull_white import HWCalculator
from django.http import JsonResponse
from django.shortcuts import render
import mpld3
from pylab import *


def home(request):
    hwc = HWCalculator()
    if request.POST:
        parseRequest(request=request, hwc = hwc)
        if len(hwc.rates) >= hwc.nbr_steps +1 :
            hwc.execute()
            graph = draw_data(hwc)
            return render(request, 'home.html', {"hw": hwc, 'graph': graph})
        else :
            return render(request, 'home_error.html', {"hw": hwc})
    hwc.maturity = 5
    hwc.alpha = 0.1
    hwc.period = 'year'
    hwc.volatility = 0.01
    return render(request, 'home_parent.html', {"hw": hwc})

def auto_generate(request):
    hwc = HWCalculator()
    hwc.maturity = 18
    hwc.alpha = 0.1
    hwc.period = 'year'
    hwc.volatility = 0.01
    hwc.nbr_steps = 18
    for i in range(len(hwc.rates), hwc.nbr_steps + 2, 1):
        hwc.rates.append(0.08 - 0.05 * math.exp(-0.18 * i))

    if request.POST:
         parseRequest(request=request, hwc = hwc)
         if len(hwc.rates) < hwc.nbr_steps + 1:
           for i in range(len(hwc.rates), hwc.nbr_steps + 2, 1):
                hwc.rates.append(0.08 - 0.05 * math.exp(-0.18 * i))

    hwc.execute()
    graph = draw_data(hwc)
    return render(request, 'test.html', {"hw": hwc, 'graph': graph})


def documentation(request):
    return render(request, 'document.html')


def about(request):
    return render(request, 'about.html')


def api_hullwhite(request):
    hwc = HWCalculator()
    hwc.maturity = 10
    hwc.alpha = 0.1
    hwc.volatility = 0.014
    hwc.period = "year"
    hwc.nbr_steps = 10
    hwc.rates = []
    parseRequest(request=request,hwc =  hwc)
    if len(hwc.rates) >= hwc.nbr_steps + 1:
        hwc.execute()
    return JsonResponse(hwc.as_json())

def api_hullwhite_auto(request):
    hwc = HWCalculator()
    hwc.maturity = 5
    hwc.alpha = 0.1
    hwc.volatility = 0.014
    hwc.period = "year"
    hwc.nbr_steps = 5
    hwc.rates = []
    for i in range(0, hwc.nbr_steps, 1):
        hwc.rates.append(0.08 - 0.05 * math.exp(-0.18 * i))

    try:
        parseRequest(request=request, hwc = hwc)
        if len(hwc.rates) < hwc.nbr_steps + 1:
            for i in range(len(hwc.rates), hwc.nbr_steps + 2, 1):
                hwc.rates.append(0.08 - 0.05 * math.exp(-0.18 * i))
    except:
        pass

    hwc.execute()
    return JsonResponse(hwc.as_json())


def draw_data(hw):
    fig, ax = plt.subplots()
    fig.set_size_inches(14, 7)
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
            if N< 8:
                ax.annotate(node.id, xy=(i, node.rate*100), xytext=(i * 0.95, node.rate*100 * 0.90), fontsize=13, color='blue')

    for node in hw.steps[N-1].nodes:
        if N < 8:
            ax.annotate(node.id, xy=(N-1, node.rate * 100), xytext=((N-1) * 0.95, node.rate * 100 * 0.90), fontsize=13,color='blue')

    # get_min_rate


    ax.set_xlabel('Maturity')
    ax.set_ylabel('Rate')
    ax.set_title('Hull White trinomial')
    ax.grid(True)
    html_fig = mpld3.fig_to_html(fig, template_type='general')
    plt.close(fig)
    return html_fig


def parseRequest(request,hwc):
    print(request.POST.get('alpha', '0.1'))
    try:
        hwc.alpha = math.fabs(float(request.POST.get('alpha', 0.1)))
    except :
        pass

    try:
        hwc.volatility = math.fabs(float(request.POST.get('volatility', 0.01)))
    except :
        pass

    try:
        hwc.maturity = math.fabs(float(request.POST.get('maturity', 20.0)))
    except :
        pass

    try:
        hwc.period= request.POST.get('period','year')
        period = get_period_value(hwc.period)
        hwc.nbr_steps = int(hwc.maturity * period)
    except :
        pass

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
