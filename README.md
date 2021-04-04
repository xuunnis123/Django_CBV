# [Django] CBV-視圖類別(Class-based View)

目的：因為在這之前我們在 views 所撰寫的商業邏輯都單純只是一個function，雖然使用它就可以幫我們處理相當多的事情，但是他並不具備著 類別繼承 的特性

貼心的 Django 為了方便我們開發，都幫我們鋪好路了，提供了許多內建的 Class-Based Views，而我們只要去繼承它們，便能幫助我們完成相當多的事情

藉由覆寫(Overriding) 的方式，將函式導向的檢視(Function-based Views)，封裝成類別導向的檢視(Class-based Views)，不但具有物件導向(OOP)的優點外，Django在背後也幫我們做了許多的事情，讓程式碼的寫法能夠更加簡潔

種類：
```
Django ListView(清單檢視類別)
Django DetailView(內容檢視類別)
Django CreateView(新增檢視類別)
Django UpdateView(修改檢視類別)
Django DeleteView(刪除檢視類別)
```



##### 補充：*args, **kwargs
*args:會給tuple格式的參數
**kwargs：提供dictionary格式的參數

ex. **kwargs
```python=
def bar(**kwargs):
    for a in kwargs:
        print a,kwargs[a]
bar(name='test',age=27)
```
```
age 27
name test
```

ex. *args
```python=
def foo(*args):
    for a in args:
        print a
foo(1)

foo(1,2,3)
```
```
1

1
2
3
```
```as_view```是View類別以及所有繼承此類別的衍生類別都會有的類別方法
我們可以想像它是視圖類別的進入點
在URL配置檔中，一律要呼叫對應的視圖類別的```as_view```方法
```類別方法```是屬於類別的方法，不需要實體化的物件實例就可以呼叫和使用
但物件方法只能由實例來呼叫
而```as_view```方法會利用View類別(以及所有繼承此類別的衍生類別)中的物件方法dispatch方法來選擇適當的處理函式，例如當我們使用Http協定去GET某個URL頁面時，dispatch會幫我們選擇使用get方法來回應

```
   分類	                  說明
Generic View	一般、沒有特殊需求可使用視圖類別
Display View	與模型合作的視圖，經過簡單設定便可展示資料庫內容
Edit View	修改資料庫相關的視圖
```
## Generic View
```Mixin```:提供衍生類別藉由多重繼承來匯聚多個類別能力的基礎類別，它會Mix in to它的衍生類別

透過```django.views.generic```模組下的各種```Mixin```
能夠讓```View```類別變為擁有更多功能的新視圖類別
像是內建的```TemplateView```，```ListView```，```FormView```都是繼承了不同Mixin實作的功能
這些視圖類別皆放置在```django.views.generic```下，如果想找內建的視圖類別和Mixin只要到這裡找即可

---
### TemplateView
TemplateView可以根據參數給定的模板以及Context參數來填寫並回應該模板



原本函式：
```python=
def index(request):
    return render(request, 'index.html')
```
改成：
``` python=
from django.views.generic.base import View, TemplateView

class IndexView(TemplateView):
    template_name = 'index.html'
```
在```template_name```填入要使用的模板名稱
設定了這個變數後，```TemplateResponseMixin```會自動幫我們取得指定的模板
接著要設定模板中的request變量
利用```TemplateView```中的```ContextMixin```來設置，但我們就必須要覆寫get方法了

``` python=
class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['request'] = request
        return self.render_to_response(context)
```
讓我們的get方法多出```*args```, ```**kwargs```兩個參數，這是一個比較安全的寫法，這樣做可以保持這個函式的彈性
接著利用```ContextMixin```提供的```get_context_data```方法來取得context
並且幫這個context多設置request這個變量
最後利用```TemplateResponseMixin```提供的```render_to_response```來填寫模板並回應

這個方法必須要重新覆寫get方法，有點麻煩，我們可以這樣做:
```settings.py```中的```TEMPLATES```加入
```python=
'django.template.context_processors.request',
```
``` python=
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', # <-加入這行
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```
在處理器中加入request處理器的模組，如此一來request變量將會自動加入context中
這樣我們就不需要覆寫get方法了，因此可以把get方法整個拿掉也不會受影響


設置```urls.py```
```python=
path('',views.IndexView.as_view()),
```
## Display View
必須要有```model```的時候，這個屬性用來定義所要展示的model或表單


---
### ListView(清單檢視類別)
```ListView```可以展示某個資料庫模型裡的資料，有點像內建查詢功能一樣
將原本的
```views.py```
```python=
from django.contrib.auth.decorators import login_required
from restaurants.models import Restaurant, Food

@login_required
def list_restaurants(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants_list.html', locals())
```
改成
```python=
from django.views.generic.list import ListView
from restaurants.models import Restaurant, Food

class RestaurantsView(ListView):
    model = Restaurant
    template_name = 'restaurants_list.html'
    context_object_name = 'restaurants'
```
首先要指定一個要展示的資料庫模型給model
我們想展示```Restaurant```的資料，所以填入```Restaurant```
接著跟之前一樣使用```template_name```來指定使用的模板
如果只寫出模板名稱，那此類別所使用的```TemplateResponseMixin```會到每個應用下的```template```資料夾去尋找該模板，所以這邊填入```restaurants_list.html```即可

