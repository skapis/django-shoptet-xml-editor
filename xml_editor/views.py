from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Settings
from .utils import process_orders_xml, parse_receipt_xml, create_receipt_xml


@login_required(login_url='/auth/login')
def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    if request.method == 'POST':
        # Handle file upload
        uploaded_file = request.FILES['xml_file']
        if not uploaded_file.name.endswith('.xml'):
            messages.error(request, 'Prosím vyberte XML soubor.')
            return redirect('home')
        
        # read the file content
        file_content = uploaded_file.read()
        # load settings from the database
        settings = Settings.objects.all()
        try:
            modified_xml = process_orders_xml(
                xml_data=file_content,
                bank_id=settings.get(code='bank_id').value,
                account_no=settings.get(code='account_no').value,
                bank_code=settings.get(code='bank_code').value,
                const_symbol=settings.get(code='const_symbol').value,
                store_id=settings.get(code='store_id').value,
                feed_url=settings.get(code='feed_url').value,
                hash=settings.get(code='hash').value,
                eur_rate=settings.get(code='eur_rate').value
            )

            # Prepare response with XML file
            response = HttpResponse(modified_xml, content_type='application/xml; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="modified_{uploaded_file.name}"'
            return response

        except Exception as e:
            messages.error(request, f'Nepovedlo se zpracovat XML soubor: {e}')
            return redirect('home')
        
def receipts(request):
    if request.method == 'GET':
        # Fetch receipts from the database
        return render(request, 'receipts.html')
    if request.method == 'POST':
        # Handle file upload
        uploaded_file = request.FILES['xml_file']
        if not uploaded_file.name.endswith('.xml'):
            messages.error(request, 'Prosím vyberte XML soubor.')
            return redirect('receipts')
        
        # read the file content
        file_content = uploaded_file.read()
        
        # parse the XML file
        try:
            receipts = parse_receipt_xml(file_content)
            # Create a new XML file with the parsed data
            xml_data = create_receipt_xml(receipts)
            
            # Prepare response with XML file
            response = HttpResponse(xml_data, content_type='application/xml; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="parsed_{uploaded_file.name}"'
            return response
        except Exception as e:
            messages.error(request, f'Nepovedlo se zpracovat XML soubor: {e}')
            return redirect('receipts')
            


@login_required(login_url='/auth/login')
def settings(request):
    # get all settings from the database sorted by category
    settings = Settings.objects.all().order_by('category')    
    if request.method == 'GET':
        # Fetch settings from the database
        context = {
            'settings': settings
        }
        return render(request, 'settings.html', context)
    if request.method == 'POST':
        # get codes of settings
        codes = settings.values_list('code', flat=True)
        # get values from the form
        values = [{'code': code, 'value': request.POST.get(code)} for code in codes]
        # Update settings in the database
        for setting in settings:
            for value in values:
                if setting.code == value['code']:
                    setting.value = value['value']
                    setting.save()
        # Show success message
        messages.success(request, 'Nastavení úspěšně uloženo.')
        return redirect('settings')