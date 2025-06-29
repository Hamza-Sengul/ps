from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Table, Pricing, Product, Session, SessionItem
from .forms import AddItemForm

def index(request):
    tables = Table.objects.all()
    products = Product.objects.all()
    pricing = Pricing.objects.all()
    return render(request, 'salon/index.html', {
        'tables': tables,
        'products': products,
        'pricing': pricing,
    })

def start_session(request, table_id):
    table = get_object_or_404(Table,id=table_id)
    if table.is_open:
        return JsonResponse({'status':'error','message':'Masa zaten açık.'})
    # GET param’dan controllers
    try:
        cnt = int(request.GET.get('controllers',2))
    except:
        cnt = 2
    sess = Session.objects.create(table=table, controllers=cnt)
    table.is_open = True
    table.save()
    return JsonResponse({
      'status':'ok',
      'start_time': sess.start_time.isoformat(),
      'controllers': cnt
    })

def add_item(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    session = table.session_set.filter(end_time__isnull=True).last()
    form = AddItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and session:
        product = form.cleaned_data['product']
        SessionItem.objects.create(session=session, product=product)
        return JsonResponse({'status': 'ok', 'total': session.total_price})
    return JsonResponse({'status': 'error'})

def close_session(request, table_id):
    table = get_object_or_404(Table,id=table_id)
    sess  = table.session_set.filter(end_time__isnull=True).last()
    if not sess:
        return JsonResponse({'status':'error'})
    sess.end_time = timezone.now()
    sess.total_amount = sess.total_price
    sess.save()
    table.is_open = False
    table.save()
    return JsonResponse({'status':'ok','total':float(sess.total_amount)})



# salon/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from .models import Table, Session, SessionItem, Pricing, Product
import datetime

def daily_log(request):
    # GET ile ?date=YYYY-MM-DD alınır, yoksa bugünkü tarih
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected = timezone.localdate()
    else:
        selected = timezone.localdate()

    # O tarihte kapanmış tüm oturumlar
    sessions = Session.objects.filter(end_time__date=selected).order_by('end_time')
    total = sessions.aggregate(sum=Sum('total_amount'))['sum'] or Decimal('0')

    return render(request, 'logs.html', {
        'sessions': sessions,
        'total': total,
        'selected_date': selected.isoformat(),
    })
