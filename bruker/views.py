from __future__ import annotations

from django.shortcuts import render
import io
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.http import require_POST


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")

@require_POST
def ingest(request: HttpRequest) -> JsonResponse:
    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided."}, status=400)

    uploaded = request.FILES["file"]

    # Example: stream text
    text = io.TextIOWrapper(uploaded.file, encoding="utf-8", newline="")
    ingested = 0
    # for line in text:
    #     ingest_line(line)  # your ingestion logic
    #     ingested += 1

    return JsonResponse({"filename": uploaded.name, "ingested_lines": ingested})
