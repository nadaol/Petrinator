"""
Determinacion automática del control de una red de Petri 
\n
Analiza las RdP y determina los supervisores para el control de los deadlock presentes en dicha red.
\n
Autores: \n
- Izquierdo, Agustina Nahir \n
- Navarro, Matias Alejandro \n
- Salvatierra, Andres \n
"""
try:
    import os
    import sys
    #file_dir = os.path.dirname(__file__)
    """ sys.path is a built-in variable within the sys module. It contains a list of directories that the interpreter will search in for the required module. 
    When a module(a module is a python file) is imported within a Python file, the interpreter first searches for the specified module among its built-in modules. 
    If not found it looks through the list of directories(a directory is a folder that contains related modules) defined by sys.path. """
    #sys.path.append(file_dir)
    #print(sys.path)
    #exit(0)
    import numpy as np
    import re
    import html_txt_all as hta
    import filter_data as filterdata
    import new_red
    import arcs as arcosrdp 
    import shutil
    import socket as sk
except ImportError as ie:
    error = "Error : " + str(ie)
    print(error,flush=True)
    exit(1)




def siphones_traps(cantidad_plazas):
    """ 
    Devuelve una matriz de [sifones x plazas] y otra de [trampas x plazas]. Tambien devuelve cantidad de sifones y de trampas. \n
    
    Parameters \n
    ----------
        cantidad_plazas     -- Cantidad de plazas de la RdP

    Returns \n
    -------
        matriz_sifones      -- Matriz de sifones
        matriz_traps        -- Matriz de trampas
        cantidad_sifones    -- Cantidad de sifones
        cantidad_traps      -- Cantidad de trampas
    """
    #Apertura de archivos resultantes de la conversion de archivos .html to .txt 
    # obtenidos del SW Petrinator, para su siguiente manipulacion y filtrado.
    pasi = open("./siphons_traps.txt","r")
    i = 0 
    aux_s = 0
    aux_t = 0

    for line in pasi: #Obtiene la cantidad de trampa y sifones que contiene la RdP 
        i=i+1
        if(i>1):
            aux_s = aux_s + 1
            aux_t = aux_t + 1 
            if(line.find("Minimal traps")==1):
                cantidad_sifones = aux_s - 1
                aux_t = 0
            if(line.find("Analysis")==1):
                cantidad_traps = aux_t -1

    pasi.seek(0) #Vuelve el cabezal al principio del archivo 
    aux_s = cantidad_sifones
    aux_t = cantidad_traps

    s_flag = 0
    t_flag = 0

    siphons_aux = []
    traps_aux = []

    for line in pasi:
        if(s_flag == 1 and aux_s != 0): #Obtiene los sifones de la RdP
            siphons_aux.append(line)
            aux_s = aux_s - 1 
        
        if(t_flag == 1 and aux_t != 0): #Obtiene las trampas de la RdP
            traps_aux.append(line)
            aux_t = aux_t -1 
        
        if(line.find("Minimal siphons")==1):
            s_flag = 1 
            #print("Sifones")
        
        if(line.find("Minimal traps")==1):
            t_flag = 1 
            #print("Trampas")

    siphons = []
    traps = [] 
    for i in range (len(siphons_aux)): #Elimina los espacios del string y agrega cada sifon
        siphons.append(str(siphons_aux[i]).split())

    for i in range (len(traps_aux)): #Elimina los espacios del string y agrega cada trampa
        traps.append(str(traps_aux[i]).split())

    #Creamos la matriz que representa por fila la cantidad de sifones o traps y por columna plazas
    #hay un 1 en las plazas que conforman esos sifones o traps
    matriz_sifones =np.zeros((cantidad_sifones,cantidad_plazas))
    matriz_traps =np.zeros((cantidad_traps,cantidad_plazas))

    for i in range(0,len(siphons)):
        for j in range(0,len(siphons[i])):
            matriz_sifones[i][int(siphons[i][j])-1]=1

    for i in range(0,len(traps)):
        for j in range(0,len(traps[i])):
            matriz_traps[i][int(traps[i][j])-1]=1

    pasi.close()
    return matriz_sifones,matriz_traps,cantidad_sifones,cantidad_traps



