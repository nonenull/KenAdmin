# coding=utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

@login_required
def homepage(request):
    return render(request, 'platform/index.html')
