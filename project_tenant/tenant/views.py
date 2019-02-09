from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from tenant.models import TblAgent
from tenant.decorators import for_admin, for_staff
from tenant.forms import AgentForm, TenantRegistratonForm
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    try:
        agents = TblAgent.objects.filter(
            is_active=False, is_staff=False).order_by('first_name', 'last_name')
        page = request.GET['page',1]
        paginator = Paginator(agents,2)
        agents=paginator.page(page)
    except Exception as e:
        agents = None
    return render(request, 'admin/agent_requests.html', {'agents': agents})


# view all agent requests on admin site
@for_admin
def view_agent_all(request):
    try:
        agents = TblAgent.objects.filter(
            is_staff=True, is_superuser=False).order_by('first_name', 'last_name')
        
        page = request.GET.get('page',1)
        paginator = Paginator(agents,2)
        agents=paginator.page(page)
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
def get_agents(max_results=0, starts_with=''):
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
    if max_results > 0:
        if len(agents) > max_results:
            agents = agents[:max_results]
    return agents


# View the search result from agent requests
@for_admin
def agent_requests_search(request):
    agents = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
        agents = get_agents(4, starts_with)
        print(starts_with)
    return render(request, 'admin/agents.html', {'agents': agents})


#######################################################################################################################
# Agent site views
#######################################################################################################################

# agent index view
@for_staff
def agent_index(request):
    return render(request, 'agent/base.html')