def invariantes(cantidad_transiciones):
    """ 
    Devuelve la matriz de invariantes de transicion, mediante la apertura de un archivo txt previamente convertido. \n
    
    Parameters \n
    ----------
        cantidad_transiciones   -- Cantidad de transiciones de la RdP

    Returns \n
    -------
        M_TI                    -- Matriz de T-invariante
    """
    file = open('invariante.txt', 'r')
    cont = 0
    TInvariantes = []
    PInvariantes = []
    for line in file:
        if(cont==0):
            TInvariantes = line
            cont = cont + 1
        elif(cont==1):
            PInvariantes = line
            cont = cont + 1

    aux_I = TInvariantes.split(' ')
    TInvariantes = []
    for i in range (cantidad_transiciones, len(aux_I)-2):
        TInvariantes.append(aux_I[i])

    M_TI = np.zeros((int(len(TInvariantes)/cantidad_transiciones), cantidad_transiciones))
    m = 0
    for i in range ((int(len(TInvariantes)/cantidad_transiciones))):
        for j in range (cantidad_transiciones):
            M_TI[i][j] = TInvariantes[m]
            m = m + 1

    file.close()
    return M_TI.astype(int)



def matriz_pre_pos(cantidad_plazas,cantidad_transiciones):
    """ 
    Devuelve la matriz pre y post a partir de un archivo txt previamente convertido. \n
    
    Parameters \n
    ----------
        cantidad_plazas         -- Cantidad de plazas de la RdP
        cantidad_transiciones   -- Cantidad de transiciones de la RdP
    
    Returns \n
    ------- 
        matriz_I_pos            -- Matriz Post (I+)
        matriz_I_neg            -- Matriz Pre  (I-)
    """
    #Apertura de archivos resultantes de la conversion de archivos .html to .txt
    # obtenidos del SW Petrinator, para su siguiente manipulacion y filtrado.
    matriz_I = open("./matricesI.txt","r")
    matriz_I_pos = np.loadtxt(matriz_I,delimiter=' '' ',skiprows=3,max_rows=cantidad_plazas, dtype=bytes).astype(str)
    matriz_I_neg = np.loadtxt(matriz_I,delimiter=' '' ',skiprows=2,max_rows=cantidad_plazas+1, dtype=bytes).astype(str)

    aux_pos = []
    aux_neg = []
    for i in range(cantidad_plazas):
        aux_pos.append(matriz_I_pos[i].split(" "))

    for i in range(cantidad_plazas):
        aux_neg.append(matriz_I_neg[i].split(" "))

    aux_pos = np.delete(aux_pos,0,1)
    aux_neg = np.delete(aux_neg,0,1)
    aux_pos = np.delete(aux_pos,cantidad_transiciones,1)
    aux_neg = np.delete(aux_neg,cantidad_transiciones,1)

    matriz_I_pos = aux_pos.astype(int)
    matriz_I_neg = aux_neg.astype(int)

    matriz_I.close()

    return matriz_I_pos,matriz_I_neg



def conflict_t_invariante(t_conflict,t_invariant,matriz_pos,plazas_sifon_complemento,t_in):
    """ 
    Obtiene las transiciones en conflicto que le tienen que devolver algun token al supervisor. \n
    
    Parameters \n
    ----------
        t_conflict                  -- Transiciones en conflicto
        t_invariant                 -- T-Invariante
        matriz_pos                  -- Matriz Post (I+)
        plazas_sifon_complemento    -- Plazas complemento del sifon a controlar
        t_in                        -- Transiciones de entrada al supervisor
    """
    respuestaTI=""
    for ii in range(0,len(t_conflict)):
        flag_sifon=0
        for jj in range(0,len(t_invariant)):
            if(int(t_invariant[jj][t_conflict[ii]])==1): #La T en conflicto forma parte del T invariante?
                aux_t=np.copy(t_invariant[jj])  #Guardamos el T invariante
                for aa in range(0,len(aux_t)):
                    if(int(aux_t[aa])==1): #Buscamos la T que forma parte del T-invariante
                        for bb in range(0,len(matriz_pos)):
                            if(int(matriz_pos[bb][aa])==1):
                                if(int(plazas_sifon_complemento[bb])==1): #La T alimenta a alguna plaza del sifon'
                                    flag_sifon=1

        if(flag_sifon==0):
            #print("Transicion input:",int(t_conflict[ii])+1)
            respuestaTI= "<br>Transicion input: " + str(int(t_conflict[ii])+1)
            t_in.append("T"+str(int(t_conflict[ii])+1))
    
    return str(respuestaTI)



