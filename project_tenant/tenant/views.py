from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib.auth.decorators import login_required
from django.core.paginator import (EmptyPage,
                                   PageNotAnInteger,
                                   Paginator)
from django.shortcuts import (HttpResponseRedirect,
                              render,
                              HttpResponse,
                              redirect,)
from django.http import JsonResponse
from django.urls import reverse

from tenant.decorators import (for_admin,
                               for_staff)
from tenant.forms import (AgentForm,
                          TenantRegistratonForm)
from tenant.models import (TblAgent,
                           TblAgentAllocation,
                           TblMasterProperty,
                           TblMasterPropertyClone,
                           TblProperty,
                           TblPropertyAllocation,
                           TblRentCollection,
                           TblTenant,
                           TblVisit
                           )

from django.db.models import (Prefetch,
                              Count,
                              Subquery,
                              OuterRef,
                              F,
                              Q,
                              prefetch_related_objects,
                              ExpressionWrapper,
                              CharField,
                              functions,
                              Value
                              )
from django.db.models.functions import Cast, Concat

from datetime import datetime,timedelta

# Create your views here.


#######################################################################################################################
# Basic views
#######################################################################################################################

# index view
def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            print('\n\nlogout\n\n')
            logout(request)
    return render(request, 'base.html')


# Requesting agent registration
def agent_registration(request):
    form = AgentForm()
    if request.method == 'POST':
        form = AgentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                agent = form.save(commit=False)
                agent.date_joined = request.POST.get('date_joined')
                agent.set_password(agent.password)
                agent.agent_save()
                return index(request)
            except Exception as e:
                print("Error:", e)
                print(form.errors)
        else:
            print(form.errors)
    return render(request, 'AgentRegistration.html', {'form': form})


# custom login for admin/agent
def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user:
        if user.is_superuser:
            # print("\n\n\n\n Admin \n",user,"\n\n\n")
            login(request, user)
            return HttpResponseRedirect(reverse(admin_index))
        elif user.is_staff:
            # print("\n\n\n\n Agent \n",user,"\n\n\n")
            login(request, user)
            return HttpResponseRedirect(reverse(agent_index))
        else:
            # print("\n\n\n\nInavlid user\n\n\n\n")
            return render(request, 'base.html')
    else:
        # print("\n\n\n\nInavlid user\n\n\n\n")
        return render(request, 'base.html')


#######################################################################################################################
# Common in admin and agent
#######################################################################################################################

# adding tenant by agent
# @login_required
# def add_tenant(request):
#     form = TenantRegistratonForm()
#     if request.method == 'POST':
#         form = TenantRegistratonForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 tenant = form.save(commit=False)
#                 tenant.tn_agent = request.user
#                 tenant.tn_joining_date = request.POST.get('date_joined')

#                 tenant.save()
#                 return index(request)
#             except Exception as e:
#                 print("Error:", e)
#                 print(form.errors)
#         else:
#             print(form.errors)

#     return render(request, 'agent/add_tenant.html', {'form': form})


#######################################################################################################################
# Admin site views
#######################################################################################################################

# Admin index view
@for_admin
def admin_index(request):
    return render(request, 'admin/base.html')

# Page Agent Requests..................................................................................................
# view all agent requests on admin site
@for_admin
def view_agent_request(request):
    # print('agents')
    try:
        # print('agents')
        agents = TblAgent.objects.filter(
            is_active=False, is_staff=False)\
            .order_by('first_name', 'last_name')

        print(agents)
    except Exception as e:
        print('Error at Agent Request', e)
        agents = None
    return render(request, 'admin/agent_requests.html',
                  {'agents': agents})

# accepting the agent request
@for_admin
def agent_request_accept(request):
    id = request.POST['id']
    agent = TblAgent.objects.get(id=id)
    agent.verified_save()
    return view_agent_request(request)

# deleting the agent request
@for_admin
def agent_request_reject(request):
    id = request.POST['id']
    TblAgent.objects.filter(id=id).delete()
    return view_agent_request(request)

# returning search result of agent requests.


def get_agents(starts_with=''):
    agents = []
    first_name = starts_with
    last_name = None
    if ' ' in starts_with:
        lst = starts_with.split(' ')
        first_name = lst[0]
        last_name = lst[1]

    if first_name:
        if last_name:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        last_name__istartswith=last_name,
                        is_active=False,
                        is_staff=False,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        else:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        is_active=False,
                        is_staff=False,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        print(agents)
    else:
        agents = TblAgent.objects\
            .filter(is_active=False,
                    is_staff=False,
                    is_superuser=False).order_by('first_name',
                                                 'last_name')
    return agents


# View the search result from agent requests
@for_admin
def agent_requests_search(request):
    agents = []
    starts_with = ''
    if request.method == 'GET':
        if 'suggestion' in request.GET.keys():
            starts_with = request.GET['suggestion']
        agents = get_agents(starts_with)

    return render(request, 'admin/agents.html', {'agents': agents, })


# End-Page Agent Requests...........................................................................................


# Page Agent View..................................................................................................
# view all agent requests on admin site
@for_admin
def view_agent_all(request):
    try:
        agents = TblAgent.objects.filter(
            is_staff=True, is_superuser=False).order_by('first_name',
                                                        'last_name')

    except Exception as e:
        agents = None
        print('Error at Agent Profile', e)
    return render(request, 'admin/agent_active.html',
                  {'agents': agents})


# activating deactivating agents status
@for_admin
def agent_action(request):
    agent = TblAgent.objects.get(id=request.GET['id'])
    act = request.GET['is_active']
    if act == '0':
        print('dealloacting all properties')
        try:
            allocation = TblAgentAllocation.objects.select_related(
                'al_master').filter(al_agent=request.GET['id'])
            print(allocation)
            for al in allocation:
                print(al.al_master.cln_alias)
                al.al_master.cln_is_allocated = False
                al.al_master.save()
            allocation.delete()
        except Exception as e:
            print('Error at deallocation', e)
    agent.is_active = act
    agent.save()
    return HttpResponseRedirect(reverse(view_agent_all))


# returning search result of Active Agents.
def get_active_agents(starts_with=''):
    agents = []
    first_name = starts_with
    last_name = None
    if ' ' in starts_with:
        lst = starts_with.split(' ')
        first_name = lst[0]
        last_name = lst[1]

    if first_name:
        if last_name:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        last_name__istartswith=last_name,
                        is_staff=True,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        else:
            agents = TblAgent.objects\
                .filter(first_name__istartswith=first_name,
                        is_staff=True,
                        is_superuser=False).order_by('first_name',
                                                     'last_name')
        print(agents)
    else:
        agents = TblAgent.objects\
            .filter(is_staff=True,
                    is_superuser=False).order_by('first_name',
                                                 'last_name')
    return agents


# View the search result from agent requests
@for_admin
def agent_active_search(request):
    agents = []
    starts_with = ''
    if request.method == 'GET':
        if 'suggestion' in request.GET.keys():
            starts_with = request.GET['suggestion']

        print("start", starts_with)
        agents = get_active_agents(starts_with)

    return render(request, 'admin/active_agents.html',
                  {'agents': agents, })

# End-Page Agent View..................................................................................................


