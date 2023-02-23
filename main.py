import pandas as pd
import numpy as np
from datetime import date
import copy
from gurobipy import GRB
import gurobipy as gp
def opti_riskazaltma(Datas,Result,DatasC,Yatirim):
    
    
   
    NewDatas=fiyatlari_duzenleme(Datas)
    covmat=NewDatas.cov()*len(Datas[0])
    
    m=gp.Model("p1")
    
    Weights=m.addVars(100,name="weights",lb=0,vtype="C")
    
    cons1=m.addConstr(Weights.sum("*")==1)
    m.setObjective(gp.quicksum(Weights[i]*covmat[i][j]*Weights[j] for i in range(100) for j in range(100)),GRB.MINIMIZE)
    m.write("project.lp")
    m.optimize()
    
    weight=[]
    for count, v in enumerate(m.getVars()):
       weight.append(v.X)
     
    expected=expectedV(weight,DatasC)
    Result.append((round(np.sqrt(np.array(weight).T @ covmat @weight)*100,1),expected*Yatirim,expected/np.sqrt(np.array(weight).T @ covmat @weight)))
def opti_ortalama(Datas,Result,DatasC,Yatirim):
    
    weight=[0 for i in range(100)]
   
    
    NewDatas=fiyatlari_duzenleme(Datas)
    
   
    NewDatas=NewDatas.values.tolist()
    m=gp.Model("p2")
    Weights=m.addVars(100,name="weights",lb=0,vtype="C")
    
    cons1=m.addConstr(Weights.sum("*")==1)
    
    m.setObjective(gp.quicksum(NewDatas[i][j]*Weights[j] for i in range(len(Datas[0])) for j in range(100)),GRB.MAXIMIZE)
    m.optimize()
    
    obj = m.getObjective()
    
    obj=obj.getValue()
    return obj
    
def convert_date_to_excel_ordinal(data):
        newdata=[]
        # Specifying offset value i.e.,
        # the date value for the date of 1900-01-00
        for i in data.iloc[:,1]:
            year=int(i[0:4])
            month=int(i[5:7])
            day=int(i[8:10])
            offset = 693594
            current = date(year, month, day)
         
            # Calling the toordinal() function to ge
            # the excel serial date number in the form
            # of date values
            n = current.toordinal()
            newdata.append(n - offset)
        return newdata
def fiyatlari_duzenleme(Datas):
    NewDatas=np.zeros([len(Datas[0]),len(Datas)])
    for i in range(len(Datas[0])):
        for j in range(len(Datas)):
            NewDatas[i][j]=Datas[j][i][3]
    NewDatas=pd.DataFrame(NewDatas)
    return NewDatas
def expectedV(weight,DatasC):
    expected_value=0
    for count, info in  enumerate(DatasC):
        for i in info:
            expected_value+=i[3]*weight[count]
    return expected_value

def convert_date_to_excel_ordinal2(data):
        newdata=[]
        # Specifying offset value i.e.,
        # the date value for the date of 1900-01-00
        for i in data.iloc[:,2]:
            year=int(i[0:4])
            month=int(i[5:7])
            day=int(i[8:10])
            offset = 693594
            current = date(year, month, day)
         
            # Calling the toordinal() function to ge
            # the excel serial date number in the form
            # of date values
            n = current.toordinal()
            newdata.append(n - offset)
        return newdata
def veri_tamamlama(Datas,status=0):
    NewDatas=[]
    for   info in Datas:
         newdatas=[]
         for i in range(len(info)):
             profit=info[i][3]/((info[i][2]-info[i][1])+1)
             for k in range(int((info[i][2]-info[i][1])+1)):
                
                 newdatas.append((info[i][0],info[i][1]+k,info[i][1]+k,profit))
         NewDatas.append(newdatas)
    NewDatas2=[]   
    u=[]
    Days=[]         
    for info in NewDatas:
        newdatas=[]
        day=[]
        total=0
        for i in range(len(info)):
             totalprofit=info[i][3]
             sayac=1
             for j in range(len(info)):
                 if i!=j and info[i][1]==info[j][1]:
                     sayac+=1
                     totalprofit+=info[j][3]
                   
             Info=[info[i][0],info[i][1],info[i][2],totalprofit/sayac]
             if len(day)!=0:
                 if info[i][1] in day:
                    pass
                 else:
            
                     newdatas.append(Info)
                     day.append(info[i][1])
                     total+=totalprofit
             else:
                 newdatas.append(Info)
                 day.append(info[i][1])
                 total+=totalprofit
        NewDatas2.append(newdatas)
        u.append(total/len(newdatas))
        Days.append(day)
        
        
        
        
    Datas=copy.deepcopy(NewDatas2)    
    Days2=[i for i in range(minday,maxday+1)]
    NewDatas4=[]
    
    if status!=2:
        for count,info in enumerate(Datas):
                newdatas=copy.deepcopy(info)  
                for day in Days2:
                    if day in Days[count]:
                        pass
                    else:
                        if status==0:
                            #ortalama ile boş günleri doldurma
                            newdatas.append((info[0][0],day,day,u[count]))
                        elif status==1:
                            #0 ile boş günleri doldurma
                            newdatas.append((info[0][0],day,day,0))
                newdatas=pd.DataFrame(newdatas,columns=["","open","",""])
                newdatas.sort_values(["open"],inplace=True, ascending=True)
                newdatas=newdatas.values.tolist()
                NewDatas4.append(newdatas)
    else:
    #ortak günleri belirleme
        
        NDays=[]
        for count, D in enumerate(Days2):
            status2=1
            for count2, D2 in enumerate(Days):
                
                    if D in D2:
                        status2=1
                    else:
                         status2=0
                         break
            if status2==1:
                NDays.append(D)
        for count,info in enumerate(Datas):
             newdatas=[]
             for day in NDays:
                 for I in info:
                     if day == int( I[1]):
                         newdatas.append(I)
             NewDatas4.append(newdatas)
    return NewDatas4,u

