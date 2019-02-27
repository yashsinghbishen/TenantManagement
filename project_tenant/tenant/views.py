from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import HttpResponseRedirect, render, HttpResponse
from django.urls import reverse

from tenant.decorators import for_admin, for_staff
from tenant.forms import AgentForm, TenantRegistratonForm
from tenant.models import (TblAgent, TblAgentAllocation, TblMasterProperty,
                           TblMasterPropertyClone, TblProperty,
                           TblPropertyAllocation, TblRentAllocation, TblTenant,
                           TblVisit, ViewMasterProperties)

from django.db.models import Prefetch, Count, Subquery, OuterRef

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
@login_required
def add_tenant(request):
    form = TenantRegistratonForm()
    if request.method == 'POST':
        form = TenantRegistratonForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                tenant = form.save(commit=False)
                tenant.tn_agent = request.user
                tenant.tn_joining_date = request.POST.get('date_joined')
                tenant.save()
                return index(request)
            except Exception as e:
                print("Error:", e)
                print(form.errors)
        else:
            print(form.errors)

    return render(request, 'agent/add_tenant.html', {'form': form})


#######################################################################################################################
# Admin site views
#######################################################################################################################

# Admin index view
@for_admin
def admin_index(request):
    return render(request, 'admin/base.html')

# -Page Agent Requests..................................................................................................
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


# Viewing the agent request in more detailed View
@for_admin
def agent_profile(request):
    id = request.POST['id']
    agent = TblAgent.objects.get(id=id)
    return render(request, 'admin/agent_profile.html',
                  {'agent': agent})


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


# -Page Agent View..................................................................................................
# view all agent requests on admin site
@for_admin
def view_agent_all(request):
    try:
        agents = TblAgent.objects.filter(
            is_staff=True, is_superuser=False).order_by('first_name',
                                                        'last_name')

    except Exception as e:
        agents = None
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


# -Page Add Master Property View.......................................................................................
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
                              msp_description=request.POST['msp_description'],
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

# -Page Add Poperty View............................................................................................
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
    msp_list = ViewMasterProperties.objects.all()
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

# -Page View MAster Property.................................................................................
# showing data on admin page
@for_admin
def show_data(request):

    try:
        act = request.GET.get('act')
        id = request.GET.get('id')
        print(act)
        data = None
        if act == 'all_clones':
            # data = TblMasterPropertyClone.objects.filter(
            #     cln_master=id).order_by(
            # '-cln_is_master_clone','cln_alias')

            # data = TblMasterPropertyClone.objects.prefetch().filter(
            #     cln_master=id).values('clone')\
            # .order_by('-cln_is_master_clone','cln_alias')

            # data = TblProperty.objects\
            #     .values('pr_master')\
            #     .filter(pr_master__cln_master=id)\
            #         .annotate(properties = Count('id',
            # distinct=True))\
            #             .group_by('pr_master__id')

            # data = TblMasterPropertyClone.objects\
            # .filter(cln_master=id)\
            #     .prefetch_related(Prefetch(
            #         queryset=Tbl

            #     )).order_by('-cln_is_master_clone','cln_alias')

            # properties = TblProperty.objects.all()
            # data = TblMasterPropertyClone.objects\
            # .filter(id__in=Subquery(properties.values('pr_master')))

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
                        pa_property__pr_master__cln_master=id
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


# End-Page View master property .................................................................................

# -Page Add Create Clone View....................................................................................
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

# -Page manage Clone View.........................................................................................
# creating new clone
@for_admin
def manage_clones(request):
    msp_list = []
    # if request.method =='POST':
    #     obj_msp=TblMasterProperty.objects\
    # .get(id=request.POST['pr_msp'])
    #     no = int(request.POST['msp_clone_no'])
    #     if no > 0 and no <= 50:
    #         for n in range(1, no+1):
    #             cln = TblMasterPropertyClone.objects.create(
    #                 cln_alias=request.POST.get('msp_clone'+str(n)),
    #                 cln_master=obj_msp,
    #                 cln_is_allocated=False,
    #                 cln_is_active=True)
    #             cln.save()

    # else:
    lst = request.POST.getlist('move_to[]')
    print(lst)
    lst = request.POST
    for l in lst.keys():
        print(l, "   ", lst[l])
    msp_list = TblMasterProperty.objects.all()

    return render(request, 'admin/manage_clones.html',
                  {'obj_msp': msp_list})


def show_properties(request):
    master = request.GET.get('id')
    is_master_property = request.GET.get('is_master')
    if is_master_property:
        data = TblProperty.objects.\
            select_related('pr_master')\
            .filter(pr_master__cln_master=master)\
            .order_by('-pr_master__cln_is_master_clone',
                      'pr_master__cln_alias',
                      'pr_address')
        # print(data.values())
    return render(request, 'admin/show_properties.html',
     {'rows': data, })


def move_to_clone_list(request):
    clones = TblMasterPropertyClone.objects.filter(
        cln_master=request.GET['msp']).order_by('id')
    response = """Select Clone to move:
                <select name="pr_msp_clone" class="form-data"
                 id="cln_list" placeholder="new hint">
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


def allocate_msp(request, msp_id=None):
    obj_msp = TblMasterProperty.objects.get(id=msp_id)
    obj_agent = []
    if request.method == 'POST':
        al_master = TblMasterProperty.objects.get(id=request.POST['msp'])
        al_agent = TblAgent.objects.get(id=request.POST['agentx'])
        obj = TblAgentAllocation.objects.get_or_create(
            al_agent=al_agent, al_master=al_master)
        obj[0].save()
        return HttpResponseRedirect(reverse(adminhome))

    obj_agent = TblAgent.objects.filter(
        is_active=True, is_staff=True, is_superuser=False)
    return render(request, 'admin/allocate_m_roperty.html',
                  {'obj_msp': obj_msp, 'obj_agent': obj_agent})
