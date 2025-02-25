# Calculate the sensor nodes and control nodes associated with each node
def create_dag_relations(dag):
    n=len(dag.V)
    ns=dag.ns
    ne=dag.ne
    node_related_control = []
    for node in range(n):
        node_related_control.append([])
    for i in range(ne) :
        control = i + n -  ne
        queue=[]
        visited=[]
        for j in range(n): 
            visited.append(0)
        visited[control]=1
        queue.append(control)
        while len(queue) :
            N = queue.pop(0)
            node_related_control[N].append(control)
            for j in range (n) :
                if dag.M[j][N]==1 and visited[j]==0:
                    visited[j]=1
                    queue.append(j)

    node_related_sensor = []
    for i in range(n):
        node_related_sensor.append([])
    for sensor in range(ns) :
        queue=[]
        visited=[]
        for j in range(n): 
            visited.append(0)
        visited[sensor]=1
        queue.append(sensor)
        while len(queue) :
            N = queue.pop(0)
            node_related_sensor[N].append(sensor)
            for j in range (n) :
                if dag.M[N][j]==1 and visited[j]==0:
                    visited[j]=1
                    queue.append(j)
    return node_related_control, node_related_sensor



def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return abs(a * b) // gcd(a, b)

# Use Algorithm 2 to construct select token for each control job
# control: the number of control node, y: the number of the job
# n: total number of nodes, ns: number of source nodes, ne: number of terminal nodes
# V: task set of nodes, node_related_sensor : sensor nodes associated with each node
# bound: end to end delay bound of the control, disparity : time disparity bound of the control
def selectToken(control,y,V,n,ns,ne,node_related_sensor,bound,disparity) :
    IS=[]
    for i in range (0,ns):
        IS.append(-1)
    for sensor in node_related_sensor[control] :
        z=0
        while z*V[sensor].T < y*V[control].T-bound+V[control].D:
            z=z+1
        if z*V[sensor].T <= y*V[control].T :
            IS[sensor]=z
        else :
            return []
    tmax = 0
    tmin = 100000000000000000000
    for sensor in node_related_sensor[control]:
        if IS[sensor]*V[sensor].T > tmax:
            tmax=IS[sensor]*V[sensor].T
        if IS[sensor]*V[sensor].T < tmin:
            tmin=IS[sensor]*V[sensor].T
    if tmax > y*V[control].T :
        return []
    for sensor in node_related_sensor[control] :
        if tmax - IS[sensor]*V[sensor].T > disparity:
            z=IS[sensor]
            while tmax - z*V[sensor].T > disparity :
                z=z+1
            IS[sensor]=z
    while tmax - tmin > disparity :
        tmax = 0
        tmin = 100000000000000000000
        for sensor in node_related_sensor[control]:
            if IS[sensor]*V[sensor].T > tmax:
                tmax=IS[sensor]*V[sensor].T
            if IS[sensor]*V[sensor].T < tmin:
                tmin=IS[sensor]*V[sensor].T
        if tmax > y*V[control].T :
            return []
        for sensor in node_related_sensor[control] :
            if tmax - IS[sensor]*V[sensor].T > disparity:
                z=IS[sensor]
                while tmax - z*V[sensor].T > disparity :
                    z=z+1
                IS[sensor]=z
    return IS

# Use Algorithm 1 to construct a token table
# n: total number of nodes, ns: number of source nodes, ne: number of terminal nodes
# V: task set of nodes , node_related_sensor : sensor nodes associated with each node
# ee_b: coefficient used to generate end-to-end delay bound, tp_b: coefficient used to generate disparity bound
def generate_token_selection_table(n,ns,ne,V,node_related_sensor,ee_b,tp_b):
    HPs = []
    table = []
    for i in range (ns):
        table.append([])
        for j in range (ne):
            control=j+n-ne
            table[i].append([])
            task = V[control]
            HP=task.T
            relation=node_related_sensor[control]
            for k in relation :
                HP=lcm(HP,V[k].T) 
            HPs.append(HP)
            for x in range(int((HP+1)/V[i].T)):
                table[i][j].append([])
    bounds=[]
    disparitys=[]
    for j in range (ne):
        control=j+n-ne
        task = V[control]
        HP=HPs[j]
        bound=ee_b*HPs[j]
        bounds.append(bound)
        maxd=V[control].T
        for p in node_related_sensor[control]:
            maxd=max(maxd,V[p].T)
        disparity=tp_b*maxd
        disparitys.append(disparity)
        for y in range (int(HP/task.T*100),int(HP/task.T*101)):
            IS=selectToken(control,y,V,n,ns,ne,node_related_sensor,bound,disparity)
            if IS != [] :
                for i in node_related_sensor[control]:
                    x=IS[i]
                    yy = y
                    while x >= (HP/V[i].T):
                        x=int(x-(HP/V[i].T))
                        yy=int(yy-(HP/task.T))
                    table[i][j][x].append(yy)
                    table[i][j][x].sort()
            # else :
                # print("select error",j,y)
    return HPs,table,bounds,disparitys
