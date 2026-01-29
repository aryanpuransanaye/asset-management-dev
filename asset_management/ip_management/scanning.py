# from celery import shared_task
from .models import IPManage, DiscoveredAsset, ScanHistory 
import nmap
from itertools import chain
from django.shortcuts import get_object_or_404
from hardware.models import Hardware
from software.models import Software
from services.models import Services
from places_and_areas.models import PlacesAndArea
from infrastructure_assets.models import InfrastructureAssets
from intangible_assets.models import IntangibleAsset
from supplier.models import Supplier
from data_and_information.models import DataAndInformation
from .serializers import CreateScannedAssetSerializer

# @shared_task
def perform_scan_task(ip_id, user, access_level):
  
    selected_range = get_object_or_404(IPManage, id=ip_id)
    ip_target = f'{selected_range.ipaddress}/{selected_range.subnet}'

    scan_record, _ = ScanHistory.objects.get_or_create(
        network_range__id=ip_id, 
        defaults={'status': 'running', 'user': user}
    )
    scan_record.network_range = selected_range
    scan_record.status = 'running'
    scan_record.save()

    models_with_ip = [
        DiscoveredAsset, DataAndInformation, Software,
        Hardware, Services, PlacesAndArea, InfrastructureAssets,
        IntangibleAsset, Supplier
    ]
    existing_ips = set(
        ip for ip in chain.from_iterable(
            m.objects.values_list('ipaddress', flat=True)
            for m in models_with_ip
        ) if ip
    )
    
    nm = nmap.PortScanner()
    try:
        nm.scan(hosts=ip_target, arguments='-sn -T4')
    except Exception as e:
        scan_record.status = 'failed'
        scan_record.error_message = str(e)
        scan_record.save()
        return

    alive_hosts = [
        ip for ip in nm.all_hosts()
        if nm[ip]['status']['state'] == 'up' and ip not in existing_ips
    ]

    if not alive_hosts:
        scan_record.status = 'no new ip founed'
        scan_record.save()
    
    new_assets_data = []
    for ip in alive_hosts:
        try:
            nm.scan(hosts=ip, arguments='-O -T4')
            host = nm[ip]
        except Exception:
            continue
        
        mac = host.get('addresses', {}).get('mac', None)
        os_type = None
        vendor = None
        osinfo = host.get('osmatch', [])
        if osinfo:
            os_type = osinfo[0].get('name', None)
            osclass = osinfo[0].get('osclass', [])
            if osclass:
                vendor = osclass[0].get('vendor', None)
        if mac is not None and mac in host.get('vendor', {}):
            vendor = host['vendor'][mac]
     
        asset_data = {
            'network_range': selected_range.id,
            'ipaddress': ip,
            'mac': mac,
            'os': os_type,
            'vendor': vendor,
            'access_level': access_level.id,
            'user': user.id
        }
        new_assets_data.append(asset_data)

    
    serializer = CreateScannedAssetSerializer(data=new_assets_data, many=True)
    if serializer.is_valid():
        print(serializer.data)
        serializer.save()
    else:
        print(serializer.errors)
    
    print(len(new_assets_data))

    scan_record.status = 'finished'
    scan_record.result_count = len(new_assets_data)
    scan_record.save()