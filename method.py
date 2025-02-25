# the experiment of our method
import time as t
import copy

# data structure of the processor
class Core:
    def __init__(self):
        self.t = -1
        self.task = -1
        self.token = Token()

# data structure of message token
class Token:
    def __init__(self):
        self.timestamp_min=1e9
        self.timestamp_max=-1
        self.label=[]
        self.dest=-1
        self.update_flag=-1

# Look up the table to get the current token table
# time : current time, i: sensor number, control: ralated control number of current sensor
# table: token table, node_related_control: control nodes associated with each node , HPs: Supercycles
# Vs: task set of sensor nodes, Ve: task set of control node, WCET: Worst-Case Execution Time, n: number of nodes  
def get_tb(time,i,table,HPs,control,Vs,Ve,n):
    ne=len(Ve)
    x=int((time-Vs[i].WCET)/Vs[i].T)
    j = control-(n-ne)
    p=int(x%(HPs[j]/Vs[i].T))
    tb=[]
    for y in table[i][j][p]:
        tb.append( y+int(x/(HPs[j]/Vs[i].T))*int(HPs[j]/Ve[j].T) )
    return tb

# gengerte message token for sensor
# time : current time, i: sensor number, control: ralated control number of current sensor
# table: token table, node_related_control: control nodes associated with each node , HPs: Supercycles
# Vs: task set of sensor nodes, Ve: task set of control node, WCET: Worst-Case Execution Time, n: number of nodes  
def produce_sensor_token(time,i, control ,table,HPs,Vs,Ve,WCET,n):
    token=Token()
    token.timestamp_min = time-WCET
    token.timestamp_max = time-WCET
    token.dest = control #start from 0
    token.label = get_tb(time,i,table,HPs,control,Vs,Ve,n)
    token.update_flag = time
    return token

# sensor put the token to the succeed waiting queue of successor Node
# time : current time, dag： dag, queue_m: queue of imcoming messages
# node_related_control: control nodes associated with each node ,table: token table, HPs: Supercycles
def sensor_output(time,dag,queue_m,node_related_control,table,HPs):
    n=len(dag.V)
    ns=dag.ns
    ne=dag.ne
    Vs=dag.V[:ns]
    Ve=dag.V[n-ne:n]
    for i in range(ns):
        if (time-Vs[i].WCET)%Vs[i].T == 0 :
            for control in node_related_control[i] :
                token=produce_sensor_token(time,i,control,table,HPs,Vs,Ve,Vs[i].WCET,n)
                if token.label == [] :
                    continue
                SUCC=[]
                for k in range(n):
                    if dag.M[i][k] :
                        SUCC.append(k)
                for j in SUCC:
                    if control in node_related_control[j]:
                        queue_m[j][i].append(copy.deepcopy(token))
    return  queue_m

# inter node put the token to the succeed waiting queue of successor Node after after the cpu task is completed
# time : current time, dag： dag, queue_m: queue of imcoming messages
# node_related_control: control nodes associated with each node ,table: token table, HPs: Supercycles
def inter_output(time, cores,queue_m,dag,node_related_control):
    n=len(dag.V)
    for i in range(len(cores)):
        if cores[i].t==0 :
            token=cores[i].token
            SUCC=[] 
            for k in range(n):
                if dag.M[cores[i].task][k] :
                    SUCC.append(k)
            for j in SUCC:
                if token.dest in node_related_control[j]:
                    token.update_flag=time
                    queue_m[j][cores[i].task].append(copy.deepcopy(token))
            cores[i]=Core()
    return  queue_m

# gettoken of control node
# queue_m: queue of imcoming messages
# k: control node number, z: control task number,PRED: Predecessor Node
def get_token_set(queue_m,k,z,PRED):
    tokenSet=[]
    for i in PRED:
        toDelete=[]
        for j in range(len(queue_m[k][i])):
            token=queue_m[k][i][j]
            if token.dest== k and (z in token.label):
                tokenSet.append(copy.deepcopy(token))
                queue_m[k][i][j].label.remove(z)
                if queue_m[k][i][j].label == [] :
                    toDelete.append(j)
                    break
        while not toDelete == []:
            j= toDelete.pop()
            queue_m[k][i].pop(j)
    return tokenSet ,queue_m

# Control node check whether output is successful
# time : current time, dag： dag, queue_m: queue of imcoming messages
# ee_b: coefficient used to generate end-to-end delay bound, tp_b: coefficient used to generate disparity bound
# succ_num: success control job,total_num: total control job, eebound：cold start time
def control_ouput(time,tp_b,ee_b,dag,queue_m,succ_num,total_num,eebound):
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
            token_set,queue_m=get_token_set(queue_m,k,z,PRED)
            if len(token_set) != len(PRED) :
                continue
            if time>eebound:
                succ_num+=1
    return succ_num,total_num