# Page Agent profile View.......................................................................................
# Viewing the agent request in more detailed View
@for_admin
def agent_profile(request):
    print("\n\n\n\n\n\n")
    id = request.GET['id']
    agent = TblAgent.objects.get(id=id)

    details = TblAgentAllocation.objects\
        .select_related('al_master')\
        .select_related('al_master__cln_master')\
        .filter(al_agent=agent)\
        .annotate(
            properties=Count('al_master__tblproperty')
        )\
        .annotate(
            unallocated=Count(
                'al_master__tblproperty',
                filter=Q(al_master__tblproperty__pr_is_allocated=False))
        )\
        .annotate(
            allocated=Count(
                'al_master__tblproperty',
                filter=Q(al_master__tblproperty__pr_is_allocated=True))
        )\
        .order_by(
            'al_master__cln_master__msp_name',
            'al_master__cln_alias',
            '-al_master__cln_is_master_clone'
        )
    for detail in details:
        print("Master =", detail.al_master.cln_master.msp_name, end="\t")
        print("Clone =", detail.al_master.cln_alias, end="\t")
        print("Properties =", detail.properties, end="\t")
        print("Unallocated =", detail.unallocated, end="\t")
        print("Allocated =", detail.allocated, end="\n")

    return render(request, 'admin/agent_profile.html',
                  {'agent': agent, 'allocations': details})

