import csv

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .models import DataElement


EXPORT_BASENAME = "uscdi-v3.1-data-elements"


def _data_elements():
    return DataElement.objects.select_related(
        "domain", "data_class", "use_case"
    ).order_by("data_class__name", "data_element", "code")


def _split_urls(value):
    return [url.strip() for url in (value or "").split(",") if url.strip()]


def _download_filename(extension):
    return f"{EXPORT_BASENAME}-{timezone.localdate().isoformat()}.{extension}"


@login_required
@require_GET
def uscdi_index(request):
    data_elements = list(_data_elements())
    rows = [
        {
            "element": element,
            "ig_urls": _split_urls(element.fhir_associated_ig_or_profile_urls),
            "us_core_urls": _split_urls(
                element.fhir_associated_us_core_profile_urls
            ),
        }
        for element in data_elements
    ]
    context = {
        "rows": rows,
        "total_count": len(rows),
        "mapped_count": sum(bool(element.mm_name) for element in data_elements),
        "data_classes": sorted(
            {element.data_class.name for element in data_elements},
            key=str.casefold,
        ),
    }
    context["unmapped_count"] = context["total_count"] - context["mapped_count"]
    return render(request, "uscdi/index.html", context)


@login_required
@require_GET
@never_cache
def export_to_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="{_download_filename("csv")}"'
    )
    # A UTF-8 BOM keeps spreadsheet applications from misreading non-ASCII text.
    response.write("\ufeff")
    writer = csv.DictWriter(response, fieldnames=DataElement.export_field_names())
    writer.writeheader()
    for element in _data_elements():
        writer.writerow(element.as_json)
    return response


@login_required
@require_GET
@never_cache
def export_to_json(request):
    content = [element.as_json for element in _data_elements()]
    response = JsonResponse(
        {"count": len(content), "content": content},
        json_dumps_params={"indent": 2},
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{_download_filename("json")}"'
    )
    return response
