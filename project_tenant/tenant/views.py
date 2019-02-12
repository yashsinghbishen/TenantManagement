from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse

from tenant.decorators import for_admin, for_staff
from tenant.forms import AgentForm, TenantRegistratonForm
from tenant.models import (TblAgent, TblAgentAllocation, TblMasterProperty,
                           TblMasterPropertyClone, TblProperty,
                           TblPropertyAllocation, TblRentAllocation, TblTenant,
                           TblVisit)

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

# view all agent requests on admin site
@for_admin
def view_agent_request(request):
    # print('agents')
    try:
        # print('agents')
        agents = TblAgent.objects.filter(
            is_active=False, is_staff=False).order_by('first_name', 'last_name')
        page = request.GET.get('page', 1)
        paginator = Paginator(agents, 2)
        agents = paginator.page(page)
        print(agents)
    except Exception as e:
        print('errror aayi hai bhai', e)
        agents = None
    return render(request, 'admin/agent_requests.html', {'agents': agents})


# view all agent requests on admin site
@for_admin
def view_agent_all(request):
    try:
        agents = TblAgent.objects.filter(
            is_staff=True, is_superuser=False).order_by('first_name', 'last_name')

        page = request.GET.get('page', 1)
        paginator = Paginator(agents, 2)
        agents = paginator.page(page)
    except Exception as e:
        agents = None
    return render(request, 'admin/agent_active.html', {'agents': agents})


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
    return render(request, 'admin/agent_profile.html', {'agent': agent})

# activating deactivating agents status
@for_admin
def agent_action(request):
    agent = TblAgent.objects.get(id=request.GET['id'])
    agent.is_active = request.GET['is_active']
    agent.save()
    return HttpResponseRedirect(reverse(view_agent_all))

# returning search result of agent requests.


def get_agents(starts_with=''):
    agents = []
    if starts_with:
        agents = TblAgent.objects.filter(first_name__istartswith=starts_with,
                                         is_active=False,
                                         is_staff=False).order_by('first_name',
                                                                  'last_name')
        print(agents)
    else:
        agents = TblAgent.objects.filter(is_active=False,
                                         is_staff=False).order_by('first_name',
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
        page = request.GET.get('page', 1)
        paginator = Paginator(agents, 2)
        agents = paginator.page(page)

    return render(request, 'admin/agents.html', {'agents': agents, "suggestion": starts_with})


# Creating Clone Input boxes according to user input 
def create_clone_list(request):
    no = request.GET['clone_no']
    if no == '':
        no = 0
    return render(request, 'admin/clone_input_list.html', {'no':range(1,int(no)+1)})

# Adding Master Property with or without clone..
@for_admin
def add_master_property(request):
    if request.method == "POST":
        try:
            #Creating new or taking Existing object for master property.
            msp = TblMasterProperty.objects.get_or_create(msp_name=request.POST['msp_name'],
                                                  msp_address=request.POST['msp_address'],
                                                  msp_description=request.POST['msp_description'],
                                                  msp_is_allocated=False,
                                                  msp_is_active=True)
            # Condition to check if new row is created or not.
            if msp[1]:
                #Saving the object and creating master clone if new row created.
                msp[0].new_save()
                no = int(request.POST['msp_clone_no'])
                if request.POST['msp_have_clones'] and no > 0 and no <= 5 :
                    for n in range(1,no+1):
                        cln = TblMasterPropertyClone.objects.create(
                            cln_alias = request.POST['msp_clone'+str(n)],
                            cln_master=msp[0] )
                        cln.save()
                return admin_index(request)
            else:
                return render(request, 'admin/add_master_property.html',
                {'context':'Master Property already exists'})
                
        except Exception as e:
            print("Error :", e)
    else:
        return render(request, 'admin/add_master_property.html')



# Creating Clone Input boxes according to user input 
@for_admin
def clone_list(request):
    clones = TblMasterPropertyClone.objects.filter(cln_master=request.GET['msp']).order_by('id')
    return render(request, 'admin/clone_list.html', {'clones':clones})

# Adding new property in the database
def add_property(request):
    address_list = []
    if request.method == "POST":
        pr_master = TblProperty.objects.get(id=request.POST['msp'])
        pr_address = request.POST['paddress']
        pr_rent = request.POST['prent']
        pr_deposite = request.POST['pdeposite']
        pr_is_allocated = False
        pr_is_active = True
        try:
            obj = TblProperty.objects.create(pr_master=pr_master,
                                             pr_address=pr_address,
                                             pr_rent=pr_rent,
                                             pr_deposite=pr_deposite,
                                             pr_is_active=pr_is_active,
                                             pr_is_allocated=pr_is_allocated)
            obj.save()
            return admin_index(request)
        except Exception as e:
            print("Error:", e)
    else:
        address_list = TblMasterProperty.objects.all()
    return render(request, 'admin/add_property.html', {'address_list': address_list})



#######################################################################################################################
# Agent site views
#######################################################################################################################

# agent index view
@for_staff
def agent_index(request):
    return render(request, 'agent/base.html')



def master_property_view(request):
    try:
        master_property_list = TblMasterProperty.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(master_property_list, 2)
        master_property_list = paginator.page(page)
    except PageNotAnInteger:
        master_property_list = paginator.page(1)
    except EmptyPage:
        master_property_list = paginator.page(paginator.num_pages)
    except Exception as e:
        master_property_list = None
        print('----> Error :', e)
    master_property_list = TblMasterProperty.objects.all()
    allocated_mp = TblAgentAllocation.objects.all()
    return render(request, 'admin/master_property_view.html',
                  {'master_property_list': master_property_list,
                   'allocated_mp': allocated_mp})


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


def master_property_soldout(request, msp_id):
    obj_msp = TblMasterProperty.objects.get(id=msp_id)
    try:
        obj_msp.msp_is_active = False
        obj_msp.save()

    except Exception as e:
        print("Error: ", e)
    return HttpResponseRedirect(reverse(master_property_view))


def property_listview(request):
    try:
        property_list = TblProperty.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(property_list, 2)
        property_list = paginator.page(page)
    except PageNotAnInteger:
        property_list = paginator.page(1)
    except EmptyPage:
        property_list = paginator.page(paginator.num_pages)
    except Exception as e:
        property_list = None
        print('----> Error :', e)
    property_list = TblProperty.objects.all()
    mp_list = TblMasterProperty.objects.all()
    return render(request, 'admin/property_view.html',
                  {'property_list': property_list, 'mp_list': mp_list})


def property_soldout(request, pr_id):
    obj_pr = TblProperty.objects.get(id=pr_id)
    try:
        obj_pr.pr_is_active = False
        obj_pr.save()
    except Exception as e:
        print("Error: ", e)
    return HttpResponseRedirect(reverse(property_listview))