# showing Allocation data of Agent
@for_admin
def show_data_agent(request):

    try:
        act = request.GET.get('act')
        id = request.GET.get('id')
        print(act)
        data = None
        if act == 'all_properties':
            data = TblProperty.objects\
                .filter(pr_master=id)\
                .order_by('pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)
        elif act == 'allocated_properties':

            data = TblPropertyAllocation.objects\
                .select_related('pa_tenant')\
                .select_related('pa_property')\
                .filter(pa_property__pr_master=id)\
                .order_by('pa_property__pr_address')
            for d in data:
                print(d.pa_property.pr_master.cln_alias,
                      d.pa_property.pr_address, d.pa_tenant.tn_name)

        elif act == 'unallocated_properties':
            data = TblProperty.objects\
                .select_related('pr_master')\
                .filter(pr_master=id, pr_is_allocated=False)\
                .order_by('pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)

        print(data)

        return render(request, 'admin/show_data.html',
                      {'rows': data, 'act': act, 'msp': id})
    except Exception as e:
        print("error ", e)
        return HttpResponse('''<div  style="color: red;
                                align: right; width: max-content; " >
                                <right>Something Went Wrong While
                                Fetching Requested data</right></div>''')


# End-Page Agent View..................................................................................................


# Page Add Master Property View.......................................................................................
# Creating Clone Input boxes according to user input
def create_clone_list(request):
    no = request.GET['clone_no']
    if no == '':
        no = 0
    return render(request, 'admin/clone_input_list.html',
                  {'no': range(1, int(no)+1)})

# Adding Master Property with or without clone..
@for_admin
def add_master_property(request):
    if request.method == "POST":
        try:
            # Creating new or taking Existing
            #  object for master property.
            msp = TblMasterProperty.objects.\
                get_or_create(msp_name=request.POST['msp_name'],
                              msp_address=request.POST['msp_address'],
                              msp_description=request.
                              POST['msp_description'],
                              msp_is_active=True)
            # Condition to check if new row is created or not.
            if msp[1]:
                # Saving the object and creating
                # master clone if new row created.
                msp[0].new_save()
                if 'msp_have_clones' in request.POST.keys():
                    no = int(request.POST['msp_clone_no'])
                    if request.POST['msp_have_clones']\
                            and no > 0 and no <= 50:
                        for n in range(1, no+1):
                            cln = TblMasterPropertyClone.objects\
                                .create(cln_alias=request.
                                        POST['msp_clone'+str(n)],
                                        cln_master=msp[0])
                            cln.save()
                return HttpResponseRedirect(
                    reverse(view_master_property))
            else:
                return render(request,
                              'admin/add_master_property.html',
                              {'context': 'Master Property already exists'})

        except Exception as e:
            print("Error :", e)
    else:
        return render(request, 'admin/add_master_property.html')
# End-Page Add master property View.................................................................................

# Page Add Poperty View............................................................................................
# Showing clone list of selected property
@for_admin
def clone_list(request):
    if request.GET.get('unallocated'):
        clones = TblMasterPropertyClone.objects.filter(
            cln_master=request.GET['msp'],
            cln_is_allocated=False).order_by('id')
    else:
        clones = TblMasterPropertyClone.objects.filter(
            cln_master=request.GET['msp']).order_by('id')
    return render(request, 'admin/clone_list.html', {'clones': clones})


# Viewing master property at admin side
@for_admin
def view_master_property(request):
    msp_list = TblMasterProperty.objects.all()\
        .annotate(
            no_of_clones=Count('tblmasterpropertyclone',
                               distinct=True))\
        .annotate(
            unallocated_clones=Count(
                'tblmasterpropertyclone', distinct=True,
                filter=Q(
                    tblmasterpropertyclone__cln_is_allocated=False)))\
        .annotate(
            allocated_clones=Count(
                'tblmasterpropertyclone', distinct=True,
                filter=Q(
                    tblmasterpropertyclone__cln_is_allocated=True)))\
        .annotate(
            no_of_property=Count(
                'tblmasterpropertyclone__tblproperty'))\
        .annotate(
            unallocated_properties=Count(
                'tblmasterpropertyclone__tblproperty',
                filter=Q(
                    tblmasterpropertyclone__tblproperty__pr_is_allocated=False)))\
        .annotate(
            allocated_properties=Count(
                'tblmasterpropertyclone__tblproperty',
                filter=Q(
                    tblmasterpropertyclone__tblproperty__pr_is_allocated=True)))

    # msp_list = ViewMasterProperties.objects.all()
    return render(request, 'admin/master_property_view.html',
                  {'master_property_list': msp_list})


# Adding new property in the database
@for_admin
def add_property(request):
    address_list = TblMasterProperty.objects.all()
    existing_addresses = []
    addeed_addresses = []
    if request.method == "POST":
        # A function to check if property alredy exists
        def is_property_exists(msp=None, add=None):
            is_exists = False
            clones = TblMasterPropertyClone.objects\
                .filter(cln_master=msp)
            for clone in clones:
                if TblProperty.objects\
                    .filter(pr_master=clone,
                            pr_address=add).exists():
                    is_exists = True
                    break
            return is_exists

        msp_id = request.POST['pr_msp']
        msp_clone_id = request.POST['pr_msp_clone']
        num = request.POST['pr_num']
        pr_rent = request.POST['pr_rent']
        pr_deposite = request.POST['pr_deposite']
        pr_description = request.POST['pr_description']
        msp = TblMasterProperty.objects.get(id=msp_id)
        msp_clone = TblMasterPropertyClone.objects.get(id=msp_clone_id)
        for n in range(int(num)):
            if 'pr_address'+str(n) in request.POST.keys():
                pr_address = request.POST['pr_address'+str(n)]
                if not is_property_exists(msp=msp, add=pr_address):
                    try:
                        obj = TblProperty.objects.\
                            create(pr_master=msp_clone,
                                   pr_address=pr_address,
                                   pr_rent=float(
                                       pr_rent),
                                   pr_deposite=float(
                                       pr_deposite),
                                   pr_description=pr_description,
                                   pr_is_active=True,
                                   pr_is_allocated=False)
                        obj.save()
                        addeed_addresses.append(pr_address)
                    except Exception as e:
                        print("\n\n\n\nError:", e)
                else:
                    existing_addresses.append(pr_address)
        if existing_addresses:
            context = ",".join(existing_addresses) +\
                " are alredy existing in <b><u>" + \
                msp.msp_name+"</u></b> Master Property."
        else:
            context = ''
        if addeed_addresses:
            success = ",".join(addeed_addresses) +\
                " are added in <b><u>"+msp_clone.cln_alias + \
                "</b></u> clone of <b><u>"+msp.msp_name +\
                "<b></u> Master Property."
        else:
            success = "No Property added to <b><u>" +\
                msp_clone.cln_alias + \
                "</u></b> clone of <b><u>"+msp.msp_name +\
                "</u></b> Master Property."
        return render(request, 'admin/add_property.html',
                      {'address_list': address_list,
                       'context': context,
                       'success': success})

    return render(request, 'admin/add_property.html',
                  {'address_list': address_list})
# End-Page Add property View.................................................................................

# Page View MAster Property.................................................................................
# showing data on admin page
@for_admin
def show_data(request):

    try:
        act = request.GET.get('act')
        id = request.GET.get('id')
        print(act)
        data = None
        if act == 'all_clones':
            data = TblMasterPropertyClone.objects.filter(cln_master=id)\
                .annotate(
                    properties=Count('tblproperty',
                                     Subquery(
                                         TblProperty.objects.filter(
                                             pr_master=OuterRef('pk')
                                         ).values('pr_master')
                                     )
                                     )
            ).order_by('-cln_is_master_clone', 'cln_alias')
            for d in data:
                print(d.properties)
        elif act == 'allocated_clones':
            data = TblAgentAllocation.objects\
                .select_related('al_agent')\
                .select_related('al_master')\
                .filter(al_master__cln_master=id,
                        al_master__cln_is_allocated=True
                        ).order_by(
                    '-al_master__cln_is_master_clone',
                    'al_master__cln_alias')

            for d in data:
                print(d.al_agent.username, d.al_master.cln_alias)
        elif act == 'unallocated_clones':
            data = TblMasterPropertyClone.objects\
                .filter(cln_master=id,
                        cln_is_allocated=False)\
                .order_by('-cln_is_master_clone', 'cln_alias')

            for d in data:
                print(d.cln_alias)
        elif act == 'all_properties':
            data = TblProperty.objects\
                .select_related('pr_master')\
                .filter(pr_master__cln_master=id)\
                .order_by('-pr_master__cln_is_master_clone',
                          'pr_master__cln_alias',
                          'pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)
        elif act == 'allocated_properties':

            data = TblPropertyAllocation.objects.select_related(
                'pa_tenant').select_related(
                    'pa_property').filter(
                        pa_property__pr_master__cln_master=id,
                        pa_is_allocated=True,
            ).order_by(
                '-pa_property__pr_master__cln_is_master_clone',
                'pa_property__pr_master__cln_alias',
                'pa_property__pr_address')
            for d in data:
                print(d.pa_property.pr_master.cln_alias,
                      d.pa_property.pr_address, d.pa_tenant.tn_name)
            # data = TblAgentAllocation.objects.select_related(
            #     'al_agent').select_related('al_master'
            #       ).filter(al_master__cln_master=id)
        elif act == 'unallocated_properties':
            data = TblProperty.objects\
                .select_related('pr_master')\
                .filter(pr_master__cln_master=id,
                        pr_is_allocated=False
                        ).order_by(
                    '-pr_master__cln_is_master_clone',
                    'pr_master__cln_alias',
                    'pr_address')

            for d in data:
                print(d.pr_master.cln_alias, d.pr_address)
        # data= TblMasterPropertyClone.objects\
        # .prefetch_related(Prefetch(

        # ))
        # data = TblAgentAllocation.objects\
        # .select_related('al_agent')\
        # .prefetch_related(Prefetch('al_master',
        #       queryset=TblMasterPropertyClone\
        # .objects.filter(cln_master=id,cln_is_allocated=True),
        #       to_attr='master'))
        # data = TblAgentAllocation.objects.select_related(
        #     'al_agent').select_related('al_master')\
        # .filter(al_master__cln_master=id)

        # .prefetch_related(Prefetch('al_master',
        #   queryset=TblMasterPropertyClone.objects\
        # .filter(cln_master=id
        #   ))).all()
        print(data)

        return render(request, 'admin/show_data.html',
                      {'rows': data, 'act': act, 'msp': id})
    except Exception as e:
        print("error ", e)
        return HttpResponse('''<div  style="color: red;
                                align: right; width: max-content; " >
                                <right>Something Went Wrong While
                                Fetching Requested data</right></div>''')

# Editing Property details
@for_admin
def edit_property(request):
    try:
        pr = TblProperty.objects.get(id=request.GET.get('id'))
        pr.pr_rent = request.GET.get('rent')
        pr.pr_deposite = request.GET.get('deposite')
        pr.pr_description = request.GET.get('description')
        pr.save()
        return HttpResponse("1")
    except Exception as e:
        print("error ", e)
        return HttpResponse("0")


# Deallocating property
@for_admin
def deallocate_clone(request):
    try:
        al = TblAgentAllocation.objects.get(id=request.GET.get('id'))
        al.al_master.cln_is_allocated = False
        al.al_master.save()
        al.delete()
        return HttpResponse("1")
    except Exception as e:
        print("error ", e)
        return HttpResponse("0")


# Deallocating property
@for_admin
def delete_clone(request):
    try:
        master_clone = TblMasterPropertyClone.objects\
            .get(cln_master=request.GET.get('msp'),
                 cln_is_master_clone=True)
        clone = TblMasterPropertyClone.objects\
            .get(id=request.GET.get('id'))
        TblProperty.objects.filter(pr_master=clone)\
            .update(pr_master=master_clone)
        clone.delete()
        return HttpResponse("1")
    except Exception as e:
        print("error ", e)
        return HttpResponse("0")

# Allocating Agent
@for_admin
def allocate_clone(request):

    if request.method == 'GET':
        obj_msp = TblMasterProperty.objects.all()
        obj_agent = TblAgent.objects.filter(
            is_active=True, is_staff=True, is_superuser=False)
        if 'msp' in request.GET.keys() and 'cln' in request.GET.keys():
            msp = TblMasterProperty.objects.\
                get(id=request.GET['msp'])
            cln = TblMasterPropertyClone.objects\
                .get(id=request.GET['cln'])
            return render(request, 'admin/agent_allocation.html',
                          {'obj_msp': obj_msp,
                           'obj_agent': obj_agent,
                           'msp': msp,
                           'cln': cln,
                           'agent': None})
        elif 'agent' in request.GET.keys():
            agent = TblAgent.objects.get(id=request.GET.get('agent'))
            return render(request, 'admin/agent_allocation.html',
                          {'obj_msp': obj_msp,
                           'obj_agent': obj_agent,
                           'msp': None,
                           'cln': None,
                           'agent': agent})
        else:
            return render(request, 'admin/agent_allocation.html',
                          {'obj_msp': obj_msp,
                           'obj_agent': obj_agent,
                           'msp': None,
                           'cln': None,
                           'agent': None})

    elif request.method == 'POST':
        try:
            # al_master=TblMasterProperty.objects\
            # .get(id=request.POST['pr_msp'])
            al_master = TblMasterPropertyClone.objects.get(
                id=request.POST['pr_msp_clone'])
            al_master.cln_is_allocated = True
            al_master.save()
            al_agent = TblAgent.objects.get(id=request.POST['agentx'])
            obj = TblAgentAllocation.objects.get_or_create(
                al_agent=al_agent, al_master=al_master)
            print(obj[1])
            obj[0].save()
            return HttpResponseRedirect(reverse(view_master_property))
        except Exception as e:
            print('Error ', e)
            return HttpResponseRedirect(reverse(view_master_property))
    else:
        HttpResponse("chutiyas hai tu")


# Deleting Master property
@for_admin
def delete_master_property(request):
    try:
        msp = TblMasterProperty.objects.get(id=request.GET.get('id'))
        tenants = TblPropertyAllocation.objects.select_related(
            'pa_tenant').select_related('pa_property')\
            .select_related('pa_property__pr_master').\
            filter(pa_property__pr_master__cln_master=msp)
        for tenant in tenants:
            tenant.pa_tenant.tn_status = 0
            tenant.pa_tenant.save()
            print(tenant.pa_tenant)
        msp.delete()
        return HttpResponse("1")
    except Exception as e:
        print('Error at Master property delete', e)
        return HttpResponse("0")


# Removing property from system
@for_admin
def property_soldout(request):
    obj_pr = TblProperty.objects.get(id=request.GET['pr_id'])
    try:
        obj_pr.pr_is_active = False
        obj_pr.pr_is_allocated = False
        obj_pr.save()
        pAllocation = TblPropertyAllocation.objects.get(
            pa_property=pobj, pa_is_allocated=True)
        print(type(pAllocation))
        pAllocation.pa_tenant.tn_status = 0
        pAllocation.pa_tenant.save()
        pAllocation.pa_is_allocated = False
        pAllocation.save()

    except Exception as e:
        print("Error: ", e)
    return HttpResponse("1")


# End-Page View master property .................................................................................

# Page Add Create Clone View....................................................................................
# creating new clone
@for_admin
def create_clone(request):
    msp_list = []
    if request.method == 'POST':
        obj_msp = TblMasterProperty.objects\
            .get(id=request.POST['pr_msp'])
        no = int(request.POST['msp_clone_no'])
        if no > 0 and no <= 50:
            for n in range(1, no+1):
                cln = TblMasterPropertyClone.objects.create(
                    cln_alias=request.POST.get('msp_clone'+str(n)),
                    cln_master=obj_msp,
                    cln_is_allocated=False,
                    cln_is_active=True)
                cln.save()

    else:
        msp_list = TblMasterProperty.objects.all()

    return render(request, 'admin/create_clone.html',
                  {'obj_msp': msp_list})


# End-Page Add Create Clone View..................................................................................

# Page manage Clone View.........................................................................................
# Moving property from one clone to another
@for_admin
def manage_clones(request):
    msp_list = []
    if request.method == 'POST':
        clone = request.POST['to_clone']
        properties = request.POST.getlist('move_to[]')
        for pr in properties:
            TblProperty.objects.filter(id=pr)\
                .update(pr_master=clone)
    # else:
    lst = request.POST.getlist('move_to[]')
    print(lst)
    lst = request.POST
    for l in lst.keys():
        print(l, "   ", lst[l])
    msp_list = TblMasterProperty.objects.all()

    return render(request, 'admin/manage_clones.html',
                  {'obj_msp': msp_list})


# showing properties of selected clone or master property
def show_properties(request):
    master = request.GET.get('id')
    is_master_property = request.GET.get('is_master')
    if is_master_property == "true":
        to_clone = request.GET['cln']
        data = TblProperty.objects.\
            select_related('pr_master')\
            .filter(pr_master__cln_master=master)\
            .exclude(pr_master=to_clone)\
            .order_by('-pr_master__cln_is_master_clone',
                      'pr_master__cln_alias',
                      'pr_address')
    else:
        data = TblProperty.objects.\
            select_related('pr_master')\
            .filter(pr_master=master)\
            .order_by('-pr_master__cln_is_master_clone',
                      'pr_master__cln_alias',
                      'pr_address')
    return render(request, 'admin/show_properties.html',
                  {'rows': data, })


# showing list of clones
def move_to_clone_list(request):
    clones = TblMasterPropertyClone.objects.filter(
        cln_master=request.GET['msp']).order_by('id')
    response = """move in clone:
                <select style="width:50%;" name="to_clone" class="form-data"
                 id="to_clone" placeholder="new hint">
                 <option value="" selected="selected">
                 Select Clone</option>
                """
    for clone in clones:
        response += "<option  value="+str(clone.id)+"> "\
            + clone.cln_alias+" </option>"
    response += "</select><br />"
    return HttpResponse(response)


# showing list of clones of selected master property
# excluding selected clone in move_to clone.
def move_from_clone_list(request):
    clones = TblMasterPropertyClone.objects\
        .filter(cln_master=request.GET['msp'])\
        .exclude(id=request.GET['cln']).order_by('id')
    response = """move from clone:
                <select style="width:50%;" name="from_clone" class="form-data"
                 id="from_clone" placeholder="new hint">
                 <option value="" selected="selected">
                 Select Clone</option>
                """
    for clone in clones:
        response += "<option  value="+str(clone.id)+"> "\
            + clone.cln_alias+" </option>"
    response += "</select><br />"
    return HttpResponse(response)

#######################################################################################################################
# Agent site views
#######################################################################################################################

# agent index view
@for_staff
def agent_index(request):

    return render(request, 'agent/base.html')

# view all  tenants of agent
@for_staff
def view_tenants(request):
    # data = TblPropertyAllocation.objects.all()\
    #     .select_related('pa_tenant')\
    #     .prefetch_related(
    #         Prefetch(
    #             'pa_property',
    #             queryset=TblProperty.objects.filter(pr_is_allocated=True),
    #             to_attr='property'
    #         )
    # )

    # tenantlist = TblTenant.objects.all()\
    #     .annotate(
    #         pr_address=Subquery(
    #             TblPropertyAllocation.objects.filter(
    #                 pa_tenant=OuterRef('pk'),
    #                 pa_is_allocated=True
    #             )
    #             .select_related('pa_property')
    #             .values('pa_property__pr_address')
    #         )
    # )
    tenantlist = TblTenant.objects.all()\
        .annotate(
            pr_address=Subquery(
                TblPropertyAllocation.objects.filter(
                    pa_tenant=OuterRef('pk'),
                    pa_is_allocated=True
                )
                .select_related('pa_property')
                .select_related('pa_property__pr_master__cln_master')
                .values('pa_property__pr_address',
                        'pa_property__pr_master__cln_master__msp_name',
                        'pa_property__pr_master__cln_master__msp_address')
                .annotate(
                    address=Concat(
                        'pa_property__pr_address',
                        Value(', '),
                        'pa_property__pr_master__cln_master__msp_name',
                        Value(', '),
                        'pa_property__pr_master__cln_master__msp_address'
                    )
                )
                .values('address'),
                output_field=CharField()
            )
    )
    # data = TblTenant.objects.all().tblproperty__set.all()
    # data = TblPropertyAllocation.objects.filter(
    #                 pa_is_allocated=True
    #             )\
    #             .select_related('pa_property')\
    #             .select_related('pa_property__pr_master__cln_master')\
    #             .values('pa_property__pr_address','pa_property__pr_master__cln_master__msp_name','pa_property__pr_master__cln_master__msp_address')\
    #             .annotate(
    #                 address=Concat(Cast('pa_property__pr_address',output_field=CharField()),
    #                 , Cast('pa_property__pr_master__cln_master__msp_name',output_field=CharField())
    #                 , Cast('pa_property__pr_master__cln_master__msp_address',output_field=CharField())

    #             ))

    # data = TblPropertyAllocation.objects.filter(
    #                 pa_is_allocated=True
    #             )\
    # .select_related('pa_property')\
    # .select_related('pa_property__pr_master__cln_master')\
    # .values('pa_property__pr_address','pa_property__pr_master__cln_master__msp_name','pa_property__pr_master__cln_master__msp_address')\
    # .annotate(
    #     address=Concat('pa_property__pr_address',Value(', ')
    #     ,'pa_property__pr_master__cln_master__msp_name',Value(', ')
    #     , 'pa_property__pr_master__cln_master__msp_address'

    # ))
    # print(data.values())
    # for d in tenantlist:
    #     print(d.tn_name, end='    ')
    #     if d.tn_status == 2 or d.tn_status == 3:
    #         print(d.pr_address)
    #     else:
    #         print('Property not allocated')
    # print(tenantlist.values())
    for d in tenantlist.values('tn_name', 'tn_contact', 'tn_status', 'pr_address'):
        print(d)
    # tenantlist = TblTenant.objects.filter(tn_agent=request.user)
    return render(request, 'agent/view_tenant.html',
                  {'tenantlist': tenantlist})

# Adding new tenant to system
@for_staff
def addTenant(request):
    form = TenantRegistratonForm()
    if request.method == 'POST':
        for k in request.POST.keys():
            print(k, "\t", request.POST[k])
        if 'update' in request.POST.keys():
            tenant = TblTenant.objects.get(id=request
                                           .POST['tn_id'])
            tenant.tn_contact = request\
                .POST['tn_contact']
            tenant.tn_permanent_address = request\
                .POST['tn_permanent_address']
            tenant.tn_is_active = True
            tenant.tn_document_description = request\
                .POST['tn_document_description']
            tenant.tn_reference_name = request\
                .POST['tn_reference_name']
            tenant.tn_reference_address = request\
                .POST['tn_reference_address']
            if 'tn_profile' in request.FILES.keys():
                tenant.tn_profile = request.FILES['tn_profile']
                # print("Data hai:",request.FILES['tn_profile'])
            if 'tn_document' in request.FILES.keys():
                tenant.tn_document = request.FILES['tn_document']
                # print("\n\nIsme bhi hai data",request.FILES['tn_document'])
            tenant.save()

        else:
            form = TenantRegistratonForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    tenant = form.save(commit=False)
                    tenant.tn_agent = request.user
                    tenant.tn_joining_date = request.POST\
                        .get('date_joined')
                    tenant.tn_name = request.POST['tn_name']
                    print("\n\n", request.POST['tn_name'])
                    tenant.tn_is_active = True
                    tenant.save()
                    print(tenant)
                    plist = TblProperty.objects\
                        .select_related('pr_master')\
                        .select_related('pr_master__cln_master')\
                        .filter(pr_is_active=True,
                                pr_is_allocated=False,
                                pr_master__in=TblAgentAllocation
                                .objects.filter(al_agent=request.user)
                                .values('al_master'))
                    print(plist.values())
                    context = {'tenant': tenant, 'plist': plist}
                    return render(request,
                                  'agent/add_visit.html',
                                  context)
                except Exception as e:
                    print("Error:", e)
                    print(form.errors)
            else:
                print(form.errors)

    return render(request, 'agent/add_tenant.html', {'form': form})


def invoke_tenant(request):
    if request.method == 'GET':
        tenant = TblTenant.objects.get(id=request.GET['tid'])
        tenant.__dict__.pop('_state')
        return JsonResponse(tenant.__dict__, safe=False)


def get_deactivated_tenant(request):
    tenantlist = TblTenant.objects.filter(tn_is_active=False,
                                          tn_agent=request.user)\
        .values('id', 'tn_name')
    print(tenantlist)
    return JsonResponse({'tenantlist': list(tenantlist)})

'''List of properties allocated to a perticular agent by admin'''
@for_staff
def allocated_property_list(request):
    allocated_mpr=[]
    allocated_pr=[]
    if 'propertytype' in request.GET.keys():
        propertytype=request.GET['propertytype']
        if propertytype == "Allocatedproperty":
            allocated_mpr = TblMasterProperty.objects.filter(pk__in=TblAgentAllocation.objects.filter(
            al_agent=request.user,
            al_master__in=TblProperty.objects.filter(pr_is_allocated=True).order_by('pr_master').distinct('pr_master').values('pr_master'))\
                .select_related('al_master').values('al_master__cln_master'))
        # print(allocated_mpr.values())

            allocated_pr = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation
                    .objects.filter(al_agent=request.user).values('al_master'),pr_is_allocated=True)
            print(allocated_pr.values())
           
        elif propertytype == "Unallocatedproperty":
            allocated_mpr = TblMasterProperty.objects.filter(pk__in=TblAgentAllocation.objects.filter(
            al_agent=request.user,
            al_master__in=TblProperty.objects.filter(pr_is_allocated=False).order_by('pr_master').distinct('pr_master').values('pr_master'))\
                .select_related('al_master').values('al_master__cln_master'))
            # print(allocated_mpr.values())

            allocated_pr = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation
                    .objects.filter(al_agent=request.user).values('al_master'),pr_is_allocated=False)
            print(allocated_pr.values())        
            
        elif propertytype == "all":
            allocated_mpr = TblMasterProperty.objects.filter(pk__in=TblAgentAllocation.objects.filter(
            al_agent=request.user,
            al_master__in=TblProperty.objects.all().order_by('pr_master').distinct('pr_master').values('pr_master'))\
                .select_related('al_master').values('al_master__cln_master'))
        # print(allocated_mpr.values())

            allocated_pr = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation
                    .objects.filter(al_agent=request.user).values('al_master'))
            print(allocated_pr.values())        
        return render(request,'agent/property.html',{'allocated_pr': allocated_pr, 'allocated_mpr': allocated_mpr,'propertytype':propertytype}) 

    allocated_mpr = TblMasterProperty.objects.filter(pk__in=TblAgentAllocation.objects.filter(
            al_agent=request.user,
            al_master__in=TblProperty.objects.all().order_by('pr_master').distinct('pr_master').values('pr_master'))\
                .select_related('al_master').values('al_master__cln_master'))
        # print(allocated_mpr.values())

    allocated_pr = TblProperty.objects\
            .select_related('pr_master')\
            .select_related('pr_master__cln_master')\
            .filter(
                pr_master__in=TblAgentAllocation
                .objects.filter(al_agent=request.user).values('al_master'))    
    # print(allocated_pr.values())        

    return render(request, 'agent/agent_property.html', {'allocated_pr': allocated_pr, 'allocated_mpr': allocated_mpr})