如果不設定template_name，那Django會去專案目錄下的templates中尋找名為```"應用名稱/模型名稱_list.html"```的模板

```context_object_name```用來為我們取出來的變量(一個模型資料的清單)取名
如果不設置此變數，則預設取出的資料清單會以```object_list```為名
比如說模板中的```{% for r in restaurants %}```就須改為```{% for r in object_list %}```

```ListView```還可以設置queryset，此變數會決定查詢的方式和結果
預設的queryset為```model.objects.all()```

依名稱排序
```python=
queryset = Restaurant.objects.order_by("-name")
```

原本這個頁面需要登入才能瀏覽
1. 直接在urls.py中使用裝飾器
    ```python=
    path('restaurants_list/', login_required(restaurants.views.RestaurantsView.as_view()))
    ```
2. 裝飾 ```dispatch```
   由於```dispatch```會將請求轉發    到各對應的函式
    所以```dispatch```被修飾過的視    圖類別，它所有支援的Http協定方法，都需要登入才能操作了
    ```python=
    from django.contrib.auth.decorators import login_required
    from django.utils.decorators import method_decorator
    from django.views.generic.list import ListView
    from restaurants.models import Restaurant, Food

    class RestaurantsView(ListView):
        model = Restaurant
        template_name = 'restaurants_list.html'
        context_object_name = 'restaurants'

        @method_decorator(login_required)
        def dispatch(self, request, *args, **kwargs):
            return super(RestaurantsView, self).dispatch(request, *args, **kwargs)
    ```
```method_decorator```這個裝飾器負責引入原本修飾函式的裝飾器給類別中的方法使用

---
### DetailView(內容檢視類別)
```DetailView```:用在單一筆資料的檢視頁面，如我們之前做的菜單，因為這個頁面呈現了其中一間餐廳的詳細資料，所以適合用```DetailView```來寫

1.
```python=
path('menu/', menu)
```
```python=
from django.shortcuts import render_to_response
from restaurants.models import Restaurant
from django.http import HttpResponseRedirect

def menu(request):
    if 'id' in request.GET and request.GET['id'] != '':
        restaurant = Restaurant.objects.get(id=request.GET['id'])
        return render_to_response('menu.html', locals())
    else:
        return HttpResponseRedirect("/restaurants_list/")
```
2.
```python=
re_path(r'menu/(\d{1,5})', menu),
```
```python=
def menu(request, id):
    if id:
        restaurant = Restaurant.objects.get(id=id)
        return render_to_response('menu.html', locals())
    else:
        return HttpResponseRedirect("/restaurants_list/")
```

都可以改成
```python=
from django.views.generic.detail import DetailView

class MenuView(DetailView):
    model = Restaurant
    template_name = 'menu.html'
    context_object_name = 'restaurant'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MenuView, self).dispatch(request, *args, **kwargs)
```
```DetailView```中的```model```代表的是我們要檢視的某一筆資料位於哪一個模型
其他設置和```ListView```都是一樣的
事實上我們可以用```ListView```來完成這件事，只要調整我們的queryset，不過```DetailView```提供了更特定的功能可以使用

使用```DetailView```就不必處理```GET方```法的判定，也不用處理```id```的取得，更不用親自去模型中查詢出要顯示的那筆資料
不過我們卻完全沒有告訴視圖我們要的是哪一筆資料，沒關係
因為```DetailView```預設會向URL討一個主鍵參數(也就是我們的餐廳id)，所以它內部預設會使用取得的主鍵來查詢出該筆資料，只是這個主鍵會以關鍵字參數的方式取得(而且預設名字為pk)

修改```urls.py```
```python=
re_path(r'menu/(?P<pk>\d+)', restaurants.views.MenuView.as_view())
```
如果不想用```pk```這個名字，只要覆寫```pk_url_kwarg```屬性即可
```python=
class MenuView(DetailView):
    model = Restaurant
    template_name = 'menu.html'
    context_object_name = 'restaurant'
    pk_url_kwarg = 'id'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MenuView, self).dispatch(request, *args, **kwargs)
```
在```DetailView```也可以藉由覆寫get方法來完成網頁重導的動作
``` python=
from django.http import HttpResponseRedirect, Http404

class MenuView(DetailView):
    model = Restaurant
    template_name = 'menu.html'
    context_object_name = 'restaurant'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MenuView, self).dispatch(request, *args, **kwargs)

    def get(self, request, pk, *args, **kwargs):
        try:
            return super(MenuView, self).get(self, request, pk=pk, *args, **kwargs)
        except Http404:
            return HttpResponseRedirect('/restaurants_list/')


```
一旦餐廳的```id```不是合法的，將會取不到資料，此時會導致```Http404```的錯誤，所以利用```try/catch```來接這個錯誤

## EditView
這類的視圖是要用來與使用者互動的，它能透過發送表單，新增、修改、刪除資料庫的內容

