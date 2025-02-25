# the experiment of baseline method
from DAG_init import *

# data structure of the processor
class ACore:
    def __init__(self):
        self.t = -1
        self.task = -1
        self.token = AToken()

# data structure of message token
class AToken:
    def __init__(self):
        self.timestamp_min=1e9
        self.timestamp_max=-1
        self.sensor=[]
        self.update_flag=-1

def A_produce_sensor_token(time,i,WCET):
    token=AToken()
    token.timestamp_min = time-WCET
    token.timestamp_max = time-WCET
    token.sensor.append(i)
    token.update_flag = time
    return token

# sensor put the token into succ node wait queue
# time: current time, queue_m: wait queue
def A_sensor_output(time,dag,queue_m):
    n=len(dag.V)
    ns=dag.ns
    Vs=dag.V[:ns]
    for i in range(ns):
        SUCC=[]
        for k in range(n):
            if dag.M[i][k] :
                SUCC.append(k)
        if (time-Vs[i].WCET)%Vs[i].T == 0 :
            for j in SUCC :
                token=A_produce_sensor_token(time,i,Vs[i].WCET)
                queue_m[j][i].append(token)
    return  queue_m

# inter node put the token into succ node wait queue after cpu jub finish
# time: current time, cores: cpu, queue_m: wait queue
def A_inter_output(time, cores,queue_m,dag):
    n= len(dag.V)
    for i in range(len(cores)):
        if cores[i].t==0 :
            token=cores[i].token
            SUCC=[]
            for k in range(n):
                if dag.M[cores[i].task][k] :
                    SUCC.append(k)
            for j in SUCC:
                token.update_flag=time
                queue_m[j][cores[i].task].append(token)
            cores[i]=ACore()
    return  queue_m


# gettoken of control node
# queue_m: wait queue, k: control node number, z: control task number,PRED: Predecessor Node
def A_get_token_set(queue_m,k,z,PRED,V,bound,disparity):
    tokenSet=[]
    deadline=z*V[k].T+V[k].D
    tmax=-1
    tmin=-1e9
    while tmax-tmin > disparity:
        tokenSet=[]
        for i in PRED:
            flag = 0
            for token in queue_m[k][i]:
                if token.timestamp_min >= deadline-bound and token.timestamp_min >= tmax-disparity and token.timestamp_max-token.timestamp_min <= disparity:
                    flag = 1
                    tokenSet.append(token)
                    break
            if flag == 0:
                return [], queue_m
        tmin=1e9
        for token in tokenSet:
            tmax=max(tmax,token.timestamp_max)
            tmin=min(tmin,token.timestamp_min)
    for i in PRED:
        while queue_m[k][i] !=[]:
            if queue_m[k][i][0].timestamp_min <= tmin:
                queue_m[k][i].pop(0)
            else :
                break
    return tokenSet , queue_m

# Control node check whether output is successful
# time : current time, dag： dag, queue_m: queue of imcoming messages
# bounds: end-to-end delay bound, disparitys: time disparity bounds
# succ_num: success control job,total_num: total control job, eebound：cold start time
def A_control_ouput(time,tp_b,ee_b,dag,queue_m,succ_num,total_num,bounds,disparitys,eebound):
    n= len(dag.V)
    ne=dag.ne
    Ve=dag.V[n-ne:n]
    for j in range(len(Ve)):
        k=j+n-ne
        if (time)%Ve[j].T == 0 : #release time 
            if time>eebound:
                total_num+=1
            z=int((time)/Ve[j].T)
            PRED=[]
            for p in range(n):
                if dag.M[p][k] :
                    PRED.append(p)
            token_set,queue_m=A_get_token_set(queue_m,k,z,PRED,dag.V,bounds[j],disparitys[j])
            if len(token_set) != len(PRED) :
                continue
            if time>eebound:
                succ_num+=1
    return succ_num,total_num

def A_could_release(queue_m,k,PRED):
    for i in PRED :
        if queue_m[k][i] == []:
            return 0
    return 1

# get pivot of messages
# queue_m: queue of imcoming messages,k: node number, PRED: Predecessor Node
def get_pivot(queue_m, k, PRED):
    timestamp= -1
    pivot= -1
    for i in PRED :
        if queue_m[k][i][0].timestamp_max > timestamp:
            timestamp= queue_m[k][i][0].timestamp_max
            pivot = i
    return pivot