# @for_staff
# def rented_property_list(request):
#     allocated_pr = TblProperty.objects\
#                     .select_related('pr_master')\
#                     .select_related('pr_master__cln_master')\
#                     .filter(
#                         pr_master__in=TblAgentAllocation
#                         .objects.filter(al_agent=request.user).values('al_master'))

#     return render(request, 'agent/agent_property.html', {'allocated_pr': allocated_pr})


# '''view tenant Details'''


@for_staff
def TenantDetails(request, tid):
    history = {}
    tenant = {}
    count = 1
   
    tenant = TblTenant.objects.get(id=tid)
    history = TblPropertyAllocation.objects.filter(
        pa_tenant=tenant).select_related('pa_property__pr_master__cln_master')
    print(history.values())
    for h in history:
        if h.pa_is_allocated == True:
            count = 0
    return render(request, 'agent/view_tenant_detail.html', {'tenant': tenant, 'history': history, 'count': count, })
   

# redirect to agent home
# @for_staff
# def agent_index(request):
#     return render(request, 'TM_template/Agent/ag_home.html')


'''To make tenant deactivate'''


# @for_staff
# def change_tenant_status(request):
#     tenant = TblTenant.objects.get(id=request.POST['tid'])
#     try:
#         if tenant.tn_is_active == False:
#             tenant.tn_is_active = True
#         else:
#             tenant.tn_is_active = False
#         tenant.save()
#     except Exception as e:
#         print("\n\nErorr:----------->", e)
#     return view_tenants(request)