# inter node could release only if a new message arrive
# time: current time,queue_m: queue of imcoming messages
# k: inter node number, PRED: Predecessor Node
def could_release(time, queue_m, k, PRED):
    for i in PRED:
        for token in queue_m[k][i] :
            if token.update_flag == time :
                return token.dest
    return 0

# collent a set of token from imcoming message
# control: control node,queue_m: queue of imcoming messages
# k: inter node number, PRED: Predecessor Node
def collect_token(control, queue_m, k, PRED): 
    tokenSet= []
    minlabel=0
    for i in PRED :
        for token in queue_m[k][i] :
            if token.dest == control :
                minlabel=max(minlabel,min(token.label))
                break
    for i in PRED :
        flag=0
        for token in queue_m[k][i] :
            if token.dest == control and minlabel in token.label:
                tokenSet.append(copy.deepcopy(token))
                flag =1
                break
        if not flag :
            return []
    return tokenSet

# generate inter node token
# tokenSet: tokenSet 
def generate_token(tokenSet):
    token=Token()
    token.label=tokenSet[0].label
    for tk in tokenSet: 
        token.timestamp_min=min(token.timestamp_min,tk.timestamp_min)
        token.timestamp_max=max(token.timestamp_max,tk.timestamp_max)
        token.label = list(set(token.label).intersection(set(tk.label)))
    token.dest=tokenSet[0].dest
    return token

# delete used token of incoming message in the queue
# queue_m: queue of imcoming messages newToken: inter node token
# k: inter node number, PRED: Predecessor Node
def delete_token(queue_m,newToken,k,PRED):
    for i in PRED :
        toDelete=[]
        for j in range(len(queue_m[k][i])) :
            token = queue_m[k][i][j]
            if token.dest == newToken.dest :
                for p in newToken.label :
                    if p in queue_m[k][i][j].label:
                        queue_m[k][i][j].label.remove(p)
                        if queue_m[k][i][j].label == [] :
                            queue_m[k][i][j].update_flag=-1
                            toDelete.append(j)
                            break
        while not toDelete == []:
            j=toDelete.pop()
            queue_m[k][i].pop(j)
    return queue_m


# inter node collect token from the message wait queue and release job into cpu waiting queue
# time: current time,queue_m: queue of imcoming messages
# wait: cpu job wait queue, PRED: Predecessor Node
def inter_release(time,queue_m,wait,dag):
    n=len(dag.V)
    ns=dag.ns
    ne=dag.ne
    for k in range(ns,n-ne):
        PRED=[]
        for j in range(n):
            if dag.M[j][k] :
                PRED.append(j)
        control = could_release(time,queue_m,k,PRED)
        while control:
            tokenSet=collect_token(control, queue_m, k, PRED)
            if tokenSet==[] :
                break
            newToken=generate_token(tokenSet)
            queue_m=delete_token(queue_m,newToken,k,PRED)
            wait.append([k,newToken])
            control = could_release(time,queue_m,k,PRED)
    return wait

# assign waiting cpu jobs into cpu
# cores: cpu, wait:  job waiting queue, V: task set of sensor nodes
def assign(cores,wait,V):
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
def get_delta_time(time,cores,ns,dag):
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
def to_next_time2(time,cores,dag):
    delta_time,status=get_delta_time(time,cores,dag.ns,dag)
    for i in range(len(cores)):
        if not cores[i].t== -1 :
            cores[i].t -= delta_time
    time = time + delta_time
    return time, cores, status

# Simulate the experimental process by time
# lb ub : lower bound and upper bound of the time,
# ee_b: coefficient used to generate end-to-end delay bound, tp_b: coefficient used to generate disparity bound
# time : current time, dag： dag, queue_m: queue of imcoming messages, cores: cpu cores, wait: asks waiting to be processed
# node_related_control: control nodes associated with each node ,table: token table, HPs: Supercycles
# eebound：cold start time
def simulator(lb,ub,tp_b,ee_b,time,dag,queue_m,node_related_control,table,HPs,cores,wait,eebound):
    succ_num,total_num=0,0
    time =lb
    while time>=lb and time<ub :
        queue_m=sensor_output(time,dag,queue_m,node_related_control,table,HPs)
        queue_m=inter_output(time, cores,queue_m,dag,node_related_control)
        succ_num,total_num=control_ouput(time,tp_b,ee_b,dag,queue_m,succ_num,total_num,eebound)
        wait=inter_release(time,queue_m,wait,dag)
        cores,wait=assign(cores,wait,dag.V)
        time,cores,status=to_next_time2(time,cores,dag)
    return succ_num,total_num

# create cpu by num
# core_num: number of cpus
def create_cpu(core_num):
    cores=[]
    for i in range(core_num):
        c=Core()
        cores.append(c)
    return cores

# create wait queue 
# n: number of nodes
def create_queue_matrix(n):
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append([])
        matrix.append(row)
    return matrix