def path_conflict(t_idle,t_analizar,flag_idle,plazas_sifon_complemento,matriz_pre,matriz_pos,cantidad_plazas,cantidad_transiciones,t_invariant,t_in):
    """ 
    Se obtienen las transiciones que forman parte del conflicto. \n
    
    Parameters \n
    ----------
        t_idle                      -- Transiciones idle
        t_analizar                  -- Transicion a analizar 
        flag_idle                   -- Indica que es una t-idle
        plazas_sifon_complemento    -- Plazas complementos del sifon a controlar
        matriz_pre                  -- Matriz Post (I+)
        matriz_pos                  -- Matriz Pre  (I-)
        cantidad_plazas             -- Cantidad de plazas de la RdP
        cantidad_transiciones       -- Cantidad de tranciones de la RdP 
        t_invariant                 -- T-Invariante
        t_in                        -- Transiciones input al supervisor
    """
    respuestaPC=""
    if(t_idle!=t_analizar or flag_idle==1):
        flag_idle=0
        p_idle=[] #Plaza a las que le pone tokens la transicion
        for jj in range (0,cantidad_plazas):
            if(int(matriz_pos[jj][t_analizar])!=0): #A que plazas esta alimentando esa transicion(t_analizar)
                p_idle.append(int(jj))
        #print(p_idle)
        for ii in range (0,len(p_idle)):
            t_conflict=[] #Plaza que alimenta a las transiciones en conflicto
            for mm in range (0,cantidad_transiciones):
                if(matriz_pre[p_idle[ii]][mm]==1):
                    t_conflict.append(mm)             #Transiciones en conflicto sensibilizadas por esa plaza
            if(len(t_conflict)>1): #La plaza sensibiliza a mas de una transicion? Hay conflicto
                file_t_conflict_orig = open(Jar_path +  '/tmp/t_conflict_red_original.txt', 'w+')
                for ij in range (0, len(t_conflict)):
                    file_t_conflict_orig.write(str(t_conflict[ij]) + ' ')
                file_t_conflict_orig.close()

                respuestaPC=conflict_t_invariante(t_conflict,t_invariant,matriz_pos,plazas_sifon_complemento,t_in)

            else: #no hay conflicto
                respuestaPC=path_conflict(t_idle,t_conflict[0],flag_idle,plazas_sifon_complemento,matriz_pre,matriz_pos,cantidad_plazas,cantidad_transiciones,t_invariant,t_in)

    return respuestaPC