@for_staff
def tenant_search_result(request):
    tenantlist = []
    starts_with = ''
    try:
        if request.method == 'GET':
            if 'suggestion' in request.GET.keys():
                status = request.GET['status']
                user = request.user
                starts_with = request.GET['suggestion']
                tenantlist = tenant_search(request, starts_with, status)
            # print("\nTenant list:\n", tenantlist)
    except Exception as e:
        print(e)
    return render(request, 'agent/tenants.html', {'tenantlist': tenantlist, 'status': status})


@for_staff
def tenant_search(request, suggestion=None, status="all"):
    tn_list = []
    if suggestion:
        if status == 'all':
            tn_list = TblTenant.objects.filter(
                tn_name__istartswith=suggestion, tn_agent=request.user)
        elif status == "active":
            tn_list = TblTenant.objects.filter(
                tn_name__istartswith=suggestion, tn_agent=request.user, tn_is_active=True)
        elif status == "inactive":
            tn_list = TblTenant.objects.filter(
                tn_name__istartswith=suggestion, tn_agent=request.user, tn_is_active=False)
    else:
        if status == 'all':
            tn_list = TblTenant.objects.filter(tn_agent=request.user)
        elif status == 'active':
            tn_list = TblTenant.objects.filter(
                tn_agent=request.user, tn_is_active=True)
        elif status == 'inactive':
            tn_list = TblTenant.objects.filter(
                tn_agent=request.user, tn_is_active=False)
    return tn_list


