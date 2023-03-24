from django.contrib import messages
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from simple.forms import dailystatusform
from simple.models import userregistrationmodel, excercisesdata, dailystatus
from datetime import date
from .algorithms.anntest import NeuralNetwork
import numpy as np
import random
from .algorithms.LogisticRegressionTest import runLogisticAlgo


def userlogincheck(request):
	if request.method == "POST":
		usid = request.POST.get('loginid')
		pswd = request.POST.get('password')
		try:
			check = userregistrationmodel.objects.get(loginid=usid, password=pswd)
			request.session['stuid'] = check.loginid
			request.session['loggedstu'] = check.name
			request.session['age'] = check.age
			print(check.age)
			request.session['weight'] = check.weight

			status = check.status
			print("stu	id ",check.loginid)
			if status == "activated":
			   #request.session['stuid'] = check.loginid
			   request.session['email'] = check.email
			   return render(request,'user/userhome.html')
			else:
				messages.success(request, 'Your Account Not at activated')
				return render(request,'user/user.html')

			return render(request,'user/userhome.html')
		except Exception as e:
			print('Exception is ',str(e))
	messages.success(request, 'Invalid Login Details')
	return render(request,'user/user.html')
def userfitness(request):
        #ag=request.session['age']
        #wt=request.session['weight']
        ag=request.session['age']
        wt=request.session['weight']
        print('age = ',ag ,' weight = ',wt)
        #qs=excercisesdata.objects.get(age=ag,weight=wt)
        qs=excercisesdata.objects.filter(age=ag,weight=wt)
        
        print(qs)
        for x in qs:
            print(x.diet)
        return render(request,"user/userfitness.html",{"message":qs})



def userhome(request):

	return render(request, 'user/userhome.html')

def userbase(request):
	return render(request,"userbase.html")





def status(request):
	if request.method == 'POST':
		form = dailystatusform(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'you are successfully status updated')
			return HttpResponseRedirect('user')
		else:
			print('Invalid')

	else:
		id = request.GET.get('id')
		name=request.session['loggedstu']
		today = date.today()
		data ={'name':name,'date':today}
		form = dailystatusform(data)
		#form = dailystatusform()
	return render(request,"user/status.html",{'form':form})



def viewuserdailystatus(request):
	dict = dailystatus.objects.all()
	return render(request,'admin/viewuserdailystatus.html',{'object':dict})

def UserPredections(request):
	dict = {}
	listUsers = userregistrationmodel.objects.all()
	dataLlist = []
	idlist = []
	for users in listUsers:
		list = []
		userid = users.loginid
		v0 = int(users.id%2)
		if v0 == 0:
			idlist.append(0)
		else:
			idlist.append(1)
		#idlist.append(users.id)
		#print('Registerd users = ',userid)
		heightandweight = userregistrationmodel.objects.get(loginid=userid)
		#print(heightandweight.age)
		age = heightandweight.age
		height = heightandweight.height
		weight = heightandweight.weight
		v1 = int(int(age)%2)
		print("V1 == ",v1)
		if v1 == 0:
			list.append(0)
		else:
			list.append(1)
		#list.append(age)
		v2= int(int(height)%2)
		if v2==0:
			list.append(0)
		else:
			list.append(1)
		#list.append(height)
		v3 = int(int(weight)%2)
		if v3==0:
			list.append(0)
		else:
			list.append(1)
		#list.append(weight)
		dataLlist.append(list)
	neural_network = NeuralNetwork()
	print("Beginning Randomly Generated Weights: ")
	dict.update({"genweight":neural_network.synaptic_weights})
	list = [[0, 0, 1], [1, 1, 1], [1, 0, 1], [0, 1, 1]]
	# training data consisting of 4 examples--3 input values and 1 output
	print("Trainfin Dataset ",dataLlist)
	print("Test Dataset ",idlist)
	training_inputs = np.array(dataLlist)
	#training_outputs = np.array([[0, 1, 1, 0]]).T
	training_outputs = np.array([idlist]).T
	# training taking plac
	neural_network.train(training_inputs, training_outputs, 15000)
	print("Ending Weights After Training: ")
	dict.update({"aftrtraining":neural_network.synaptic_weights})
	pathList = [0,1]
	user_input_one = random.choice(pathList) #str(input("User Input One: "))
	user_input_two = random.choice(pathList) #str(input("User Input Two: "))
	user_input_three = random.choice(pathList) #str(input("User Input Three: "))

	dict.update({"newsiut": [user_input_one, user_input_two, user_input_three]})
	print("New Output data: ")
	dict.update({'result':neural_network.think(np.array([user_input_one, user_input_two, user_input_three]))})
	print("Its Done ")
	lgdict = runLogisticAlgo()
	return render(request,'user/userpredections.html',{'dict':dict,'lgdict':lgdict})
