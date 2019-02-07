from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from tenant.models import TblAgent
# Create your views here.

#index view

def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            print('\n\nlogout\n\n')
            logout(request)
    return render(request,'base.html')

#custom login for admin/agent
def do_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user and user.is_staff or user.is_superuser:
        if  user.is_superuser :
            print("\n\n\n\n Admin \n",user,"\n\n\n")
            login(request, user)
            return render(request,'admin_site/base.html')
        elif user.is_staff :
            print("\n\n\n\n Agent \n",user,"\n\n\n")
            login(request, user)
            return render(request,'agent/base.html')
    else:
        print("\n\n\n\nInavlid user\n\n\n\n")
        return render(request,'base.html')

    
#view all agent requests on admin site
def view_agent_request(request):
    try:
        agents = TblAgent.objects.filter(is_active=False, is_staff=False)
    except Exception as e:
        agents=None
        print('error aayi bhai', e)

    if agents :
        for agent in agents:
            print(agent)
    return render(request,'admin_site/agent_requests.html',{'agents':agents})


#accepting the agent request
def agent_request_accept(request):
    id = request.POST['id']
    agent = TblAgent.objects.get(id=id)
    agent.verified_save()
    print("\n\n\n\n\n",agent)
    return view_agent_request(request)

#deleting the agent request
def agent_request_reject(request):
    id = request.POST['id']
    agent = TblAgent.objects.filter(id=id).delete()
    # agent.verified_save()
    print("\n\n\n\n\n",agent)
    return view_agent_request(request)


#Viewing the agent request in more detailed View
def agent_profile(request):
    id = request.POST['id']
    agent = TblAgent.objects.get(id=id)
    # agent.verified_save()
    print("\n\n\n\n\n",agent)
    return render(request,'admin_site/agent_profile.html',{'agent':agent})