@for_staff
def get_Tenant_list(request):
    if 'pid' in request.GET.keys():
        pobj = TblProperty.objects\
            .select_related('pr_master')\
            .select_related('pr_master__cln_master')\
            .get(pk=request.GET['pid'])
            

        Tenant_list = TblTenant.objects.filter(
            tn_is_active=True, tn_agent_id=request.user, tn_status=1)
        # print(Tenant_list)
        context = {'pobj': pobj,
                   'Tenant_list': Tenant_list, 'page': "pdetails"}
    elif 'tid' in request.GET.keys():
        ten = TblTenant.objects.get(id=request.GET['tid'],
                                    tn_is_active=True)
        if ten.tn_status == 2:
            prp = TblPropertyAllocation.objects\
                .select_related('pa_property')\
                .get(pa_tenant=ten, pa_is_allocated=True)
            context = {'ten': ten, 'prp': prp, 'page': "tdetails"}
        else:
            # Add filter for already allocated properties to the tenants.
            plist = TblVisit.objects.select_related('vs_property')\
                .select_related('vs_property__pr_master')\
                .select_related('vs_property__pr_master__cln_master')\
                .filter(
                vs_tenant=ten,
                vs_property__pr_is_allocated=False,
                vs_property__pr_is_active=True,
                vs_property__pr_master__in=TblAgentAllocation
                            .objects.filter(al_agent=request.user)
                            .values('al_master'),
            )\
                .distinct('vs_property')\
                .order_by('vs_property')
            # for p in plist:
            # print(p.msp_name)
            context = {'ten': ten, 'plist': plist, 'page': "tdetails"}
    else:
        Tenant_list = TblTenant.objects.filter(
            tn_is_active=True, tn_agent_id=request.user, tn_status=1)
        plist = TblProperty.objects\
            .select_related('pr_master')\
            .select_related('pr_master__cln_master')\
            .filter(
                pr_master__in=TblAgentAllocation.objects
                .filter(al_agent=request.user).values('al_master'),
                pr_is_active=True,
                pr_is_allocated=False)
        # agent_id=request.user, pr_is_active=True, pr_is_allocated=False)
        context = {'Tenant_list': Tenant_list, 'plist': plist, }
    return render(request, 'agent/allocate_property.html',
                  context)


@for_staff
def allocate_property(request):
    if request.method == 'POST':
        p = request.POST['page']
        # # print(p)
        # # print(type(p))
        tobj = TblTenant.objects.get(id=request.POST['tselect'])
        if tobj.tn_status == 2:
            for k in request.POST.keys():
                print(k, "\t", request.POST[k])
            allocation = TblPropertyAllocation.objects\
                .get(pk=request.POST['pselect'])
            print(type(allocation))
            allocation.pa_agreement_date = request\
                .POST['start_agreement_date']
            allocation.pa_agreement_end_date = request\
                .POST['end_agreement_date']
            allocation.pa_acceptance_letter = request\
                .FILES['pa_agreement_letter']
            allocation.pa_tenancy_agreement = request\
                .FILES['tenancy_agreement']
            allocation.pa_tenant.tn_status = 3
            allocation.pa_tenant.save()
            print(allocation.pa_tenant.tn_status)
            # breakpoint()
            # allocation.al_property.pr_is_allocated =
            # allocation.pa_final_rent = request.POST['final_rent'],
            allocation.save()
        else:
            objp = TblProperty.objects.get(id=request.POST['pselect'])
            # print(objp)

            # print(tobj)
            try:
                allocation = TblPropertyAllocation.objects.create(
                    pa_property=objp,
                    pa_tenant=tobj,
                    pa_agreement_date=request
                    .POST['start_agreement_date'],
                    pa_agreement_end_date=request
                    .POST['end_agreement_date'],
                    pa_acceptance_letter=request
                    .FILES['pa_agreement_letter'],
                    pa_tenancy_agreement=request
                    .FILES['tenancy_agreement'],
                    pa_final_rent=request.POST['final_rent'],
                    pa_is_allocated=True)
                allocation.save()
                objp.pr_is_allocated = True
                objp.save()
                tobj.tn_status = 3
                tobj.save()
            except Exception as e:
                print("\n\nError: ", e)

        if p == "pdetails":
            return HttpResponseRedirect(
                reverse(allocated_property_list))
        if p == "tdetails":
            return HttpResponseRedirect(reverse(view_tenants))
    return get_Tenant_list(request)