# collent a set of token from imcoming message
# queue_m: queue of imcoming messages,k: node number, PRED: Predecessor Node
def A_collect_token(queue_m, k, PRED):
    pivot=get_pivot(queue_m,k,PRED)
    tmax=queue_m[k][pivot][0].timestamp_max
    tmin=queue_m[k][pivot][0].timestamp_min
    tokenSet=[]
    for i in PRED:
        trange=1e9
        if i == pivot :
            tokenSet.append(queue_m[k][pivot][0])
            queue_m[k][pivot].pop(0)
            continue
        best_token=0
        for j in range(len(queue_m[k][i])):
            ttmax=max(tmax,queue_m[k][i][j].timestamp_max)
            ttmin=min(tmin,queue_m[k][i][j].timestamp_min)
            if ttmax -ttmin < trange :
                best_token=j
        tokenSet.append(queue_m[k][i][best_token])
        tmax=max(tmax,queue_m[k][i][best_token].timestamp_max)
        tmin=min(tmin,queue_m[k][i][best_token].timestamp_min)
        while best_token+1:
            tmin,queue_m[k][i].pop(0)
            best_token-=1
    return tokenSet, tmax ,tmin

# inter node collect token from the message wait queue and release job into cpu waiting queue
# time: current time,queue_m: queue of imcoming messages
# wait: cpu job wait queue
def A_inter_release(time,queue_m,wait,dag):
    n= len(dag.V)
    ns=dag.ns
    ne=dag.ne
    for k in range(ns,n-ne):
        PRED=[]
        for j in range(n):
            if dag.M[j][k] :
                PRED.append(j)
        while A_could_release(queue_m,k,PRED):
            tokenSet,tmax,tmin=A_collect_token(queue_m, k, PRED)
            newToken=AToken()
            newToken.timestamp_max=tmax
            newToken.timestamp_min=tmin
            wait.append([k,newToken])
    return wait

# assign waiting cpu jobs into cpu
# cores: cpu, wait:  job waiting queue, V: task set of sensor nodes
def A_assign(cores,wait,V):
    for i in range(len(cores)):
        if wait == [] :
            break
        if cores[i].t == -1 :
            TJ=wait.pop(0)
            cores[i].t = V[TJ[0]].WCET
            cores[i].task = TJ[0]
            cores[i].token = TJ[1]
    return cores,wait

# get delta time from current time to next event
# time: current time, cores: cpu,ns: number of sensor node
def A_get_delta_time(time,cores,ns,dag):
    n=len(dag.V)
    ns=dag.ns
    ne=dag.ne
    cpu_t = 1e9
    for core in cores:
        if  core.t != -1 :
            cpu_t=min(cpu_t,core.t)
    
    next_output_time=1e9
    for i in range(ns):
        if time < dag.V[i].WCET :
            output_i= dag.V[i].WCET
        else :    
            output_i=(int((time-dag.V[i].WCET)/dag.V[i].T)+1)*dag.V[i].T+dag.V[i].WCET
        next_output_time=min(next_output_time,output_i)
    for i in range(ne):
        output_i=(int(time/dag.V[i+n-ne].T)+1)*dag.V[i+n-ne].T
        next_output_time=min(next_output_time,output_i)
    delta_time=min(cpu_t,next_output_time-time)
    status= 1 if (delta_time == next_output_time-time) else 0
    return delta_time ,status

# to the next time and do the cpu simulation
# time: current time, cores: cpu
def A_to_next_time2(time,cores,dag):
    delta_time,status=A_get_delta_time(time,cores,dag.ns,dag)
    for i in range(len(cores)):
        if not cores[i].t== -1 :
            cores[i].t -= delta_time
    time = time + delta_time
    return time, cores, status
    
# Simulate the experimental process by time
# lb ub : lower bound and upper bound of the time, 
# ee_b: coefficient used to generate end-to-end delay bound, tp_b: coefficient used to generate disparity bound
# time : current time, dag： dag , queue_m: queue of imcoming messages ,cores: cpu cores ,wait: asks waiting to be processed
# bounds: end to end delay bound of the control, disparitys : time disparity bound of the control
# eebound：cold start time
def A_simulator(lb,ub,tp_b,ee_b,time,dag,queue_m,cores,wait,bounds,disparitys,eebound):
    succ_num,total_num=0,0
    time=0
    while time >=0 and time < ub :
        if time != 0:
            queue_m=A_sensor_output(time,dag,queue_m)
        queue_m=A_inter_output(time, cores,queue_m,dag)
        
        succ_num,total_num=A_control_ouput(time,tp_b,ee_b,dag,queue_m,succ_num,total_num,bounds,disparitys,eebound)
        wait=A_inter_release(time,queue_m,wait,dag)
        cores,wait=A_assign(cores,wait,dag.V)
        time,cores,status=A_to_next_time2(time,cores,dag)
    return succ_num,total_num

# def create_cpu(core_num):
#     cores=[]
#     for i in range(core_num):
#         c=ACore()
#         cores.append(c)
#     return cores

# def create_queue_matrix(n):
#     matrix = []
#     for i in range(n):
#         row = []
#         for j in range(n):
#             row.append([])
#         matrix.append(row)
#     return matrix