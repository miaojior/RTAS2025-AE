# The code in this file utilizes the RD-GEN tool to generate the topology of the task DAG.
# It then employs the method described in the main-text of paper to generate the task parameters.
import random
from subprocess import run

# Data structure of the task DAG
class DAG:
    def __init__(self):
        M = []  # The adjacency matrix of the DAG
        V = []  # Task set of nodes
        cp = [] # Critical path
        ns = 0  # Number of source nodes
        ne = 0  # Number of terminal nodes

# Data structure of the task node
class Task:
    def __init__(self):
        T = 0     #period
        WCET = 0  #worst case execution time
        D = 0     #deadline

# Generate the topology and node parameters of a task graph
# n: total number of nodes, ns: number of source nodes, ne: number of terminal nodes, O_degree/I_degree: maximum in-out degree
def initDAG(n, ns, ne, O_degree, I_degree):
    newDAG = DAG()
    newDAG.M = get_RD_GEN_M(n, ns, ne, O_degree, I_degree)
    newDAG.V = getV(n)
    newDAG.ns = ns
    newDAG.ne = ne
    return newDAG

# Generate the topology of the graph, returned as an adjacency matrix
# n: total number of nodes, ns: number of source nodes, ne: number of terminal nodes, O_degree/I_degree: maximum access degree
def get_RD_GEN_M(n, ns, ne, O_degree, I_degree):
    M = []
    RD_GEN_user(n, ns, ne, O_degree, I_degree)
    M = read_RD_GEN_DAG(n)
    return M


# Generate node parameters for each task, including period, execution time and deadline
# n: total number of tasks
def getV(n):
    V = []
    alpha=1
    for i in range(n):
        task = Task()
        task.T = get_T()
        task.WCET = get_WCET()
        task.D = task.WCET+alpha*(task.T-task.WCET)
        V.append(task)
    return V

# Use the RD_GEN tool to generate the topology file of the graph and store it in dag_0.yaml
# Write the parameters to the configuration file and then start the system instruction to run RD_GEN
def RD_GEN_user(n, ns, ne, O_degree, I_degree):
    seed = str(random.randint(1, 999))
    I_list = []
    for i in range(I_degree):
        I_list.append(i+1)
    I_list = str(I_list)
    O_list = []
    for i in range(O_degree):
        O_list.append(i+1)
    O_list =str(O_list)
    Note=open('./RD-Gen_user/fan_in_fan_out.yaml',mode='w')
    # The following words are the control instructions for the RD-GEN tool
    fan_in_fan_out_setting = 'Seed: '+seed+'\n'+'Number of DAGs: '+'1'+'\n'+'Graph structure:\n'+'  Generation method: "Fan-in/Fan-out"\n'+'  Number of nodes:\n'+'      Fixed: '+str(n)+'\n'+'  In-degree:\n'+'      Random: '+I_list+'\n'+'  Out-degree:\n'+'      Random: '+O_list+'\n'+'  Number of source nodes:\n'+'      Fixed: '+str(ns)+'\n'+'  Number of sink nodes:\n'+'      Fixed: '+str(ne)+'\n'+'  Ensure weakly connected: True\n'+'\n'+'Properties:\n'+'  Execution time:\n'+'      Random: (1, 50, 1)\n'+'\n'+'Output formats:\n'+'  Naming of combination directory: "Abbreviation"\n'+'  DAG:\n'+'      YAML: True\n'+'      JSON: False\n'+'      XML: False\n'+'      DOT: False\n'+'  Figure:\n'+'      Draw legend: False\n'+'      PNG: True\n'+'      SVG: False\n'+'      EPS: False\n'+'      PDF: False\n'
    Note.write(fan_in_fan_out_setting)
    Note.close()
    command = 'python ./RD-Gen_user/run_generator.py -c ./RD-Gen_user/fan_in_fan_out.yaml'
    run(command, shell = True)
    return

# Read the dag_0.yaml file and output the adjacency matrix of the graph
def read_RD_GEN_DAG(n):
    M = []
    for i in range(n):
        m = []
        for j in range(n):
            m.append(0)
        M.append(m)
    with open('./RD-Gen_user/DAGs/DAGs/dag_0.yaml', 'r') as f:
        while True:
            line = f.readline()
            line = line.split()
            if line[0] == 'multigraph:':
                break
            if line[0] == '-':
                pre = int(line[2])
            elif line[0] == 'target:':
                suc = int(line[1])
                M[pre][suc] = 1
    return M


# Generate task period probabilistically
def get_T():
    x = random.randint(1, 60)
    if x <= 10:
        return 10
    elif x <= 20:
        return 20  
    elif x <= 30:
        return 40
    elif x <= 40:
        return 60
    elif x <= 50:
        return 80
    else :
        return 100

# Generate worst-case execution time probabilistically
def get_WCET():
    x = random.randint(1, 30)
    if x <= 10:
        return 1
    elif x <= 20:
        return 2  
    elif x <= 30:
        return 5