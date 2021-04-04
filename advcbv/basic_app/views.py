from django.shortcuts import render
from django.views.generic import View,TemplateView,ListView,DetailView
from django.http import HttpResponse
from . import models
# Create your views here.

class CBView(View):
    def get(self,request):
        return HttpResponse("CLASS BUILD VIEWS IS COOL!!!")

class SchoolListView(ListView):
    context_object_name='schools'
    model= models.School
    
class SchoolDetailView(DetailView):
    
    context_object_name='school_detail'
    model=models.School
    template_name='basic_app/school_detail.html'


class IndexView(TemplateView):
    template_name='index.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['injectme']='BASIC_INJECTION'
        return context