def supervisor(cantidad_transiciones,cantidad_plazas,sifon,matriz_es_tr,matriz_pos,matriz_pre,matriz_sifones,t_invariant,lista_supervisores):
    """ 
    Define el supervisor que va a controlar el bad-siphon. Esta funcion define el marcado de la plaza supervisor y las transiciones de entrada y salida del mismo. \n
    
    Parameters \n
    ----------
        cantidad_transiciones   -- Cantidad de transiciones de la RdP
        cantidad_plazas         -- Cantidad de plazas de la RdP
        sifon                   -- bad siphon a controlar. Compuesto por 3 elementos: estado deadlock[0], numero sifon[1], marcado sifon[2]
        matriz_es_tr            -- Matriz [estado x transiciones]
        matriz_pos              -- Matriz Pos (I+)
        matriz_pre              -- Matriz Pre (I-)
        matriz_sifones          -- Matriz de sifones 
        t_invariant             -- T-invariantes
    """
    global id
    #print("\nid=", id)
    respuestaSup= "<br><br>id="+ str(id)
    id=id+1
    trans_idle=[] #Transiciones habilitadas en el marcado inicial
    marcado_supervisor=sifon[2]-1 #Es la posicion 2 debido que el sifon esta declarado estado deadlock[0], numero sifon[1], marcado sifon[2]
    #Marcado del supervisor
    #nuevo
    respuestaSup+= "<br>Supervisor_mark:"+ str(marcado_supervisor)
    #end nuevo
    #("Sifon a controlar: ",sifon[1]+1)
    respuestaSup+= "<br>Siphon to supervise: "+ str(sifon[1]+1)
    plazas_sifon_aux=np.copy(matriz_sifones[sifon[1]])
    sif_aux = []
    for i in range (len(plazas_sifon_aux)): 
        if(plazas_sifon_aux[i] != 0):
            sif_aux.append(f"P{i+1}")
    #print("Plazas del Sifon: ",sif_aux)
    respuestaSup+= "<br>Siphon places: "+ str(sif_aux)
    #print("Marcado del supervisor",marcado_supervisor) 
    #respuestaSup+= "<br>Marcado del supervisor: "+ str(marcado_supervisor)

    #Transiciones que salen del estado idle, le quitan tokens a los supervisores
    #estas se encuentran sensibilizadas en el estado inicial (0) y son las transiciones
    #que son distintan de -1 en la matriz matriz_es_tr (estado-transicion) --> Transiciones 1 de Ezpeleta
    t_out=[]
    for ii in range(cantidad_transiciones):
        if(matriz_es_tr[0][ii]!=-1):
            trans_idle.append(ii)
            t_out.append("T"+str(ii+1))
            #print("Transicion output: ",ii+1) #+1 Por problemas de indice en petrinator empieza en 1
            respuestaSup+= "<br>Transicion output: "+ str(ii+1)

    tran_sifon=np.zeros(cantidad_transiciones) #Vector que indica que transiciones sacan/ponen tokens en el sifon

    plazas_sifon=np.copy(matriz_sifones[sifon[1]]) #Vectors de todas las plazas del sistema, en 1 se encuentran las plazas que componen nuestro sifon
    #print(plazas_sifon)
    #Localizamos transiciones que colocan tokens al supervisor-->Transiciones 2 de Ezpeleta
    for i in range(0,cantidad_plazas):
        if(plazas_sifon[i]==1): #Es una plaza del sifon
            for j in range(0,cantidad_transiciones):
                if(int(matriz_pre[i][j])==1):
                    tran_sifon[j]=tran_sifon[j]-1 #Le quita tokens al sifon
                if(int(matriz_pos[i][j])==1):
                    tran_sifon[j]=tran_sifon[j]+1 #Le agrega tokens al sifon
    t_in=[]
    for i in range(0,cantidad_transiciones):
        if(tran_sifon[i]>0): #Si es mayor a 0 significa que esta transicion coloca mas tokens a los sifones de los que le quitan
            #("Transicion input:", i+1) #Petrinator empieza en 1 y no en cero por eso el +1
            respuestaSup+= "<br>Transicion input: " + str(i+1)
            t_in.append("T"+str(i+1))
    plazas_sifon_complemento=np.copy(plazas_sifon) #Usado para calcular la 3er transicion de Ezpeleta

    #Obtenemos los complementos
    for i in range(0,len(tran_sifon)):
        if(tran_sifon[i]>0):
            for j in range(0,cantidad_plazas):
                if(int(matriz_pre[j][i])==1):#son las plazas que habilitan transiciones que agregan mas
                                             #tokens de los que sacan del sifon.
                    plazas_sifon_complemento[j]=1

    for tt in range (0,len(trans_idle)):
        cont_t_invariante=0 #indica en cuantos T-invariantes aparece la Transiciones habilitadas en estado idle
                        #de ser =>2 implica que esta en conflicto
        for yy in range (0,len(t_invariant)):
            if(t_invariant[yy][trans_idle[tt]]==1):
                cont_t_invariante=cont_t_invariante+1
        if(cont_t_invariante>=2):
            respuestaSup+=path_conflict(trans_idle[tt],trans_idle[tt],1,plazas_sifon_complemento,matriz_pre,matriz_pos,cantidad_plazas,cantidad_transiciones,t_invariant,t_in) #El 1 indica que es flag_idle

    lista_supervisores.append(["P"+str(cantidad_plazas+1),str(marcado_supervisor),t_in,t_out])
    return respuestaSup


