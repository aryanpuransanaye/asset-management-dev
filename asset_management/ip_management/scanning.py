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
from itertools import chain
from django.shortcuts import get_object_or_404
from celery import shared_task



####celery####
@shared_task
def start_scanning_celery(ip_id, user_id, access_level_id, scan_id=None):
    """Start scanning for the given ip range.

    If `scan_id` is provided, ensure the task operates on that exact ScanHistory
    record and exit early if it's missing or not in `running` state. This
    prevents duplicate/ambiguous processing when multiple tasks are queued.
    """
    selected_range = get_object_or_404(IPManage, id=ip_id)
    ip_target = f"{selected_range.ipaddress}/{selected_range.subnet}"

    scan_record = None
    if scan_id:
        scan_record = ScanHistory.objects.filter(id=scan_id).first()
        # if the scan record isn't found or doesn't match expected range/status, stop
        if not scan_record or scan_record.network_range_id != ip_id or scan_record.status != 'running':
            return 0
    else:
        # fallback for older callers: use latest scan history for the range
        scan_record = ScanHistory.objects.filter(network_range_id=ip_id).order_by('-created_at').first()
        if not scan_record:
            scan_record = ScanHistory.objects.create(
                network_range_id=ip_id,
                status='running',
                user_id=user_id
            )
        else:
            scan_record.status = 'running'
            scan_record.user_id = user_id
            scan_record.save()
    
    models_with_ip = [
        DiscoveredAsset, DataAndInformation, Software,
        Hardware, Services, PlacesAndArea, InfrastructureAssets,
        IntangibleAsset, Supplier
    ]
    existing_ips = set(
        ip for ip in chain.from_iterable(
            m.objects.values_list('ipaddress', flat=True) for m in models_with_ip
        ) if ip
    )

    nm = nmap.PortScanner()
    try:
        nm.scan(hosts=ip_target, arguments='-sn -T4')
    except Exception as e:
        scan_record.status = 'failed'
        scan_record.error_message = str(e)
        scan_record.save()
        return 0

    # check for cancellation requested by user
    scan_record.refresh_from_db()
    if scan_record.status == 'canceled':
        scan_record.result_count = 0
        scan_record.save()
        return 0

    alive_hosts = [ip for ip in nm.all_hosts() if nm[ip]['status']['state'] == 'up' and ip not in existing_ips]

    if not alive_hosts:
        scan_record.status = 'no_new_ip'
        scan_record.save()
        return 0

    new_assets_data = []
    for ip in alive_hosts:
        # allow cancellation between hosts
        scan_record.refresh_from_db()
        if scan_record.status == 'canceled':
            # persist partial results count and stop
            scan_record.result_count = len(new_assets_data)
            scan_record.save()
            return 0

        try:
            nm.scan(hosts=ip, arguments='-O -T4')
            host = nm[ip]
        except Exception:
            continue

        mac = host.get('addresses', {}).get('mac')
        os_type = None
        vendor = None
        osinfo = host.get('osmatch', [])
        if osinfo:
            os_type = osinfo[0].get('name')
            osclass = osinfo[0].get('osclass', [])
            if osclass:
                vendor = osclass[0].get('vendor')
        if mac is not None and mac in host.get('vendor', {}):
            vendor = host['vendor'][mac]

        asset_data = {
            'network_range': selected_range.id,
            'ipaddress': ip,
            'mac': mac,
            'os': os_type,
            'vendor': vendor,
            'access_level': access_level_id,
            'user': user_id
        }
        new_assets_data.append(asset_data)

    serializer = CreateScannedAssetSerializer(data=new_assets_data, many=True)
    if serializer.is_valid():
        serializer.save()
    else:
        scan_record.status = 'failed'
        scan_record.error_message = str(serializer.errors)
        scan_record.save()
        return 0

    # if scan was canceled while adding assets, do not overwrite canceled state
    scan_record.refresh_from_db()
    if scan_record.status != 'canceled':
        scan_record.status = 'finished'
        scan_record.result_count = len(new_assets_data)
        scan_record.error_message = str(serializer.errors)
        scan_record.save()


####threading#####
def start_scan_thread(ip_id, user, access_level):
  
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

    # check for cancellation requested by user
    scan_record.refresh_from_db()
    if scan_record.status == 'canceled':
        scan_record.result_count = 0
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
        # allow cancellation between hosts
        scan_record.refresh_from_db()
        if scan_record.status == 'canceled':
            scan_record.result_count = len(new_assets_data)
            scan_record.save()
            return

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

    scan_record.refresh_from_db()
    if scan_record.status != 'canceled':
        scan_record.status = 'finished'
        scan_record.result_count = len(new_assets_data)
        scan_record.save()