@for_staff
def deallocate_property(request):
    if 'tenant' in request.GET.keys():
        try:
            tid = request.GET['tenant']
            tobj = TblTenant.objects.get(id=tid)
            tobj.tn_status = 0
            tobj.save()
            pAllocation = TblPropertyAllocation.objects.get(
                pa_tenant=tobj, pa_is_allocated=True)
            pAllocation.pa_property.pr_is_allocated = False
            pAllocation.pa_property.save()
            pAllocation.pa_is_allocated = False
            pAllocation.save()
            return HttpResponse("1")
        except Exception as e:
            print("Error ", e)
    if 'property' in request.GET.keys():
        try:
            pid = request.GET['property']
            print("\n\n", pid, "\n\n")
            pobj = TblProperty.objects.get(id=pid)
            print(type(pobj))
            TblProperty.objects.filter(id=pid).update(
                pr_is_allocated=False)
            pAllocation = TblPropertyAllocation.objects.get(
                pa_property=pobj, pa_is_allocated=True)
            print(type(pAllocation))
            pAllocation.pa_tenant.tn_status = 0
            pAllocation.pa_tenant.save()
            pAllocation.pa_is_allocated = False
            pAllocation.save()
            return HttpResponse("1")
        except Exception as e:
            print("Error ", e)
    return HttpResponse("0")


@for_staff
def get_tenant_visit(request):
    id = request.GET.get('id')
    visits = TblVisit.objects.select_related('vs_property')\
        .select_related('vs_property__pr_master__cln_master')\
        .filter(vs_tenant=id,
                vs_property__pr_is_allocated=False,
                vs_property__pr_is_active=True,
                vs_property__pr_master__in=TblAgentAllocation
                .objects.filter(al_agent=request.user)
                .values('al_master'),
                )\
        .distinct('vs_property')\
        .order_by('vs_property')
    # TblVisit.objects.select_related('vs_property')\
    #         .select_related('vs_property__pr_master')\
    #         .select_related('vs_property__pr_master__cln_master')\
    #         .filter(
    #         vs_tenant=ten,
    #         vs_property__pr_is_allocated=False,
    #         vs_property__pr_is_active=True,
    #         vs_property__pr_master__in=TblAgentAllocation
    #                     .objects.filter(al_agent=request.user)
    #                     .values('al_master'),
    #     )\
    #         .distinct('vs_property')\
    #         .order_by('vs_property')
    if visits.first() is not None:
        response = """<option value="" selected="selected">
                    Select Proerty</option>
                    """
        for visit in visits:
            response += "<option  value="+str(visit.vs_property.id)\
                + "> " + visit.vs_property.pr_address+" " \
                + visit.vs_property.pr_master.cln_master.msp_name + " "\
                + visit.vs_property.pr_master.cln_master.msp_address + " | Rent: "+  str(visit.vs_property.pr_rent)\
                + " </option>"
        return HttpResponse(response)
    else:
        return HttpResponse(0)


@for_staff
def change_tenant_status(request):
    tenant = TblTenant.objects.get(id=request.POST['tid'])

    try:
        if tenant.tn_is_active == False:
            tenant.tn_is_active = True
            tenant.save()
        else:
            tenant.tn_is_active = False
            tenant.tn_status = 0
            tenant.save()
            pAllocation = TblPropertyAllocation.objects.get(
                pa_tenant=tenant, pa_is_allocated=True)
            pAllocation.pa_property.pr_is_allocated = False
            pAllocation.pa_property.save()
            pAllocation.pa_is_allocated = False
            pAllocation.save()
    except Exception as e:
        print("\n\nErorr:----------->", e)
    return HttpResponseRedirect(reverse(view_tenants))


@for_staff
def add_visit(request):

    if request.method == 'GET':
        if 'tid' in request.GET.keys():
            # print(request.GET['tid'])
            tenant = TblTenant.objects.get(id=request.GET['tid'])
            plist = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation.objects
                    .filter(al_agent=request.user).values('al_master'),
                    pr_is_active=True,
                    pr_is_allocated=False)
            context = {'tenant': tenant, 'plist': plist}
        else:
            tlist = TblTenant.objects.filter(
                tn_is_active=True, tn_agent_id=request.user)
            plist = TblProperty.objects\
                .select_related('pr_master')\
                .select_related('pr_master__cln_master')\
                .filter(
                    pr_master__in=TblAgentAllocation.objects
                    .filter(al_agent=request.user).values('al_master'),
                    pr_is_active=True,
                    pr_is_allocated=False)
            context = {'tlist': tlist, 'plist': plist}
        return render(request, 'agent/add_visit.html',
                      context)
    if request.method == 'POST':
        tenant = TblTenant.objects.get(id=request.POST['selectedtn'])
        if tenant.tn_status == 0:
            tenant.tn_status = 1
            tenant.save()
        prop = TblProperty.objects.get(id=request.POST['selectedpr'])
        TblVisit.objects.create(vs_tenant=tenant,
                                vs_property=prop,
                                vs_date=request.POST['visitdate'],
                                vs_intrest_status=request.
                                POST['selectedin'])
        return HttpResponseRedirect(reverse(view_tenants))
    else:
        agent_index(request)


def change_status(request):
    if request.method == 'GET':
        for k in request.GET.keys():
            print(k, "  ", request.GET[k])

        try:
            tenant = TblTenant.objects.get(pk=request.GET['id'])
            status = request.GET['status']
            current_status = tenant.tn_status
            if status == '0':
                if current_status == 1:
                    tenant.tn_status = '0'
                    tenant.save()
                elif current_status in [2, 3]:
                    allocation = TblPropertyAllocation.objects.get(
                        pa_tenant=tenant,
                        pa_is_allocated=True,
                    )
                    allocation.pa_property.pr_is_allocated = False
                    allocation.pa_property.save()
                    allocation.pa_tenant.tn_status = '0'
                    allocation.pa_tenant.save()
                    allocation.pa_is_allocated = False
                    allocation.save()
                return HttpResponse("1")
            elif status == '2':
                if request.GET['update'] == 'true':
                    allocation = TblPropertyAllocation.objects.get(
                        pa_tenant=tenant,
                        pa_is_allocated=True,
                    )
                    new_allocation = allocation
                    new_allocation.pk = None
                    new_allocation.pa_agreement_date = None
                    new_allocation.pa_agreement_date_end = None
                    new_allocation.pa_acceptance_letter = None
                    new_allocation.pa_tenancy_agreement = None
                    new_allocation.pa_final_rent = None
                    new_allocation.save()

                    # allocation.pa_property.pr_is_allocated = False
                    # allocation.pa_property.save()
                    allocation.pa_tenant.tn_status = '2'
                    allocation.pa_tenant.save()
                    allocation.pa_is_allocated = False
                    allocation.save()
                else:
                    prp = TblProperty.objects\
                        .get(pk=request.GET['property'])
                    allocation = TblPropertyAllocation.objects\
                        .create(
                            pa_property=prp,
                            pa_tenant=tenant,
                            pa_is_allocated=True,
                            pa_final_rent=request.GET['rent']
                        )
                    allocation.save()
                    prp.pr_is_allocated = True
                    prp.save()
                    tenant.tn_status = 2
                    tenant.save()

                return HttpResponse("1")

        except Exception as e:
            print('Error in updating the ststus of tenant.', e)
            return HttpResponse("0")