def fun_sifones_deadlock(estado,matriz_sifones,matriz_es_pl,idle,cantidad_plazas,cantidad_sifones,sifon_idle,sifon_deadlock):
    """ 
    Devuelve los sifones que se vacian en ese estado de deadlock. \n
    Apartir de matriz de Estados x Plazas = [Marcado] se recorre la fila de la matriz donde se encuentra el estado deadlock,
    colocando un "1" en aquellas plazas donde el marcado sea >=1. \n
    Se realiza un and entre esa fila de la matriz y el sifon, si la and = 0 implica que ese sifon se encuentra vacio para ese estado de deadlock. 
    
    Parameters \n
    ----------
        estado          -- Estado que posee Deadlock.
        matriz_sifones  -- [Marcado de plazas que componen el sifon]
        matriz_es_pl    -- EstadosxPlazas = [Marcado para ese estado].
        idle            -- Indica si se agrega a la lista de sifon_idle o sifon_deadlock
    """

    aux=np.zeros(cantidad_plazas)
    flag_sifon_idle=0
    for j in range(0,cantidad_plazas):
        if(matriz_es_pl[estado][j]>=1): #Obtenemos las plazas(marcadas) del estado deadlock
            aux[j]=1

    for i in range(0,cantidad_sifones):
        cont=0
        for j in range(0,cantidad_plazas):
            if(int(matriz_sifones[i][j] and aux[j])==1):
                cont=cont+1             #Si el contador es distinto de cero, el sifon no esta vacio
        if(cont==0):
            marcado=0
            for j in range(0,cantidad_plazas):
                if(matriz_sifones[i][j]==1):
                    marcado=marcado+matriz_es_pl[0][j] #Es 0 en fila, porque es el estado inicial en el que se encontraban las plazas de los sifones
            if(idle==0):
                for jj in range(0,len(sifon_idle)):
                    if(sifon_idle[jj]==i): #El sifon vacio en deadlock esta vacio en idle?
                        flag_sifon_idle=1
                if(flag_sifon_idle==0): #El sifon no estaba vacio en idle
                    sifon_agregado = 1 
                    for index in range(0, len(sifon_deadlock)): #Verifica si el sifon ya se incluyó en la lista, de no ser así lo agrega
                        if(sifon_deadlock[index][1]==i):
                            sifon_agregado = 0
                    if(sifon_agregado):
                        sifon_deadlock.append([estado,i,marcado]) #Devuelve el sifon y su marcado inicial, para ese estado deadlock
            else:
                sifon_idle.append(i)#sifon_idle.append[i]

def cleanTXTS():
    
    pathActual = os.path.dirname(os.path.realpath(__file__))
    files = os.listdir()
    for name in files:
        if name.endswith(".txt") and not(name.endswith("original.txt")) :
            os.remove(name)
    shutil.rmtree(pathActual+"/__pycache__")

def createString(len):
    i=0
    arr = ""
    for i in range(len):
        arr+= str(i) + " "
    return arr   

def finalizeCom():
    respuesta = "Analysis executed, python process is exiting"
    #respuesta = respuesta.encode("UTF-8")
    #sCliente.send(len(respuesta).to_bytes(2, byteorder='big'))
    #sCliente.send(respuesta)
    #print(len(respuesta))
    print(respuesta,flush=True)
    cleanTXTS()
    #sCliente.close()
    exit(0)

