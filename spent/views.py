from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.http import HttpResponse
from .forms import CategoryForm,SpentForm,TrackForm,TrackingForm,BudgetCategoryForm,BudgetForm,BudgetClassItemForm,BudgetItemForm
from .models import Spent,Category,SavingsTracker,Tracker,Track,Tracking,NotIn,BudgetCategory,Budget,BudgetItem,BudgetClassItem
from django.views import View
import datetime
import calendar
from django.utils import timezone as tz
from django_pandas.io import read_frame
import pandas as pd
from django.db.models import Sum
from django.db import connection
from django.conf import settings
from .utils import TrackingDict
import math
# Create your views here.
def index(request):
    return HttpResponse("Hello From Django")
class BudgetCategoryView(LoginRequiredMixin,View):
    template_name = "spent/budget_category.html"
    form_class = BudgetCategoryForm
    success_url = "/budgetcategorylist"
    context_object_name = "form"
    login_url = settings.LOGIN_URL
    def get(self,request):
        form = BudgetCategoryForm()
        return render(request,self.template_name,{'form':form})
    def post(self,request):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        form = BudgetCategoryForm(request.POST)
        if(form.is_valid()):
            name = form.cleaned_data['name']
            name= name.upper().strip()
            priority= form.cleaned_data['priority']
            bcat_dub = BudgetCategory.objects.filter(name=name)
            if(len(bcat_dub) ==0):
                record = BudgetCategory()
                record.name=name
                record.priority=priority
                record.user_id=user
                record.save()
                return redirect('budget_category_list')
            else:
                return render(request,self.template_name,{'form':form,'error':'Budget Category Already Exists!!!'})
        else:
            return render(request, self.template_name, {'form': form, 'error': 'Some Error Ocurred!!!'})



class UpdateBudgetCategoryView(LoginRequiredMixin,UpdateView):
    template_name = "spent/update_budget_category.html"
    model = BudgetCategory
    success_url = "/budgetcategorylist"
    pk_url_kwarg = "pk"
    fields = ['name', 'priority']
    login_url = settings.LOGIN_URL
    def get(self,request,id):
        bcategory = BudgetCategory.objects.get(pk=id)
        form = BudgetCategoryForm(instance=bcategory)
        return render(request,self.template_name,{'form':form})
    def post(self,request,id):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        form = BudgetCategoryForm(request.POST)
        if (form.is_valid()):
            name = form.cleaned_data['name']
            name = name.upper().strip()
            priority = form.cleaned_data['priority']
            bcat_dub = BudgetCategory.objects.filter(name=name)
            if (len(bcat_dub) == 0):
                record = BudgetCategory.objects.get(pk=id)
                record.name = name
                record.priority = priority
                record.user_id=user
                record.save()
                return redirect('budget_category_list')
            else:
                return render(request, self.template_name, {'form': form, 'error': 'Budget Category Already Exists!!!'})
        else:
            return render(request, self.template_name, {'form': form, 'error': 'Some Error Ocurred!!!'})

class BudgetCategoryListView(LoginRequiredMixin,ListView):
    template_name ="spent/budget_category_list.html"
    model = BudgetCategory
    login_url = settings.LOGIN_URL
    def get_queryset(self):
        query_set = super().get_queryset()
        user = User.objects.get(username=self.request.user)
        query_set=query_set.filter(user_id=user,voided=0)
        return query_set

class DeleteBudgetCategoryView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        obj = BudgetCategory.objects.get(pk=id)
        return render(request,"spent/delete_budget_category.html",{"obj":obj})
    def post(self,request,id,*args,**kwargs):
        if request.POST['delete'] =="delete":
            category = BudgetCategory.objects.get(pk=id)
            category.voided =1
            category.save()
            return redirect("budget_category_list")
        else:
            return redirect("budget_category_list")
#................end of Budget Category Sections
# .........BUDGET SECTION ...............
class AddBudgetView(LoginRequiredMixin,View):
    template_name = "spent/create_budget.html"
    form_class = BudgetForm
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user)
        form = BudgetForm(user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user)  # gets the current logged in user
        form = BudgetForm(user, request.POST)
        if form.is_valid():
            name= form.cleaned_data['name']
            description= form.cleaned_data['description']
            track_id = form.cleaned_data['track_id']
            record = Budget()
            record.name=name
            record.description = description
            record.track_id =track_id
            record.user_id =user
            record.save()
            return redirect("budget_list")
        else:
            return render(request,self.template_name,{'form':form})

class UpdateBudgetView(LoginRequiredMixin,View):
    template_name = "spent/update_budget_form.html"
    form_class = BudgetForm
    def get(self,request,id ,*args, **kwargs):
        user = User.objects.get(username=self.request.user)
        budget_data = Budget.objects.get(pk=id)
        form = BudgetForm(user,instance=budget_data)
        return render(request, self.template_name, {'form': form})
    def post(self, request, id, *args, **kwargs):
        user = User.objects.get(username=self.request.user)  # gets the current logged in user
        form = BudgetForm(user, request.POST)
        if form.is_valid():
            name= form.cleaned_data['name']
            description= form.cleaned_data['description']
            track_id = form.cleaned_data['track_id']
            record = Budget.objects.get(pk=id)
            record.name=name
            record.description = description
            record.track_id =track_id
            record.user_id =user
            record.save()
            return redirect("budget_list")
        else:
            return render(request,self.template_name,{'form':form})

class DeleteBudgetView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        obj = Budget.objects.get(pk=id)
        return render(request,"spent/delete_budget_form.html",{"obj":obj})
    def post(self,request,id,*args,**kwargs):
        if request.POST['delete'] =="delete":
            category = Budget.objects.get(pk=id)
            category.voided =1
            category.save()
            return redirect("budget_list")
        else:
            return redirect("budget_list")