def view_visit(request):
    data = TblVisit.objects.all().dates('vs_date','month',order='DESC')\
        .distinct('datefield').order_by('datefield').values('datefield')
    print(data.values('datefield'))
    visits = TblVisit.objects.all().select_related('vs_tenant')\
        .select_related('vs_property')\
        .annotate(
            vs_address=Subquery(
                TblProperty.objects.filter(
                    pk=OuterRef('vs_property')
                )
                .select_related('pr_master__cln_master')
                .values('pr_address',
                        'pr_master__cln_master__msp_name',
                        'pr_master__cln_master__msp_address')
                .annotate(
                    address=Concat(
                        'pr_address',
                        Value(', '),
                        'pr_master__cln_master__msp_name',
                        Value(', '),
                        'pr_master__cln_master__msp_address'
                    )
                )
                .values('address'),
                output_field=CharField()
            )
    )
    allocated_visits = TblVisit.objects.filter(
        vs_property__pr_is_allocated=True)\
        .select_related('vs_tenant')\
        .select_related('vs_property')\
        .annotate(
            vs_address=Subquery(
                TblProperty.objects.filter(
                    pk=OuterRef('vs_property')
                )
                .select_related('pr_master__cln_master')
                .values('pr_address',
                        'pr_master__cln_master__msp_name',
                        'pr_master__cln_master__msp_address')
                .annotate(
                    address=Concat(
                        'pr_address',
                        Value(', '),
                        'pr_master__cln_master__msp_name',
                        Value(', '),
                        'pr_master__cln_master__msp_address'
                    )
                )
                .values('address'),
                output_field=CharField()
            )
    )
    unallocated_visits = TblVisit.objects.filter(
        vs_property__pr_is_allocated=False)\
        .select_related('vs_tenant')\
        .select_related('vs_property')\
        .annotate(
            vs_address=Subquery(
                TblProperty.objects.filter(
                    pk=OuterRef('vs_property')
                )
                .select_related('pr_master__cln_master')
                .values('pr_address',
                        'pr_master__cln_master__msp_name',
                        'pr_master__cln_master__msp_address')
                .annotate(
                    address=Concat(
                        'pr_address',
                        Value(', '),
                        'pr_master__cln_master__msp_name',
                        Value(', '),
                        'pr_master__cln_master__msp_address'
                    )
                )
                .values('address'),
                output_field=CharField()
            )
    )

    # print(visits.values())
    return render(request, 'agent/view_visit.html',
                  {'visits': visits,
                   'allocated_visits': allocated_visits,
                   'unallocated_visits': unallocated_visits})

@for_staff
def getrent(request):
    rent = TblProperty.objects.get(id=request.GET['pid'])
    print(rent.pr_rent)
    return HttpResponse(rent.pr_rent)

@for_staff
def add_rent_collected(request):
    last_paid = None
    if request.method == 'GET':
        if 'pid' in request.GET.keys():
            propertyobj=TblPropertyAllocation.objects.select_related('pa_property').select_related('pa_tenant').get(pa_property=request.GET['pid'],pa_is_allocated=True)
            
        elif 'tid' in request.GET.keys():
            propertyobj=TblPropertyAllocation.objects.select_related('pa_property').select_related('pa_tenant').get(pa_tenant=request.GET['tid'],pa_is_allocated=True)

        # print("\n\nProperty:",propertyobj.id)    
        rentdetails=TblRentCollection.objects.filter(rc_allocation=propertyobj)
        # length = (len(rentdetails.values()))
        print("\n\nRent Details:",rentdetails)
        # diff_month=(propertyobj.pa_agreement_end_date,propertyobj.pa_agreement_date)
        
        i=propertyobj.pa_agreement_date
        # print("start",i)
        # print("end",propertyobj.pa_agreement_end_date)
        months=[]
        delta = timedelta(days=30)
        while i < propertyobj.pa_agreement_end_date:
            # print("i",i)
            months.append(i.strftime("%B, %Y"))
            # print(i.strftime("%B")) 
            i+=delta
        result=[]
        
        recorded = False
        for m in months:
            # print("\n\naya")
            # print(len(rentdetails))
            if (len(rentdetails.values()) > 0):
                rent=False
                for r in rentdetails:
                    print("\n\naya")
                    if m == r.rc_month.strftime("%B, %Y"):
                        rent=True
                        # print("Except")
                        # # last_paid = r.rc_month
                        # # last_paid += delta 
                        break
                if rent:
                    result.append([m,"Paid"])
                else:
                    if not recorded:
                        last_paid = datetime.strptime(m,"%B, %Y")
                        recorded = True
                    result.append([m,"Unpaid"])
                    
            else:
                result.append([m,"Unpaid"])
                if not last_paid:
                    last_paid = datetime.strptime(m,"%B, %Y")
        print(result)        
        if last_paid is not None:
            last_paid = last_paid.strftime("%B, %Y") 
        
        return render(request,'agent/add_rent.html',{'propertyobj':propertyobj,'rentdetails':rentdetails,'months':result, 'last_paid':last_paid})
    
    elif request.method == 'POST':
        for k in request.POST.keys():
            print(k, "\t", request.POST[k])
        for k in request.FILES.keys():
            print(k, "\t", request.FILES[k])  
        print(type(request.POST['payofmonth']))
        paymonth=datetime.strptime(request.POST['payofmonth'],"%B, %Y")
        print(paymonth)
        print(type(paymonth))
        allocation=TblPropertyAllocation.objects.get(id=request.POST['allocationid'])
        # print(allocation.id)
        addrent=TblRentCollection.objects.create(rc_allocation=allocation,rc_recipt_no=request.POST['reciptno'],rc_recipt=request.FILES['reciptpic'],rc_month=paymonth,rc_pay_off_date=datetime.now())
        addrent.save()
        return redirect('/agent/add_rent/?pid='+str(allocation.pa_property.id))

@for_staff
def check_allocation(request):
    if 'pid' in request.GET.keys():
            propertyobj=TblPropertyAllocation.objects.select_related('pa_property').select_related('pa_tenant').get(pa_property=request.GET['pid'],pa_is_allocated=True)
            if propertyobj.pa_tenant.tn_status == 3:
                return HttpResponse("1")
            else:
                return HttpResponse("0")
            