def main():

    
    #print("--------------------------------------------------------------------------")
    #print("Algoritmo para la solucion de deadlock para redes de petri tipo S3PR")
    #print("--------------------------------------------------------------------------")

    analisis = sys.stdin.readline().replace("\n","")
    #Conversion de archivos html a txt

    hta.main()

    #Filtrado de archivos provenientes del Petrinator
    (cantidad_estados, cantidad_plazas , cantidad_transiciones, matriz_es_tr, matriz_es_pl, state_deadlock) = filterdata.main()

    #Matrices
    (matriz_sifones,matriz_traps,cantidad_sifones,cantidad_traps)=siphones_traps(cantidad_plazas)

    (matriz_pos,matriz_pre)=matriz_pre_pos(cantidad_plazas,cantidad_transiciones)

    #T-invariantes
    t_invariant=invariantes(cantidad_transiciones)

    #print("\nIngrese: ")
    #print("1 - Primer analisis de la red")
    #print("2 - Análisis de red con supervisores")
    #print("3 - Red con supervisores, tratamiento de conflicto y t_idle")

    if (((analisis != "1")and(analisis != "2")and(analisis != "3")and(analisis != "S"))):
        finalizeCom()

    if(analisis=="1"):
        #Obtenemos la cantidad de plazas de la red original
        file_plazas = open(Jar_path + '/tmp/cantidad_plazas_red_original.txt', 'w')
        file_plazas.write(str(len(matriz_es_pl[0])))
        file_plazas.close()

        #Guardamos los T-invariantes de la red original
        file_t_inv_orig = open(Jar_path +  '/tmp/invariante_red_original.txt', 'w')
        for i in range (0, len(t_invariant)):
            for j in range(0, len(t_invariant[0])):
                file_t_inv_orig.write(str(t_invariant[i][j]) + ' ')
            file_t_inv_orig.write("\n")
        file_t_inv_orig.close()

        #print("\n")
        file_t_conflict_orig = open(Jar_path +  '/tmp/t_conflict_red_original.txt', 'w')
        file_t_conflict_orig.close()


    if(analisis=="2" or analisis=="1"  or analisis == "S"):#entro en la opcion S para obtener: sifon_deadlock
        
        sifon_idle=[] #Estado_idle sifon
        sifon_deadlock=[] #Estado_deadlock-sifon-marcado

        idle=1 #Sifones vacios estado inicial
        fun_sifones_deadlock(0,matriz_sifones,matriz_es_pl,idle,cantidad_plazas,cantidad_sifones,sifon_idle,sifon_deadlock)
        #print("Sifones vacios en idle",sifon_idle)

        #Llamada recursiva a fun_deadlock en busqueda de caminos que dirigen al deadlock
        idle=0 #Sifones en estado deadlock
        for i in range (0, len(state_deadlock)):
            fun_sifones_deadlock(state_deadlock[i],matriz_sifones,matriz_es_pl,idle,cantidad_plazas,cantidad_sifones,sifon_idle,sifon_deadlock)
        #print("Cantidad de estados con deadlock:", len(state_deadlock))
        respuesta = "Number of deadlock states: "+ str(len(state_deadlock)) +"<br>"
        #print("Cantidad de sifones vacios:", len(sifon_deadlock))
        respuesta += "Number of empty siphons: "+ str(len(sifon_deadlock)) +"<br>"

        lista_supervisores=[]

        for i in range(0, len(sifon_deadlock)):
            #Nos quedamos con un solo sifon
            sifon=np.copy(sifon_deadlock[i])
            
            #Agregamos el supervisor del bad-sifon
            respuesta +=supervisor(cantidad_transiciones,cantidad_plazas,sifon,matriz_es_tr,matriz_pos,matriz_pre,matriz_sifones,t_invariant,lista_supervisores)

        #Elimina archivo temporal
        os.remove("filtrado_prueba.txt")
        #respuesta
    if(analisis=="S"):
        respuesta = createString(len(sifon_deadlock))#le envio la cantidad de sifones
        #respuesta = respuesta.encode("UTF-8")

        #sCliente.send(len(respuesta).to_bytes(2, byteorder='big'))
        #sCliente.send(respuesta)
        #log.write(respuesta)
        print(respuesta,flush=True)

        #espero un ID
    
        #length_of_message = int.from_bytes(sCliente.recv(2), byteorder='big')
        #recv=sCliente.recv(length_of_message).decode("UTF-8")

        #length_of_message = input()
        recv = sys.stdin.readline().replace("\n","")
        if(recv == "q"):
            finalizeCom()
        id_int = int(recv)
        #id_int= 0 #int(input("AGREGA EL ID: ")) 
        new_red.main(lista_supervisores[id_int][0],lista_supervisores[id_int][1],lista_supervisores[id_int][2],lista_supervisores[id_int][3],Pflow_path)
        #nuevo
        respuesta = "Supervisor " + recv + " added succesfully"
    
    
    if(analisis=="3"):   #se obtienen los supervisores (3) o Anular brazos de idle a supervisores (4)
        
        file_plazas = open(Jar_path + '/tmp/cantidad_plazas_red_original.txt', 'r')
        cantidad_plazas_red_original=int(file_plazas.read())
        array_supervisor =[]
        for i in range (cantidad_plazas_red_original,len(matriz_es_pl[0])):
            array_supervisor.append(i)

        trans_idle=[] #Transiciones habilitadas en el marcado inicial
        #Transiciones que salen del estado idle
        for ii in range(cantidad_transiciones):
            if(matriz_es_tr[0][ii]!=-1):
                trans_idle.append(ii)

        #Guardamos los T-invariantes de la red original
        file_t_invariant_red_original = open(Jar_path + "/tmp/invariante_red_original.txt","r")

        t_invariant_red_original = []
        aux_t_inv = [] 

        for line in file_t_invariant_red_original:
            aux_t_inv.append(line)
        
        for i in range(len(aux_t_inv)):
            t_invariant_red_original.append(str(aux_t_inv[i]).split())
        
        #Guardamos los conflictos de la red original
        file_t_conflict_red_original = open(Jar_path +  "/tmp/t_conflict_red_original.txt","r")

        t_conflict_red_original = []
        t_conflict_red_original_aux = []
        aux_conflic = [] 

        for line in file_t_conflict_red_original:
            aux_conflic.append(line)
            
        for i in range(len(aux_conflic)):
            t_conflict_red_original_aux.append(str(aux_conflic[i]).split())
            
        if(len(t_conflict_red_original_aux)!=0):
            t_conflict_red_original = t_conflict_red_original_aux[0]
        

        msjadd = []
        msjdel = []
        #Buscamos eliminar los arcos de las transiciones idle cuyo T-invariante al que pertenece no le devuelve token al supervisor. (i.e arcos innecesarios)
        for i in range(len(trans_idle)): #Cantidad de trans_idle
            for j in range(len(t_invariant_red_original)): #cantidad de t-invariantes
                if(int(t_invariant_red_original[j][trans_idle[i]])==1): #La transicion idle forma parte del t-invariantes
                    for m in range(len(array_supervisor)):
                        cont_sup = 0
                        for l in range(len(t_invariant_red_original[j])):
                            if(int(t_invariant_red_original[j][l])==1):
                                if(int(matriz_pos[array_supervisor[m]][l])==1): #El T-invariante de la transicion idle le devuelve token al supervisor?
                                    cont_sup = 1 # si devuelve
                        if(cont_sup==0): #no devuelve
                            cont=0
                            for k in range(len(t_conflict_red_original)):
                                aux = int(t_conflict_red_original[k])
                                if(int(t_invariant_red_original[j][aux])==1): #La transicion en conflicto forma parte del T-invariante por lo tanto debe devolver el token 
                                    cont = cont + 1
                                    #print(f"La transicion en conflicto T{aux+1} le tiene que devolver un token al supervisor  P{array_supervisor[m]+1}")
                                    msjadd.append('Arc added from '+ str(f'T{aux+1}') + ' to ' + str(f'P{array_supervisor[m]+1}'))
                                    #Se agrega el arco
                                    arcosrdp.agregararco(Pflow_path,aux+1,array_supervisor[m]+1)

                            if(cont == 0):
                                if(int(matriz_pre[int(array_supervisor[m])][int(trans_idle[i])])==1):
                                    #print(f"Eliminar arco desde  P{array_supervisor[m]+1} hasta  T{trans_idle[i]+1}")
                                    msjdel.append('Deleted arc from '+ str(f'P{array_supervisor[m]+1}') + ' to ' + str(f'T{trans_idle[i]+1}'))
                                    
                                    #Se elimina el arco
                                    arcosrdp.eliminararco(Pflow_path, array_supervisor[m]+1, trans_idle[i]+1)

        respuesta=""
        #print("\n")
        for i in range (len(msjadd)):
            #print(msjadd[i])
            respuesta+=msjadd[i]+"<br>"
        for i in range (len(msjdel)):
            #print(msjdel[i])
            respuesta+=msjdel[i]+"<br>"
        
        if (respuesta==""):
            respuesta="There are no conflicts in the net<br>"
    print(respuesta,flush=True)    
    
try :
    #Variable globales
    id=0
    #name_pflow= ""
    Pflow_path =""

    Pflow_path=str(sys.argv[1])
    Jar_path = str(sys.argv[2])

    while(1): #El algoritmo se ejecuta iterativamente hasta que se controla la red. De no ser así se dice que el algoritmo no converge
        id=0
        main()
except Exception as e:
    error = "Error : " + str(e)
    print(error,flush=True)
    cleanTXTS()
    exit(1)