class BudgetListView(LoginRequiredMixin,View):
    def get(self,request):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        data ={}
        with connection.cursor() as cursor:
            cursor.execute(f"""
                select b.id,
                b.name,
                b.description,
                t.start_date,
                t.end_date,
                t.amount as track_amount,
                case when total_budget.budget_total is not NULL
                then total_budget.budget_total
                else 0 end as budget_total,
                case when spent.total_spent is not NULL
                then spent.total_spent else 0 end as total_spent,
                case when total_budget.budget_total is not null and spent.total_spent is not null then 
                total_budget.budget_total-spent.total_spent
                when total_budget.budget_total is null and spent.total_spent is not null   then 0-spent.total_spent
                when total_budget.budget_total is not null and spent.total_spent is null  then total_budget.budget_total-0
                else 0 end as remaining_budget,
                
                case when (total_budget.budget_total is not null and spent.total_spent is not null) AND
                 (total_budget.budget_total-spent.total_spent) < 0  then "surpassed budget"
                when total_budget.budget_total is null and spent.total_spent is not null  and spent.total_spent >0   then "surpassed budget"
                when total_budget.budget_total is not null and spent.total_spent is null and total_budget.budget_total !=0 then "on budget"
                else "on budget" end as budget_status
                from spent_budget b
                inner join spent_track t on t.id = b.track_id_id
                left outer join (
                select sbi.budget_id,sum(sbi.amount) as budget_total
                 from spent_budgetitem sbi
                where sbi.voided = 0 and user_id_id = {user_id}
                group by sbi.budget_id
                )total_budget on b.id = total_budget.budget_id
                left outer join (
                select bd.id,tracker.total_spent
                from spent_budget bd
                inner join (
                select tk.track_id_id,
                 sum(s.amount) as total_spent
                 from spent_tracking tk
                inner join spent_spent s on tk.spent_id_id = s.id
                where tk.voided=0 and s.voided=0 and tk.user_id_id= {user_id}
                group by tk.track_id_id
                )tracker on bd.track_id_id = tracker.track_id_id
                )spent on b.id = spent.id
                where b.voided = 0 and b.user_id_id ={user_id}
                order by t.start_date desc
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        context ={
            'datalist':data,
        }
        return render(request,'spent/budget_list.html',context)
class IndividualBudgetView(LoginRequiredMixin,View):
    def get(self,request,budget):
        user = User.objects.get(username=self.request.user) # get the user
        user_id = user.id #get the user id
        with connection.cursor() as cursor:
            cursor.execute(f"""
            select b.id,
            b.name,
            b.description,
            t.start_date,
            t.end_date,
            t.amount as track_amount,
            case when total_budget.budget_total is not NULL
            then total_budget.budget_total
            else 0 end as budget_total,
            case when spent.total_spent is not NULL
            then spent.total_spent else 0 end as total_spent,
            total_budget.budget_total-spent.total_spent as remaining_budget,
            case when (total_budget.budget_total-spent.total_spent) < 0 then "surpassed budget"
            else "on budget"  end as budget_status
            from spent_budget b
            inner join spent_track t on t.id = b.track_id_id
            left outer join (
            select sbi.budget_id,sum(sbi.amount) as budget_total
             from spent_budgetitem sbi 
            where sbi.voided = 0 and user_id_id = {user_id}
            group by sbi.budget_id
            )total_budget on b.id = total_budget.budget_id
            left outer join (
            select bd.id,tracker.total_spent
            from spent_budget bd
            inner join (
            select tk.track_id_id,
             sum(s.amount) as total_spent
             from spent_tracking tk
            inner join spent_spent s on tk.spent_id_id = s.id
            where tk.voided=0 and s.voided=0 and tk.user_id_id= {user_id}
            group by tk.track_id_id
            )tracker on bd.track_id_id = tracker.track_id_id
            )spent on b.id = spent.id
            where b.voided = 0 and b.user_id_id ={user_id} and b.id={budget}
            order by t.start_date desc
            """)
            columns = [col[0] for col in cursor.description]
            budgetdata = [dict(zip(columns, row)) for row in cursor.fetchall()][0]

        with connection.cursor() as cursor:
            cursor.execute(f"""
            select bi.id,
            bci.name,
            bi.amount,
            case when sp.budget_spent is not NULL then sp.budget_spent
            else 0 end as budget_spent,
            case when sp.budget_spent is not NULL then (bi.amount - sp.budget_spent)
            else bi.amount end as remaining_budget,
            case when ((sp.budget_spent is not NULL) and (bi.amount - sp.budget_spent) < 0) then "surpasses budget"
            else "on budget" end as budget_status,
            bc.name as category,
            bc.priority
             from spent_budgetitem bi
            inner join spent_budgetclassitem bci on bi.budget_class_item_id = bci.id
            inner join spent_budgetcategory bc on bci.budget_category_id = bc.id
            left outer join(
            select
            spent.budget_class_category,
            spent.name,
            sum(amount) budget_spent
            from spent_budget b
            inner join (
            select trk.track_id_id,
            a.*
             from spent_tracking trk
             inner join (
            select 
            ss.id as spent_id,
            ss.amount,
            ss.category_id_id,
            ct.budget_class_category,
            ct.name
             from spent_spent ss
              inner join(
            select cat.id as category_id,
            cat.category,
            bdgclass.id as budget_class_category,
            bdgclass.name
             from spent_category cat
            inner join spent_budgetclassitem bdgclass on cat.budget_category_id = bdgclass.id
            where cat.voided =0 and bdgclass.voided=0 and cat.user_id_id={user_id}) ct
            on ss.category_id_id = ct.category_id
             where ss.voided=0 and ss.user_id_id={user_id}) a 
             on trk.spent_id_id = a.spent_id 
             where trk.voided =0
            )spent on b.track_id_id = spent.track_id_id
            where b.voided=0 and b.id ={budget}
            group by spent.budget_class_category
            )sp on bci.id = sp.budget_class_category
            where bi.voided=0 and bci.voided=0 and bi.user_id_id={user_id} and bci.user_id_id ={user_id}
            and bi.budget_id={budget}
            order by bc.priority
            """)
            columns = [col[0] for col in cursor.description]
            datalist = [dict(zip(columns, row)) for row in cursor.fetchall()]
        with connection.cursor() as cursor:
            cursor.execute(f"""
            select 
            sum(s.amount) as budget_total,
            sum(s.budget_spent) as spent_total,
            sum(s.remaining_budget) as remaining_total,
            s.category
            from 
            (
            select bi.id,
            bci.name,
            bi.amount,
            case when sp.budget_spent is not NULL then sp.budget_spent
            else 0 end as budget_spent,
            case when sp.budget_spent is not NULL then (bi.amount - sp.budget_spent)
            else bi.amount end as remaining_budget,
            case when ((sp.budget_spent is not NULL) and (bi.amount - sp.budget_spent) < 0) then "surpasses budget"
            else "on budget" end as budget_status,
            bc.name as category,
            bc.priority
             from spent_budgetitem bi
            inner join spent_budgetclassitem bci on bi.budget_class_item_id = bci.id
            inner join spent_budgetcategory bc on bci.budget_category_id = bc.id
            left outer join(
            select
            spent.budget_class_category,
            spent.name,
            sum(amount) budget_spent
            from spent_budget b
            inner join (
            select trk.track_id_id,
            a.*
             from spent_tracking trk
             inner join (
            select 
            ss.id as spent_id,
            ss.amount,
            ss.category_id_id,
            ct.budget_class_category,
            ct.name
             from spent_spent ss
              inner join(
            select cat.id as category_id,
            cat.category,
            bdgclass.id as budget_class_category,
            bdgclass.name
             from spent_category cat
            inner join spent_budgetclassitem bdgclass on cat.budget_category_id = bdgclass.id
            where cat.voided =0 and bdgclass.voided=0 and cat.user_id_id={user_id}) ct
            on ss.category_id_id = ct.category_id
             where ss.voided=0 and ss.user_id_id={user_id}) a 
             on trk.spent_id_id = a.spent_id 
             where trk.voided =0
            )spent on b.track_id_id = spent.track_id_id
            where b.voided=0 and b.id ={budget}
            group by spent.budget_class_category
            )sp on bci.id = sp.budget_class_category
            where bi.voided=0 and bci.voided=0 and bi.user_id_id={user_id} and bci.user_id_id ={user_id}
            and bi.budget_id={budget}
            order by bc.priority) s
            group by s.category
            order by s.priority
            """)

            columns = [col[0] for col in cursor.description]
            groupdata = [dict(zip(columns, row)) for row in cursor.fetchall()]
        context={
            'datalist':datalist,
            'groupdata':groupdata,
            'budgetdata':budgetdata,
        }
        return render(request,'spent/individual_budget_view_form.html',context)

# ...............end of budget section
#...............start of Budget Class Item and Budget Item

class AddBudgetClassItemView(LoginRequiredMixin,View):
    template_name = "spent/add_budget_class_item_form.html"
    form_class = BudgetClassItemForm
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user)
        form = BudgetClassItemForm(user)
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user)  # gets the current logged in user
        form = BudgetClassItemForm(user, request.POST)
        if form.is_valid():
            name= form.cleaned_data['name']
            budget_category= form.cleaned_data['budget_category']
            name = name.upper().strip()
            #check if the item already exists
            data = BudgetClassItem.objects.filter(name=name,voided=0,user_id=user.id)
            if(len(data)==0):
                record = BudgetClassItem()
                record.name=name
                record.budget_category = budget_category
                record.user_id =user
                record.save()
                return redirect("class_item_list")
            else:
                return render(request, self.template_name, {'form': form,'error':'Budget Class Item Already Exists!!!'})
        else:
            return render(request,self.template_name,{'form':form})


class UpdateBudgetClassItemView(LoginRequiredMixin,View):
    template_name = "spent/update_budget_class_item_form.html"
    form_class = BudgetClassItemForm
    def get(self,request,id ,*args, **kwargs):
        user = User.objects.get(username=self.request.user)
        class_data = BudgetClassItem.objects.get(pk=id)
        form = BudgetClassItemForm(user,instance=class_data)
        return render(request, self.template_name, {'form': form})
    def post(self, request, id, *args, **kwargs):
        user = User.objects.get(username=self.request.user)  # gets the current logged in user
        form = BudgetClassItemForm(user, request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            name = name.upper().strip()
            budget_category = form.cleaned_data['budget_category']
            data = BudgetClassItem.objects.filter(name=name, voided=0, user_id=user.id)
            if (len(data) == 0):
                record = BudgetClassItem.objects.get(pk=id)
                record.name = name
                record.budget_category = budget_category
                record.user_id = user
                record.save()
                return redirect("class_item_list")
            else:
                return render(request, self.template_name, {'form': form,'error':'Class Item Already Exists'})
        else:
            return render(request,self.template_name,{'form':form})


class DeleteBudgetClassItemView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        obj = BudgetClassItem.objects.get(pk=id)
        return render(request,"spent/delete_budget_class_item_form.html",{"obj":obj})
    def post(self,request,id,*args,**kwargs):
        if request.POST['delete'] =="delete":
            category = BudgetClassItem.objects.get(pk=id)
            category.voided =1
            category.save()
            return redirect("class_item_list")
        else:
            return redirect("class_item_list")

class BudgetClassItemListView(LoginRequiredMixin,View):
    def get(self,request):
        user = User.objects.get(username=self.request.user)
        datalist = BudgetClassItem.objects.filter(user_id=user,voided=0)
        context={
            'datalist':datalist
        }
        return render(request,'spent/budget_class_item_list.html',context)
#.......................................................................
#.................INDIVIDUAL BUDGET ITEM ....................
class AddBudgetItemView(LoginRequiredMixin,View):
    template_name = "spent/add_budget_item_form.html"
    form_class = BudgetItemForm
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user)
        form = BudgetItemForm(user)
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        user = User.objects.get(username=self.request.user)  # gets the current logged in user
        form = BudgetItemForm(user, request.POST)
        if form.is_valid():
            budget= form.cleaned_data['budget']
            budget_class_item= form.cleaned_data['budget_class_item']
            #check if the value already exists
            data = BudgetItem.objects.filter(budget=budget,budget_class_item=budget_class_item,voided=0,user_id=user.id)
            if(len(data)==0):
                amount = form.cleaned_data['amount']
                record = BudgetItem()
                record.budget=budget
                record.budget_class_item = budget_class_item
                record.amount = amount
                record.user_id =user
                record.save()
                return redirect("budget_item_list")
            else:
                return render(request, self.template_name, {'form': form,'error':'Budget Item Already Exists'})
        else:
            return render(request,self.template_name,{'form':form})

class UpdateBudgetItemView(LoginRequiredMixin,View):
    template_name = "spent/update_budget_item_form.html"
    form_class = BudgetItemForm
    def get(self, request,id, *args, **kwargs):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        budgetItem = BudgetItem.objects.get(pk=id)
        form = BudgetItemForm(user,instance=budgetItem)
        return render(request, self.template_name, {'form': form})
    def post(self, request,id, *args, **kwargs):
        user = User.objects.get(username=self.request.user)  # gets the current logged in user
        form = BudgetItemForm(user, request.POST)
        if form.is_valid():
            budget= form.cleaned_data['budget']
            budget_class_item= form.cleaned_data['budget_class_item']
            amount = form.cleaned_data['amount']
            record = BudgetItem.objects.get(pk=id)
            record.budget=budget
            record.budget_class_item = budget_class_item
            record.amount = amount
            record.user_id =user
            record.save()
            return redirect("budget_item_list")
        else:
            return render(request, self.template_name, {'form': form,'error':'Some Error Ocurred!!!'})


class DeleteBudgetItemView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        obj = BudgetItem.objects.get(pk=id)
        return render(request,"spent/delete_budget_item_form.html",{"obj":obj})
    def post(self,request,id,*args,**kwargs):
        if request.POST['delete'] =="delete":
            category = BudgetItem.objects.get(pk=id)
            category.voided =1
            category.save()
            return redirect("budget_item_list")
        else:
            return redirect("budget_item_list")

class BudgetItemListView(LoginRequiredMixin,View):
    def get(self,request):
        user = User.objects.get(username=self.request.user)
        user_id =user.id
        today = datetime.datetime.now().date()
        start_date = datetime.date(today.year, today.month, 1)
        end_date = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        datalist={}
        with connection.cursor() as cursor:
            cursor.execute(f"""
            select sbi.id, b.name as budget,
            bci.name as budget_class_item,
             sbi.amount
             from spent_budgetitem sbi
            inner join spent_budget b on sbi.budget_id = b.id
            inner join spent_budgetclassitem bci on sbi.budget_class_item_id = bci.id
            inner join spent_track tr on b.track_id_id = tr.id
            where tr.start_date < CURRENT_DATE AND tr.end_date > CURRENT_DATE AND sbi.voided = 0 
            and b.voided=0 and bci.voided=0
            and tr.voided=0 and sbi.user_id_id ={user_id}
            
            """)
            columns = [col[0] for col in cursor.description]
            datalist = [dict(zip(columns, row)) for row in cursor.fetchall()]
            budgets = Budget.objects.filter(user_id=user,voided=0)
        context={
            'datalist':datalist,
            'budgets':budgets
        }
        return render(request,'spent/budget_item_list.html',context)
    def post(self,request):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        budget = request.POST['budget']
        datalist = {}
        with connection.cursor() as cursor:
            cursor.execute(f"""
                    select sbi.id,b.name as budget,
                    bci.name as budget_class_item,
                     sbi.amount
                     from spent_budgetitem sbi
                    inner join spent_budget b on sbi.budget_id = b.id
                    inner join spent_budgetclassitem bci on sbi.budget_class_item_id = bci.id
                    inner join spent_track tr on b.track_id_id = tr.id
                    where b.id={budget} AND sbi.voided = 0 
                    and b.voided=0 and bci.voided=0
                    and tr.voided=0 and sbi.user_id_id ={user_id}

                    """)
            columns = [col[0] for col in cursor.description]
            datalist = [dict(zip(columns, row)) for row in cursor.fetchall()]
        budgets = Budget.objects.filter(user_id=user, voided=0)
        context = {
            'datalist': datalist,
            'budgets': budgets
        }
        return render(request, 'spent/budget_item_list.html', context)
#...............................................................................
class CategoryView(LoginRequiredMixin,View):
    template_name = "spent/category_page.html"
    form_class= CategoryForm
    success_url = "/addCategory"
    context_object_name="form"
    login_url = settings.LOGIN_URL

    def get(self,request):
        user = User.objects.get(username=self.request.user)
        form = CategoryForm(user)
        return render(request,self.template_name,{'form':form})
    def post(self,request):
        user = User.objects.get(username=self.request.user)
        user_id =user.id
        form = CategoryForm(user,request.POST)
        if(form.is_valid()):
            date = form.cleaned_data['date']
            category = form.cleaned_data['category']
            category = category.upper().strip()
            as_savings = form.cleaned_data['as_savings']
            budget_category  = form.cleaned_data['budget_category']
            cat_dub = Category.objects.filter(category=category)
            if(len(cat_dub)==0):
                record = Category()
                record.date=date
                record.category=category
                record.as_savings = as_savings
                record.budget_category=budget_category
                record.user_id=user
                record.save()
                return redirect('category_list')
            else:
                return render(request,self.template_name,{'form':form,'error':'Error Category Already Exists!!!'})
        else:
            return render(request,self.template_name,{'form':form})


class CategoryListView(LoginRequiredMixin,ListView):
    template_name ="spent/category_list.html"
    model = Category
    login_url = settings.LOGIN_URL
    def get_queryset(self):
        query_set = super().get_queryset()
        user = User.objects.get(username=self.request.user)
        query_set=query_set.filter(user_id=user,voided=0)
        return query_set

class UpdateCategoryView(LoginRequiredMixin,View):
    template_name = "spent/category_page.html"
    model= Category
    success_url="/"
    pk_url_kwarg = "pk"
    fields=['date','category','as_savings','budget_category']
    login_url = settings.LOGIN_URL
    def get(self,request,id):
        user = User.objects.get(username=self.request.user)
        user_id =user.id
        category = Category.objects.get(pk=id)
        form = CategoryForm(user,instance=category)
        return render(request, self.template_name, {'form': form})
    def post(self,request,id):
        user = User.objects.get(username=self.request.user)
        user_id =user.id
        form = CategoryForm(user, request.POST)
        if (form.is_valid()):
            date = form.cleaned_data['date']
            category = form.cleaned_data['category']
            category =category.upper().strip()
            as_savings = form.cleaned_data['as_savings']
            budget_category = form.cleaned_data['budget_category']
            #retrieve the record to update
            record = Category.objects.get(pk=id)
            record.date = date
            record.category = category
            record.as_savings = as_savings
            record.budget_category = budget_category
            record.user_id =user
            record.save()
            return redirect('category_list')
        else:
            return render(request, self.template_name, {'form': form})
class DeleteCategoryView(LoginRequiredMixin,View):
    def get(self,request,id,*args,**kwargs):
        obj = Category.objects.get(pk=id)
        return render(request,"spent/delete_category.html",{"obj":obj})
    def post(self,request,id,*args,**kwargs):
        if request.POST['delete'] =="delete":
            category = Category.objects.get(pk=id)
            category.voided =1
            category.save()
            return redirect("category_list")
        else:
            return redirect("category_list")


class AddSpentView(LoginRequiredMixin,View):
    template_name="spent/spent_page.html"
    login_url = settings.LOGIN_URL
    def get(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        form = SpentForm(user)
        return render(request,self.template_name,{'form':form})
    def post(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user) #gets the current logged in user
        form = SpentForm(user,request.POST)
        if form.is_valid():
            date= form.cleaned_data['date']
            category_id = form.cleaned_data['category_id'].id
            amount = form.cleaned_data['amount']
            user_id = User.objects.get(username=self.request.user)

            already = Spent.objects.filter(date=date,category_id=category_id,user_id=user_id,voided=0) #checking if spent already exists
            if(len(already) == 0):
                result = Spent()
                result.date=date
                result.category_id = Category.objects.get(id=category_id)
                result.amount=amount
                result.user_id = user_id
                result.save()
                #create tracking for tracking between a certain period
                track = Track.objects.filter(start_date__lte=date,end_date__gte=date,user_id=user_id,voided=0).order_by('-start_date')
                print("Track Model",track,date)
                if(len(track) !=0): # if there is a track define in that period
                    recent_track = track[0] #get the recent track
                    #get the Tracker with the recent track id and category_id and use it to create tracking in the spent Model
                    tracker = Tracker.objects.filter(track_id=recent_track,category_id=Category.objects.get(id=category_id),voided=0,user_id=user_id)
                    print("Tracker Model",tracker)
                    if(len(tracker)==1):
                        new_tracking = Tracking()
                        new_tracking.user_id=user_id
                        new_tracking.spent_id = Spent.objects.get(pk=result.id)
                        new_tracking.track_id=recent_track
                        new_tracking.save() # create a new tracking
                #update the savingsTracker if category has as_savings to true
                if result.category_id.as_savings:
                    savings = SavingsTracker()
                    savings.spent_id = Spent.objects.get(pk=result.id) #update the spent record id
                    savings.user_id=user_id
                    savings.save()

            else:
                return HttpResponse("You have already spent that item, do you wish to update the item???")
            return redirect("daily_list")
        else:
            return render(request, self.template_name, {'form': form})
class UpdateSpentView(LoginRequiredMixin,View):
    template_name="spent/update_spent_form.html"
    model= Spent
    form_class = SpentForm
    #fields =["date","category_id","amount"]
    pk_url_kwarg ="pk"
    success_url="/dailylist"
    login_url = settings.LOGIN_URL
    def get(self,request,id):
        user = User.objects.get(username=self.request.user)
        spent = Spent.objects.get(pk=id)
        form = SpentForm(user, instance=spent)
        return render(request,self.template_name,{'form':form})
    def post(self,request,id):
        user = User.objects.get(username=self.request.user)
        spent = Spent.objects.get(pk=id)
        form = SpentForm(user,request.POST)
        if(form.is_valid()):
            date = form.cleaned_data['date']
            category_id = form.cleaned_data['category_id']
            amount = form.cleaned_data['amount']
            record = Spent.objects.get(pk=id)
            record.date=date
            record.category_id =category_id
            record.amount=amount
            record.user_id=user
            record.save()
            return redirect('daily_list')
        else:
            return render(request, self.template_name, {'form': form,'error':'Some Error Ocurred'})
class DeleteSpentView(LoginRequiredMixin,View):
    template_name="spent/delete_spent_form.html"
    model =Spent
    pk_url_kwarg="pk"
    success_url='/dailylist'
    login_url = settings.LOGIN_URL
    def get(self,request,id,*args,**kwargs):
        object=get_object_or_404(Spent,pk=id)
        return render(request,self.template_name,{"obj":object})
    def post(self,request,id,*args,**kwargs):
        print(request.POST['delete'])
        if request.POST['delete'] == "delete":
            Spent.objects.filter(pk=id).update(voided=1)
            return redirect('daily_list')
        else:
            return redirect('daily_list')

class DailyListView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        today =tz.now().date()
        spents = Spent.objects.filter(date=today,voided=0,user_id=user)
        user_id = user.id
        totals = spents.aggregate(totals=Sum('amount')) #calculate aggregated Spent
        with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT sum(c.amount) as total_debt
                     FROM credits_credit c
                     where c.voided=0 and c.paid=0 and c.user_id_id={user_id}
                """)
                columns = [col[0] for col in cursor.description]
                debt_owed = [dict(zip(columns,row)) for row in cursor.fetchall()]
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT sum(s.amount) debt_paid
                 FROM credits_credit c
                 inner join (
                 SELECT
                cs.amount,
                cs.debt_id_id
                 FROM credits_creditservice cs
                 where cs.voided=0
                 )s on c.id = s.debt_id_id
                 where c.voided=0 and c.paid=0 and c.user_id_id={user_id}
            """)
            columns = [col[0] for col in cursor.description]
            debt_paid = [dict(zip(columns,row)) for row in cursor.fetchall()]

            if len(debt_owed)>0:
                debt_owed= debt_owed[0]['total_debt']
            else:
                debt_owed = 0
            if len(debt_paid)>0:
                debt_paid= debt_paid[0]['debt_paid']
            else:
                debt_paid = 0
            if(debt_paid is None):
                debt_paid = 0
            if(debt_owed is None):
                debt_owed =0
        return render(request,"spent/daily_spent.html",{'daily_spent':spents,'totals':totals['totals'],'debt':(debt_owed-debt_paid)})


class AllListView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        now = tz.now()
        new_data=[]
        # start_month =datetime.date(now.year,now.month,1)
        # end_month = datetime.date(now.year,now.month,calendar.monthrange(now.year,now.month)[1])
        month_data = Spent.objects.filter(voided=0,user_id=user)
        #calculate the total budget spending done so far and what is remaining
        spent_amount = 0
        budget_amount =0
        remaining_amount = 0
        tracks=Track.objects.filter(start_date__lte=now.date(),end_date__gte=now.date(),voided=0,user_id=user)
        if(len(tracks) ==1):
            spent_amount=Tracking.objects.filter(track_id=tracks[0]).aggregate(Sum('spent_id__amount'))
            spent_amount=spent_amount['spent_id__amount__sum']
            if(spent_amount == None):
                spent_amount =0
            budget_amount = tracks[0].amount
            remaining_amount =budget_amount - spent_amount
        #........................................................................
        if(len(month_data) > 0): # account for empty list
            month_df = read_frame(month_data,fieldnames=['date','category_id','amount'])
            month_df.index = pd.to_datetime(month_df['date']) #use date as datetime_index inorder to perform resample
            month_cumm = month_df.resample('D').sum()
            month_cumm = month_cumm.reset_index()#reset back index to 0 index based.
            month_cumm = month_cumm.sort_values('date',ascending=False)
            data = month_cumm.to_dict() #convert dataframe to dictionary

            new_data = []
            for (x, y) in zip(list(data['date'].values()), list(data['amount'].values())): #combine both date and amount in a tuple
                if(y == 0): # remove days where there were no spent
                    continue
                new_data.append((x,y))
            totals = None
            if new_data != []:
                df =pd.DataFrame(new_data)
                totals = df[1].sum()
            return render(request,"spent/all_list.html",{'data':new_data,'totals':totals,
                                                              'budget_amount':budget_amount,
                                                              'remaining_amount':remaining_amount,
                                                              'spent_amount':spent_amount})
        else:
            return render(request,"spent/all_list.html")


class SpentInASpecificDayView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,day,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        today = datetime.datetime.fromisoformat(day)
        today = today.date()
        spents = Spent.objects.filter(date=today,voided=0,user_id=user)
        totals = spents.aggregate(totals=Sum('amount'))
        return render(request, "spent/daily_spent.html", {'daily_spent': spents,'totals':totals['totals']})
class MonthlyListView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        now = tz.now()
        new_data=[]
        start_month =datetime.date(now.year,now.month,1)
        end_month = datetime.date(now.year,now.month,calendar.monthrange(now.year,now.month)[1])
        days_spent = (now.date()-start_month).days + 1
        month_data = Spent.objects.filter(date__gte=start_month,date__lte=end_month,voided=0,user_id=user)
        #calculate the total budget spending done so far and what is remaining
        spent_amount = 0
        budget_amount =0
        remaining_amount = 0
        tracks=Track.objects.filter(start_date__lte=now.date(),end_date__gte=now.date(),voided=0,user_id=user)
        if(len(tracks) ==1):
            spent_amount=Tracking.objects.filter(track_id=tracks[0],spent_id__voided=0).aggregate(Sum('spent_id__amount'))
            spent_amount=spent_amount['spent_id__amount__sum']
            if(spent_amount == None):
                spent_amount =0
            budget_amount = tracks[0].amount
            remaining_amount = budget_amount - spent_amount
        #........................................................................
        if(len(month_data) > 0): # account for empty list
            month_df = read_frame(month_data,fieldnames=['date','category_id','amount'])
            month_df.index = pd.to_datetime(month_df['date']) #use date as datetime_index inorder to perform resample
            month_cumm = month_df.resample('D').sum()
            month_cumm = month_cumm.reset_index()#reset back index to 0 index based.
            month_cumm = month_cumm.sort_values('date',ascending=False)
            data = month_cumm.to_dict() #convert dataframe to dictionary

            new_data = []
            for (x, y) in zip(list(data['date'].values()), list(data['amount'].values())): #combine both date and amount in a tuple
                if(y == 0): # remove days where there were no spent
                    continue
                new_data.append((x,y))
            totals = None
            if new_data != []:
                df =pd.DataFrame(new_data)
                totals = df[1].sum()
            return render(request,"spent/daily_summary.html",{'data':new_data,'totals':totals,
                                                              'budget_amount':budget_amount,
                                                              'remaining_amount':remaining_amount,
                                                              'spent_amount':spent_amount,'average':math.ceil(totals/days_spent)})
        else:
            return render(request,"spent/daily_summary.html")

class DeleteBunchView(View,LoginRequiredMixin):
    login_url = settings.LOGIN_URL
    def get(self, request, day, *args, **kwargs):
        user = User.objects.get(username=self.request.user)
        date = datetime.datetime.fromisoformat(day)
        date = date.date()
        spents = Spent.objects.filter(date=date,voided=0,user_id=user)
        return render(request,"spent/delete_bunch.html",{'data':spents})
    def post(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        ids = request.POST.getlist('delete_ids')
        for id in ids:
            Spent.objects.filter(pk=id).update(voided=1)
        return redirect("monthly_list")


#savings view
class SavingsList(LoginRequiredMixin,ListView):
    template_name = "spent/savings_list.html"
    model = SavingsTracker
    login_url = settings.LOGIN_URL
    def get_queryset(self):
        query_set = super().get_queryset()# get the list
        user = User.objects.get(username=self.request.user) #filter for the current logged in user
        query_set = query_set.filter(user_id=user,voided=0)
        return query_set

class CreateTrackView(LoginRequiredMixin,CreateView):
    login_url = settings.LOGIN_URL
    model = Track
    template_name = "spent/create_track.html"
    form_class =TrackForm
    success_url = "/"

    def form_valid(self, form):
        user = User.objects.get(username=self.request.user)
        form.instance.user_id= user
        return super().form_valid(form)

class UpdateTrackView(LoginRequiredMixin,UpdateView):
    model = Track
    template_name = "spent/create_track.html"
    form_class = TrackForm
    login_url = settings.LOGIN_URL
    success_url = "/"
    pk_url_kwarg = "pk"
class TrackListView(LoginRequiredMixin,ListView):
    model = Track
    template_name = "spent/track_list.html"
    login_url = settings.LOGIN_URL

    def get_queryset(self):
        queryset= super().get_queryset()
        user = User.objects.get(username=self.request.user)
        queryset = queryset.filter(user_id=user,voided=0)
        return queryset




class CreateTrackingView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        choices = Track.objects.filter(user_id=user).values_list('id', 'start_date')

        return render(request,"spent/create_tracking.html",{"select_values":choices})

    def post(self,request,*args,**kwargs):
        track_id = None
        val = request.POST['tracks_submit'] # the value of button pressed
        user = User.objects.get(username=self.request.user)
        trackDict = TrackingDict()
        track_id = request.POST['tracks']
        print(track_id)
        choices = Track.objects.filter(user_id=user).values_list('id', 'start_date')
        if val == "Generate trackings Category":
            all_category = Category.objects.filter(user_id=user,voided=0).values('id','category')
            track = Track.objects.get(pk=track_id)
            tracker = Tracker.objects.filter(track_id=track,voided=0)
            for x in all_category:
                trackDict.addCategory(x['category'],x['id'])
            for cat in tracker:
                trackDict.updateCategory(cat.category_id.category)
            return render(request,"spent/create_tracking.html",{"select_values":choices,"categories":trackDict.get_tracking_list()})


        if val == "Update the Tracking list":
            track_id = request.POST['tracks']
            track = Track.objects.get(pk=track_id) #get the Track instance to add to Tracker
            ids = request.POST.getlist('cat_list')
            for id in ids: #use all checked boxes in the create_tracking template
                c=Category.objects.get(pk=id) # all the
                if(len(Tracker.objects.filter(track_id=track,category_id=c,voided=0))==0): #check for dublicate
                    tracker = Tracker()
                    tracker.category_id = c
                    tracker.user_id=user
                    tracker.track_id = track
                    tracker.save()
                elif(len(Tracker.objects.filter(track_id=track,category_id=c,voided=1))> 0): #this may blow up
                    tracker = Tracker.objects.get(track_id=track,category_id=c,voided=1)
                    tracker.voided=0
                    tracker.save()

            trackers = Tracker.objects.filter(track_id=track_id)
            trackers.update(voided=1)
            ### void all the Trackers and then unvoid all the selected inorder to use the in
            Tracker.objects.filter(track_id=track_id,category_id__in=ids).update(voided=0)

            # Laststep
            all_category = Category.objects.filter(user_id=user, voided=0)
            print(trackers)
            for x in all_category:
                trackDict.addCategory(x.category, x.id)
            for cat in trackers:
                print("values",cat.category_id.category)
                trackDict.updateCategory(cat.category_id.category)
            return render(request, "spent/create_tracking.html",
                          {"select_values": choices, "categories": trackDict.get_tracking_list()})
        return render(request, "spent/create_tracking.html", {"select_values": choices})

class TrackingListView(LoginRequiredMixin,ListView):
    model = Tracking
    login_url = settings.LOGIN_URL
    template_name = "spent/tracking_list.html"
    def get_queryset(self):
        user = User.objects.get(username=self.request.user)
        queryset = super().get_queryset()
        queryset=queryset.filter(user_id=user,voided=0)
        return queryset

class TrackerListView(LoginRequiredMixin,View):
    model =Tracker
    login_url = settings.LOGIN_URL
    template_name = "spent/tracker_list.html"
    def get(self,request,pk,*args,**kwargs):
        track =Track.objects.get(pk=pk)
        trackers = Tracker.objects.filter(track_id=track,voided=0)
        return render(request,self.template_name,{'trackers':trackers,'track':track})
class TrackerSummary(LoginRequiredMixin,View):
    model =Tracking
    login_url = settings.LOGIN_URL
    template_name = "spent/tracking_summary.html"
    def get(self,request,pk,*args,**kwargs):
        track = Track.objects.get(pk=pk)
        trackinglist = model.objects.get(track_id=track,voided=0)
        summary = tracklinglist.aggregate(total=Sum('spent_id'))
        return render(request,self.template_name)



class TrackerSpentListView(LoginRequiredMixin,View):
    model =Tracking
    login_url = settings.LOGIN_URL
    template_name = "spent/tracker_list.html"
    def get(self,request,pk,*args,**kwargs):
        track =Track.objects.get(pk=pk)
        #get info about Track selected start_date,end_date,budget_amount,spent_amount,remaining_amount
        start_date = track.start_date
        end_date = track.end_date
        days_spent = 1
        new_data=[]
        budget_amount =track.amount
        user = User.objects.get(username=self.request.user)
        trackings = Tracking.objects.filter(track_id=track,voided=0,user_id=user,spent_id__voided=0) # check if the spent was voided.
        spent_amount=trackings.aggregate(Sum('spent_id__amount'))
        spent_amount=spent_amount['spent_id__amount__sum']
        if(spent_amount == None):
            spent_amount =0
        remaining_amount = budget_amount - spent_amount

        if(len(trackings) > 0): # account for empty list
            track_data = Tracking.objects.filter(track_id=track,voided=0,user_id=user,spent_id__voided=0).values('spent_id__date','spent_id__amount')
            track_dict ={}
            #convert the list-dict to dict-list for easier export to pandas Dataframe
            for keys in track_data[0].keys():
                track_dict[keys]=[]
            for data in track_data:
                for key,val in data.items():
                    track_dict[key].append(val)
            days_spent=(max(track_dict['spent_id__date'])-min(track_dict['spent_id__date'])).days + 1



            #month_df = read_frame(track_data,fieldnames=['date','category_id','amount'])
            month_df=pd.DataFrame(track_dict)
            month_df.index = pd.to_datetime(month_df['spent_id__date']) #use date as datetime_index inorder to perform resample
            month_cumm = month_df.resample('D').sum()
            month_cumm = month_cumm.reset_index()#reset back index to 0 index based.
            month_cumm = month_cumm.sort_values('spent_id__date',ascending=False)
            data = month_cumm.to_dict() #convert dataframe to dictionary

            new_data = []
            for (x, y) in zip(list(data['spent_id__date'].values()), list(data['spent_id__amount'].values())): #combine both date and amount in a tuple
                if(y == 0): # remove days where there were no spent
                    continue
                new_data.append((x,y))
            totals = None
            if new_data != []:
                df =pd.DataFrame(new_data)
                totals = df[1].sum()
            return render(request,"spent/tracking_spent_list.html",{'data':new_data,'totals':totals,'start_date':start_date,'end_date':end_date,
                                                              'budget_amount':budget_amount,
                                                              'remaining_amount':remaining_amount,
                                                             'average':math.ceil(totals/days_spent),'budget_average':math.ceil(budget_amount/((end_date-start_date).days + 1))})
        return render(request,'spent/tracking_spent_list.html')




class SummaryGraphView(LoginRequiredMixin,View):
    def get(self,request,track,*args,**kwargs):
        track_data = Track.objects.get(pk=track)
        user = User.objects.get(username=self.request.user)
        sql =f"""select
        category.category,
        final.amount_spent
        from (
        select distinct sum(cat.amount) as amount_spent,
        cat.category_id_id
        from (
        select s.date,
        s.amount,
        s.category_id_id
         from spent_spent s
        inner join (
        select tng.spent_id_id
         from spent_tracking tng
        where tng.track_id_id = {track}
        and voided=0 and tng.user_id_id = {user.id}) t
        on s.id = t.spent_id_id
        where s.voided=0 ) cat
        group by cat.category_id_id) final
        left outer join (
        	select
        	c.id,
        	c.category
        	 from spent_category c
        )category on final.category_id_id = category.id
        order by final.amount_spent desc
         """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            graph_data = [dict(zip(columns,row)) for row in cursor.fetchall()]
            top_ten_data = graph_data[0:10]
            bottom_ten_data =graph_data[-10:]
        context ={
                'graph':graph_data,
                'top':top_ten_data,
                'bottom':bottom_ten_data,
                'track':track_data,
            }
        return render(request,'credits/summary_graph.html',context)


# Create your views here.
