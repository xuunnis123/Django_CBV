from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
# Create your views here.

class CBView(View):
    def get(self,request):
        return HttpResponse("CLASS BUILD VIEWS IS COOL!!!")