from django.shortcuts import render,redirect,get_object_or_404

# Create your views here.

from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import DebtRegistrationForm,DebtServiceForm
from django.views import View
from django.conf import settings
from .models import Credit,CreditService
from django.db import connection

class DebtRegistrationView(LoginRequiredMixin,View):
    login_url = settings.LOGIN_URL
    def get(self,request,*args,**kwargs):
        form = DebtRegistrationForm()
        return render(request,'credits/debt_registration_form.html',{'form':form})
    def post(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)#get the logged in user
        form = DebtRegistrationForm(request.POST)
        if form.is_valid():
            credit_date = form.cleaned_data['credit_date']
            credit_agency = form.cleaned_data['credit_agency']
            amount = form.cleaned_data['amount']
            credit_service_date = form.cleaned_data['credit_service_date']
            comment=form.cleaned_data['comment']
            #add to the Credit Table
            credit = Credit()
            credit.credit_date = credit_date
            credit.credit_agency = credit_agency
            credit.amount = amount
            credit.credit_service_date = credit_service_date
            credit.comment = comment
            credit.user_id = user

            credit.save()#commit to the database
        else:
            return render(request,'credits/debt_registration_form.html',{'form':form})
        return redirect('debt_list')

class DebtServiceView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        login = settings.LOGIN_URL
        user = User.objects.get(username=self.request.user)
        form = DebtServiceForm(user)
        return render(request,'credits/debt_service_form.html',{'form':form})
    def post(self,request,*args,**kwargs):
        user =  User.objects.get(username=self.request.user)#get the logged in user
        form = DebtServiceForm(user,request.POST)
        if form.is_valid():
            debt_id = form.cleaned_data['debt_id']
            amount= form.cleaned_data['amount']
            comment = form.cleaned_data['comment']
            service_date = form.cleaned_data['service_date']
            creditService = CreditService()
            creditService.debt_id=debt_id
            creditService.service_date=service_date
            creditService.amount = amount
            creditService.comment = comment
            creditService.user_id = user
            creditService.save() # commit to the database
            with connection.cursor() as cursor:
                cursor.execute(f"""
                SELECT
                    sum(cs.amount) as total
                     FROM credits_creditservice cs
                     where cs.voided=0 and cs.debt_id_id={debt_id.id}
                """)
                columns = [col[0] for col in cursor.description]
                amount_paid = [dict(zip(columns,row)) for row in cursor.fetchall()]
                if len(amount_paid)>0:
                    amount_paid= amount_paid[0]['total']
                else:
                    amount_paid = 0
                if amount_paid == debt_id.amount:
                    debt_id.paid= 1
                    debt_id.save()
            return redirect('debt_list')
        return render(request,'credits/debt_service_form.html',{'form':form})