### FormView
``` python=
def comment(request, id):
    if id:
        r = Restaurant.objects.get(id=id)
    else:
        return HttpResponseRedirect("/restaurants_list/")
    if request.POST:
        f = CommentForm(request.POST)
        if f.is_valid():
            visitor = f.cleaned_data['visitor']
            content = f.cleaned_data['content']
            email = f.cleaned_data['email']
            date_time = timezone.localtime(timezone.now())  # 擷取現在時間
            Comment.objects.create(visitor=visitor, email=email, content=content, date_time=date_time, restaurant=r)
            visitor, content, email = ('', '', '')
            f = CommentForm(initial={'content': '我沒意見'})
    else:
        f = CommentForm(initial={'content': '我沒意見'})
    return render(request, 'comments.html', locals())
```
改成
```python=
from restaurants.forms import CommentForm
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView

class CommentView(FormView, SingleObjectMixin):
    form_class = CommentForm
    template_name = 'comments.html'
    success_url = '/comment/'
    initial = {'content': '我沒意見'}

    def form_valid(self, form):
        Comment.objects.create(
            visitor=form.cleaned_data['visitor'],
            email=form.cleaned_data['email'],
            content=form.cleaned_data['content'],
            date_time=timezone.localtime(timezone.now()),
            restaurant=self.get_object(),
        )
        return self.render_to_response(self.get_context_data(
            form=self.form_class(initial=self.initial)
        ))
```
```form_class```:設定要使用的表單類別，```template_name```跟之前一樣
```success_url```:指定一個合法的URL路徑，預設如果表單驗證正確，就會在表單處理完後跳轉至此頁面
```initial```:可以依表單欄位名稱提供初始值
```form_valid```方法會在使用者提交表單且表單欄位皆驗證通過時被呼叫(如果使用者是第一次進入該頁面，則會由其他方法處理)，不過此方法有預設的處理手段，如果我們不覆寫它的話，它就只會讓頁面跳轉至```success_url```，因為我們要依據表單來建立Comment資料，所以我們覆寫此方法
```form_valid```吃兩個參數，第一個是```self```，第二個是已經驗證通過的表單模型物件```form```
從form中取出各欄位的```cleaned_data```並呼叫Comment物件管理器的create方法來新增一筆評論

## 處理CRUD

---
### CreateView(新增檢視類別)
```views.py```
```python=
class SchoolCreateView(CreateView):
    fields=('name','principal','location')
    model=models.School
```
```urls.py```
```python=
path('create/',views.SchoolCreateView.as_view(), name='create'),
```
```school_form.html```
```python=
{% extends "basic_app/basic_app_base.html"%}

{% block body_block %}
<h1>
    {% if not form.instance.pk %}
    Create School
    {% else %}
    Update School
    {% endif %}
</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="submit" class="btn btn-primary" value="Submit"> 
</form>

{% endblock%}
```
```models.py```
```python=
class School(models.Model):
    name=models.CharField(max_length=256)
    principal=models.CharField(max_length=256)
    location=models.CharField(max_length=256)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("basic_app:detail", kwargs={"pk": self.pk})
    

class Student(models.Model):
    name=models.CharField(max_length=256)
    age=models.PositiveIntegerField(default=0,max_length=256)
    school=models.ForeignKey(School,related_name='students',on_delete=models.CASCADE)

    def __str__(self):
        return self.name
```
---
### UpdateView(修改檢視類別)

```python=
class SchoolUpdateView(UpdateView):
    fields =('name','principal')
    model=models.School
```
```urls.py```
```python=
path('update/<int:pk>/', views.SchoolUpdateView.as_view(), name='update'),
```
```school_detail.html```
```html=
{% extends 'basic_app/basic_app_base.html' %}
{% block body_block %}
<div class="jumbotron">
    <h1>Welcome to the School Detail Page</h1>
    <h2>School details:</h2>
    <p>Name: {{school_detail.name}}</p>
    <p>Principal: {{school_detail.principal }} </p>
    <p>Location:{{school_detail.location}}</p>
    <h3>Students:</h3>

    {% for student in school_detail.students.all %}
    <p>{{student.name}} who is {{student.age}} years old.</p>
    {% endfor %}
</div>
<div class="container">
    <p><a class='btn btn-warning' href="{% url 'basic_app:update' pk=school_detail.pk %}">Update</a></p>
</div>
{% endblock %}
<h1></h1>
```

---
### DeleteView(刪除檢視類別)

```views.py```
```python=
class SchoolDeleteView(DeleteView):
    model=models.School
    success_url= reverse_lazy("basic_app:list")
```

```urls.py```
```python=
path('delete/<int:pk>/', views.SchoolDeleteView.as_view(), name='delete'),
```
```school_confirm_delete.html```
```html=
{% extends "basic_app/basic_app_base.html" %}

{% block body_block %}
<h1>Delete {{school.name}}?</h1>
<form method="post">
    {% csrf_token %}
    <input type="submit" class='btn btn-danger' value="Delete">
    <a href="{% url 'basic_app:detail' pk=school.pk %}">Cancel</a>
</form>

{% endblock %}
```
