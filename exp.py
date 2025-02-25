from DAG_init import *
from selection_table import *
from method import *
from approximate import *

parameters1 = [
    [5,10,15,20,25,30,35,40,45,50],
    [2,4,6,8,10,12,14,16,18,20],
    [2,4,6,8,10,12,14,16,18,20],
    [2,4,6,8,10,12,14,16,18,20],
    [0.2,0.4,0.6,0.8,1.0,1.2,1.4,1.6,1.8,2.0],
    [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.3,0.45,0.5],
]

parameters2 =["n","ns","ne","D","ee_b","tp_b"]

def getPre(i, j):
    PRE = [parameters1[0][7],parameters1[1][3],parameters1[2][3],parameters1[3][4], parameters1[4][4],parameters1[5][0]]
    PRE[i]=parameters1[i][j]
    n = PRE[0]
    ns = PRE[1]
    ne = PRE[2]
    if i==0:
        ns=int(n*0.2)
        ne=int(n*0.2)
    O_degree = PRE[3]
    I_degree = PRE[3]
    ee_b=PRE[4]
    tp_b=PRE[5]
    return n, ns, ne, O_degree, I_degree, ee_b, tp_b

#  Calculates the success rate data of Figures 6 to 11 by simulating
def exp(batchsize):
    with open("./output.txt", "w") as out_file:
        for i in range(len(parameters1)):
            for j in range (len(parameters1[i])):
                results_1 = []
                results_2 = []
                for t in range (batchsize):
                    n, ns, ne, O_degree, I_degree, ee_b, tp_b= getPre(i,j)
                    core_num=1000
                    dag = initDAG(n, ns, ne, O_degree, I_degree)
                    node_related_control, node_related_sensor = create_dag_relations(dag)
                    HPs,table,bounds,disparitys=generate_token_selection_table(n,ns,ne,dag.V,node_related_sensor,ee_b,tp_b)
                    HHP = calculate_HHP(HPs)
                    lb=0
                    ub=int(HHP*10+HHP*ee_b+1)
                    wait = []
                    cores = create_cpu(core_num)
                    queue_m= create_queue_matrix(n)
                    time=0
                    succ_num,total_num=simulator(lb,ub,tp_b,ee_b,time,dag,queue_m,node_related_control,table,HPs,cores,wait,int(HHP*ee_b+1))
                    wait = []
                    cores = create_cpu(core_num)
                    queue_m= create_queue_matrix(n)
                    time=0
                    A_succ_num,A_total_num=A_simulator(lb,ub,tp_b,ee_b,time,dag,queue_m,cores,wait,bounds,disparitys,int(HHP*ee_b+1))
                    results_1.append(round(succ_num/total_num, 4))
                    results_2.append(round(A_succ_num/A_total_num, 4))
                out_file.write(f"{round(sum(results_1) / len(results_1), 4)} {round(sum(results_2) / len(results_2), 4)}\n")

def calculate_HHP(HPs):
    HHP = HPs[0]
    for h in range(1, len(HPs)):
        HHP = lcm(HHP, HPs[h])
    return HHP