data=pd.read_csv('sampledata.csv')
RobotId=data.drop_duplicates(subset=["roboID"])["roboID"].values
data['dateOpened']=convert_date_to_excel_ordinal(data)
data['dateClosed']=convert_date_to_excel_ordinal2(data)

minday=min(data['dateOpened'].values.tolist())
maxday=max(data['dateClosed'].values.tolist())


Datas=[]
Yatirim=500
#oralama getiri oranı
data["profit"]=data["profit"]/Yatirim

for i in RobotId:
    datas=[]

    for j in range(len(data)):
        if i==data.iloc[j,0]:
            datas.append(data.iloc[j].values.tolist())

    Datas.append(datas)
DatasC=copy.deepcopy(Datas)
Result=[]

Datas,u=veri_tamamlama(Datas=Datas)
#%% optimizasyon risk azaltma

opti_riskazaltma(Datas,Result,DatasC,Yatirim)
#%% getireye göre veri doldurma yok eksik veriler sıfırlar doldurulaacak

Datas=copy.deepcopy(DatasC)
Datas,u=veri_tamamlama(Datas=Datas,status=1)
opti_riskazaltma(Datas=Datas,Result=Result,DatasC=DatasC,Yatirim=Yatirim)
ortalama=opti_ortalama(Datas=Datas,Result=Result,DatasC=DatasC,Yatirim=Yatirim)*Yatirim


#%% sadece ortak günler üzerine optimizasyon yapılacak
Datas=copy.deepcopy(DatasC)
Datas,u=veri_tamamlama(Datas=Datas,status=2)
opti_riskazaltma(Datas=Datas,Result=Result,DatasC=DatasC,Yatirim=Yatirim)

#%%MonteCarloYöntemi
Result2=[]
indexname=['Ortalamaya_göre_Opt','Boşyer_ortalama_risk.Opt','Boşyer_0_risk.Opt','Ortakgün_risk.Opt']
num_iter = 3000
Datas=copy.deepcopy(DatasC)
Datas,u=veri_tamamlama(Datas=Datas,status=2)
for i in range(1,num_iter+1):
    rand_weights = np.random.random(100)
    rand_weights = rand_weights/np.sum(rand_weights)
    expected=expectedV(   rand_weights,DatasC)
    NewDatas=fiyatlari_duzenleme(Datas)
    covmat=NewDatas.cov()*len(Datas[0])
    sharper=expected/np.sqrt(np.array(rand_weights).T @ covmat @rand_weights)
    ad='MC_'+str(i)
    indexname.append(ad)
    Result2.append((round(np.sqrt(np.array(rand_weights).T @ covmat @rand_weights)*100,1),expected*Yatirim,expected/np.sqrt(np.array(rand_weights).T @ covmat @rand_weights)))
Result2=np.array(Result2).reshape(num_iter,3)
#%% sonuçların rapor ve grafik haline getirilmesi

print('ortalama risk: %s ortalama kazanç: %s ortalama sharper oran: %s'%(sum(Result2[:,0])/num_iter,sum(Result2[:,1])/num_iter,sum(Result2[:,2])/num_iter))
Result3=list(Result).copy()
Result3.insert(0,(None,ortalama,None))
Result3=np.array(list(Result3)).reshape(4,3)
Result3=np.append(Result3,Result2,axis=0)

Result3=pd.DataFrame(Result3,columns=['Risk(%)','Getiri($)','Sharper Ratio'],index=indexname)
Result3.plot.scatter(x='Risk(%)', y='Getiri($)',grid=True,marker='o')
Result3.to_excel('Result.xlsx')