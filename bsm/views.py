from django.shortcuts import render
from  bsm.bopm2bsmengine import BopmData
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.


def bsm_home(request):
    bopm = parseCompute(request)
    bopmdata_json = json.dumps(bopm.as_json(), cls=DjangoJSONEncoder)
    return render(request, 'blackschole.html', {"bopmdata": bopm, "bopmdata_json": bopmdata_json})

def parseCompute(request):
    stock_price = float(request.GET.get('stock',50))
    strick_price = float(request.GET.get('strike',50))
    rate = float(request.GET.get('rate',10))
    volatility = float(request.GET.get('volatility',30))
    maturity = float(request.GET.get('maturity', 1))
    op_type = int(request.GET.get('op_type', 0))
    op_nat = int(request.GET.get('op_nat', 0))
    step_unit = request.GET.get('step_unit', 'm')
    step_value = float(request.GET.get('step_value', 0.1))
    b= BopmData(stock_price, strick_price, rate, volatility,maturity, step_value,step_unit, op_type = op_type,op_nat = op_nat)
    b.compute()
    return b