#list Debts Summary
class DebtSummaryView(LoginRequiredMixin,View):
    login = settings.LOGIN_URL
    def get(self,request,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        with connection.cursor() as cursor:
            cursor.execute(f"""
            select final.* 
            from(
            SELECT distinct
            c.id,
            c.credit_date,
            c.credit_agency,
            c.amount,
            c.credit_service_date,
            c.comment,
            c.paid,
            case when (c.paid == 0) and date(c.credit_service_date) < CURRENT_DATE
            then "Overdue"
            when (c.paid == 0) and (date(c.credit_service_date) >= CURRENT_DATE) then "In Progress"
            when c.paid=1 then "Debt Paid"
            else "" end as paying_status,
			date('now') as n,
		
            case when service.amount_paid == c.amount then "Fully Paid"
            when service.amount_paid is not null then "Partially Paid"
            else "Not Paid" end as service_status,
            case when service.amount_paid is NULL then 0
             else service.amount_paid end as amount_paid,
			 case when service.amount_paid is NULL then c.amount
			 else c.amount - service.amount_paid end as amount_remaining
             FROM credits_credit c
             left outer join (
             SELECT
             cs.debt_id_id,
             sum(cs.amount) as amount_paid
             FROM credits_creditservice cs
             where cs.voided=0
             group by cs.debt_id_id
             )service on c.id = service.debt_id_id
            where c.voided=0  and c.user_id_id={user_id}
            order by c.credit_date desc) final
            where final.amount_remaining > 0
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns,row)) for row in cursor.fetchall()]

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
            context ={
                'data':data,
                'debt': (debt_owed-debt_paid),
                'help_text':"PENDING"
                }
            return render(request,"credits/debt_summary_list.html",context)
    def post(self,request):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        post_data = request.POST['select']
        if post_data == "SETTLED":
            with connection.cursor() as cursor:
                cursor.execute(f"""
                        select final.* 
                        from(
                        SELECT distinct
                        c.id,
                        c.credit_date,
                        c.credit_agency,
                        c.amount,
                        c.credit_service_date,
                        c.comment,
                        c.paid,
                        case when (c.paid == 0) and date(c.credit_service_date) < CURRENT_DATE
                        then "Overdue"
                        when (c.paid == 0) and (date(c.credit_service_date) >= CURRENT_DATE) then "In Progress"
                        when c.paid=1 then "Debt Paid"
                        else "" end as paying_status,
                        date('now') as n,

                        case when service.amount_paid == c.amount then "Fully Paid"
                        when service.amount_paid is not null then "Partially Paid"
                        else "Not Paid" end as service_status,
                        case when service.amount_paid is NULL then 0
                         else service.amount_paid end as amount_paid,
                         case when service.amount_paid is NULL then c.amount
                         else c.amount - service.amount_paid end as amount_remaining
                         FROM credits_credit c
                         left outer join (
                         SELECT
                         cs.debt_id_id,
                         sum(cs.amount) as amount_paid
                         FROM credits_creditservice cs
                         where cs.voided=0
                         group by cs.debt_id_id
                         )service on c.id = service.debt_id_id
                        where c.voided=0  and c.user_id_id={user_id}
                        order by c.credit_date desc) final
                        where final.amount_remaining <=0
                        """)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        elif (post_data == 'PENDING'):
            with connection.cursor() as cursor:
                cursor.execute(f"""
                        select final.* 
                        from(
                        SELECT distinct
                        c.id,
                        c.credit_date,
                        c.credit_agency,
                        c.amount,
                        c.credit_service_date,
                        c.comment,
                        c.paid,
                        case when (c.paid == 0) and date(c.credit_service_date) < CURRENT_DATE
                        then "Overdue"
                        when (c.paid == 0) and (date(c.credit_service_date) >= CURRENT_DATE) then "In Progress"
                        when c.paid=1 then "Debt Paid"
                        else "" end as paying_status,
                        date('now') as n,

                        case when service.amount_paid == c.amount then "Fully Paid"
                        when service.amount_paid is not null then "Partially Paid"
                        else "Not Paid" end as service_status,
                        case when service.amount_paid is NULL then 0
                         else service.amount_paid end as amount_paid,
                         case when service.amount_paid is NULL then c.amount
                         else c.amount - service.amount_paid end as amount_remaining
                         FROM credits_credit c
                         left outer join (
                         SELECT
                         cs.debt_id_id,
                         sum(cs.amount) as amount_paid
                         FROM credits_creditservice cs
                         where cs.voided=0
                         group by cs.debt_id_id
                         )service on c.id = service.debt_id_id
                        where c.voided=0  and c.user_id_id={user_id}
                        order by c.credit_date desc) final
                        where final.amount_remaining > 0
                        """)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                        select final.* 
                        from(
                        SELECT distinct
                        c.id,
                        c.credit_date,
                        c.credit_agency,
                        c.amount,
                        c.credit_service_date,
                        c.comment,
                        c.paid,
                        case when (c.paid == 0) and date(c.credit_service_date) < CURRENT_DATE
                        then "Overdue"
                        when (c.paid == 0) and (date(c.credit_service_date) >= CURRENT_DATE) then "In Progress"
                        when c.paid=1 then "Debt Paid"
                        else "" end as paying_status,
                        date('now') as n,

                        case when service.amount_paid == c.amount then "Fully Paid"
                        when service.amount_paid is not null then "Partially Paid"
                        else "Not Paid" end as service_status,
                        case when service.amount_paid is NULL then 0
                         else service.amount_paid end as amount_paid,
                         case when service.amount_paid is NULL then c.amount
                         else c.amount - service.amount_paid end as amount_remaining
                         FROM credits_credit c
                         left outer join (
                         SELECT
                         cs.debt_id_id,
                         sum(cs.amount) as amount_paid
                         FROM credits_creditservice cs
                         where cs.voided=0
                         group by cs.debt_id_id
                         )service on c.id = service.debt_id_id
                        where c.voided=0  and c.user_id_id={user_id}
                        order by c.credit_date desc) final
                        """)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        with connection.cursor() as cursor:
            cursor.execute(f"""
                        SELECT sum(c.amount) as total_debt
                         FROM credits_credit c
                         where c.voided=0 and c.paid=0 and c.user_id_id={user_id}
                    """)
            columns = [col[0] for col in cursor.description]
            debt_owed = [dict(zip(columns, row)) for row in cursor.fetchall()]
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
            debt_paid = [dict(zip(columns, row)) for row in cursor.fetchall()]

        if len(debt_owed) > 0:
            debt_owed = debt_owed[0]['total_debt']
        else:
            debt_owed = 0
        if len(debt_paid) > 0:
            debt_paid = debt_paid[0]['debt_paid']
        else:
            debt_paid = 0
        if (debt_paid is None):
            debt_paid = 0
        if (debt_owed is None):
            debt_owed = 0
        context = {
            'data': data,
            'debt': (debt_owed - debt_paid),
            'help_text':post_data
        }
        return render(request, "credits/debt_summary_list.html", context)


class DebtServiceHistoryView(LoginRequiredMixin,View):
    login = settings.LOGIN_URL
    def get(self,request,pk,*args,**kwargs):
        user = User.objects.get(username=self.request.user)
        user_id = user.id
        debt_record = Credit.objects.get(pk=pk)
        #1.get the debt summary - amount and remaining amount
        #2.service history based on debt id
        # debt owed
        with connection.cursor() as cursor:
            cursor.execute(f"""
             SELECT distinct
            c.credit_date,
            c.credit_agency,
            c.amount,
            c.credit_service_date,
            c.comment,
            c.paid,
            case when (c.paid == 0) and cast(c.credit_service_date as date) > CURRENT_DATE
            then "Overdue"
            when (c.paid == 0) and (cast(c.credit_service_date as date) <= CURRENT_DATE) then "In Progress"
            when c.paid=1 then "Debt Paid"
            else "" end as paying_status,
            case when service.amount_paid == c.amount then "Fully Paid"
            when service.amount_paid is not null then "Partially Paid"
            else "Not Paid" end as service_status,
            case when service.amount_paid is NULL then 0
             else service.amount_paid end as amount_paid,
			 case when service.amount_paid is NULL then c.amount
			 else c.amount - service.amount_paid end as amount_remaining
             FROM credits_credit c
             left outer join (
             SELECT
             cs.debt_id_id,
             sum(cs.amount) as amount_paid
             FROM credits_creditservice cs
             where cs.voided=0
             group by cs.debt_id_id
             )service on c.id = service.debt_id_id
            where c.voided=0 and c.user_id_id={user_id} and c.id={pk}
            order by c.credit_date desc
            """)
            columns = [col[0] for col in cursor.description]
            debt = [dict(zip(columns,row)) for row in cursor.fetchall()]
            if len(debt) > 0:
                debt = debt[0]
            else:
                debt ={}

        debt_history = CreditService.objects.filter(voided=0,user_id=user,debt_id=debt_record)
        context ={
            'debt':debt,
            'data':debt_history,
            }
        return render(request,'credits/debt_history_form.html',context)




class UpdateDebtRegistrationView(LoginRequiredMixin,UpdateView):
    template_name="credits/update_debt_registration_form.html"
    model= Credit
    fields =["credit_date","credit_agency","amount","credit_service_date","comment"]
    pk_url_kwarg ="pk"
    success_url="/credits/debtlist/"
    login_url = settings.LOGIN_URL

class DeleteDebtRegistrationView(LoginRequiredMixin,View):
    template_name="credits/delete_debt_registration_form.html"
    model =Credit
    pk_url_kwarg="pk"
    success_url='/debtlist'
    login_url = settings.LOGIN_URL
    def get(self,request,pk,*args,**kwargs):
        object=get_object_or_404(Credit,pk=pk)
        return render(request,self.template_name,{"obj":object})
    def post(self,request,pk,*args,**kwargs):
        print(request.POST['delete'])
        if request.POST['delete'] == "delete":
            Credit.objects.filter(pk=pk).update(voided=1)
            return redirect('debt_list')
        else:
            return redirect('debt_list')


class UpdateDebtServiceView(LoginRequiredMixin,UpdateView):
    template_name="credits/update_debt_service_form.html"
    model= CreditService
    fields =["debt_id","service_date","amount","comment"]
    pk_url_kwarg ="pk"
    success_url="/credits/debtlist/"
    login_url = settings.LOGIN_URL

class DeleteDebtServiceView(LoginRequiredMixin,View):
    template_name="credits/delete_debt_service_form.html"
    model =CreditService
    pk_url_kwarg="pk"
    success_url='/credits/debtlist'
    login_url = settings.LOGIN_URL
    def get(self,request,pk,*args,**kwargs):
        object=get_object_or_404(self.model,pk=pk)
        return render(request,self.template_name,{"obj":object})
    def post(self,request,pk,*args,**kwargs):
        print(request.POST['delete'])
        if request.POST['delete'] == "delete":
            self.model.objects.filter(pk=pk).update(voided=1)
            return redirect('debt_list')
        else:
            return redirect('debt_list')