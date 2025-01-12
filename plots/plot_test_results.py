import matplotlib.pyplot as plt
import numpy as np
import os
import math
# # Creating dataset
# np.random.seed(10)
# data = np.random.normal(100, 20, 200)
#
# fig = plt.figure(figsize=(10, 7))
#
# # Creating plot
# plt.boxplot(data)
#
# # show plot
# plt.show()

def gabriel(pose_array):
    node_mum = np.shape(pose_array)[0]
    gabriel_graph=[[1]*node_mum for _ in range(node_mum)]
    position_array=pose_array[:,:2]
    for u in range(node_mum):
        for v in range(node_mum):
            m=(position_array[u]+position_array[v])/2
            for w in range(node_mum):
                if w==v:
                    continue
                if  np.linalg.norm(position_array[w]-m)<np.linalg.norm(position_array[u]-m):
                    gabriel_graph[u][v]=0
                    gabriel_graph[v][u]=0
                    break
    return gabriel_graph
def get_convergence_time_average(raw_data,desired_distance=2,tolerrance=0.1,check_time=10):
    time_steps=raw_data.shape[1]
    check_timesteps=check_time*20
    check_window=[]
    for time_step in range(time_steps):
        data=raw_data[:,time_step,:]
        gabriel_graph = gabriel(data)
        stop=True
        distance_error_list=[]
        for i in range(len(gabriel_graph)):
            for j in range(i, len(gabriel_graph)):
                if not i == j:
                    if gabriel_graph[i][j] == 1:
                        distance = ((data[i,0] - data[j,0])**2 + (data[i, 1] - data[j,1])**2)**0.5
                        distance_error_list.append(math.fabs(distance - desired_distance))

        if len(check_window)<check_timesteps:
            check_window.append(distance_error_list)
        else:
            sum_distance_error=0
            num_data_point=0
            for i in range(len(check_window)):
                for j in range(len(check_window[i])):
                    sum_distance_error+=check_window[i][j]
                num_data_point+=len(check_window[i])
            average_formation_error= sum_distance_error/num_data_point
            if average_formation_error/desired_distance<=tolerrance:
                return time_step/20
            else:
                check_window.pop(0)
    return time_step/20
def get_convergence_time(raw_data,desired_distance=2,tolerrance=0.1,check_time=10):
    time_steps=raw_data.shape[1]
    realstop = 0
    for time_step in range(time_steps):
        data=raw_data[:,time_step,:]
        gabriel_graph = gabriel(data)
        stop=True
        for i in range(len(gabriel_graph)):
            for j in range(i, len(gabriel_graph)):
                if not i == j:
                    if gabriel_graph[i][j] == 1:
                        distance = ((data[i,0] - data[j,0])**2 + (data[i, 1] - data[j,1])**2)**0.5
                        if math.fabs(distance-desired_distance)/desired_distance>tolerrance:
                            stop=False
        if stop:
            realstop+=1
        else:
            realstop=0
        if realstop>=check_time*20:
            break
        # print(realstop)
    return time_step/20
def process_data(dir):
    paths = os.walk(dir)
    path_list=[]
    for path, dir_lst, file_lst in paths:
        for dir_name in dir_lst:

            path_list.append(os.path.join(path, dir_name))
    converge_time_all=[]
    average_formation_all=[]
    average_formation_error_all=[]
    unsuccess=0
    for path in path_list:
        file=os.path.join(path, "pose_array_scene.npy")
        raw_data=np.load(file)
        sim_time=raw_data.shape[1]*0.05
        convergence_time = get_convergence_time_average(raw_data)
        if convergence_time >= 100:
            unsuccess += 1
            print(path)
            continue
        observe_data=raw_data[:,-400:,:2]
        time_steps=observe_data.shape[1]
        for time_step in range(time_steps):
            data=observe_data[:,time_step,:]
            gabriel_graph=gabriel(data)
            reference=np.ones(data.shape[1])
            reference=reference*2
            distance_error_list=[]
            distance_list=[]
            for i in range(len(gabriel_graph)):
                for j in range(i,len(gabriel_graph)):
                    if not i==j:
                        if gabriel_graph[i][j]==1:
                            distance=np.sqrt(np.square(data[i,0]-data[j,0])+np.square(data[i,1]-data[j,1]))
                            # print(distance)
                            distance_list.append(distance)
                            distance_error=np.abs(distance-reference)
                            distance_error_list.append(distance_error)
        average_formation = np.average(np.array(distance_list))
        average_formation_error = 100*np.average(np.array(distance_error_list)) / 2
        converge_time_all.append(convergence_time)
        average_formation_error_all.append(average_formation_error)
        average_formation_all.append(average_formation)
        # break
    print(dir,unsuccess)
    return converge_time_all,average_formation_all,average_formation_error_all
    # print(observe_data-reference)

def box_1(data_m,title,ylabel,save_dir):
    fig = plt.figure(figsize=(5, 3))
    labels=[4,5,6,7,8,9]
    color_model='#1f77b4'
    color_expert='#ff7f0e'
    model=plt.boxplot(data_m,
                      positions=np.array(range(len(data_m))) * 1.0,
                      boxprops=dict(color=color_model),
                      capprops=dict(color=color_model),
                      whiskerprops=dict(color=color_model),
                      flierprops=dict(color=color_model,markeredgecolor=color_model),
                      medianprops=dict(color="black"),
                      widths=0.6)
    plt.subplots_adjust(left=0.18,
                        bottom=0.18,
                        right=0.99,
                        top=0.99,
                        wspace=0.0,
                        hspace=0.0)
    # plt.legend([model["boxes"][0], exp["boxes"][0]], ['GNN', 'Expert'], loc='upper left',borderpad=0.5,labelspacing=0.5)
    plt.xticks(np.array(range(len(data_m)))*1.0,labels=labels,fontsize=15)
    plt.yticks(fontsize=15)
    # plt.title(title,fontsize=18)
    plt.xlabel("Number of robots",fontsize=15)
    plt.ylabel(ylabel,fontsize=15)
    plt.savefig(os.path.join(save_dir,title+'.png'))
def box_2(data_m,data_e,title,ylabel,save_dir):
    fig = plt.figure(figsize=(2.5, 3))
    labels=["Expert","DNN"]
    color_model='#1f77b4'
    color_expert='#ff7f0e'
    print(title)
    print(sum(data_m[0])/len(data_m[0]))
    print(sum(data_e[0])/len(data_e[0]))
    model=plt.boxplot(data_m,
                      positions= [2.0],
                      boxprops=dict(color=color_model),
                      capprops=dict(color=color_model),
                      whiskerprops=dict(color=color_model),
                      flierprops=dict(color=color_model,markeredgecolor=color_model),
                      medianprops=dict(color="black"),
                      widths=0.4)
    exp=plt.boxplot(data_e,
                      positions= [1.0],
                      boxprops=dict(color=color_expert),
                      capprops=dict(color=color_expert),
                      whiskerprops=dict(color=color_expert),
                      flierprops=dict(color=color_expert,markeredgecolor=color_expert),
                      medianprops=dict(color="black"),
                      widths=0.4)
    # plt.legend([model["boxes"][0], exp["boxes"][0]], ['GNN', 'Expert'], loc='upper left',borderpad=2,labelspacing=2)
    plt.xticks([1,2], labels=labels, fontsize=15)
    plt.yticks(fontsize=15)
    # plt.tick_params(
    #     axis='x',  # changes apply to the x-axis
    #     which='both',  # both major and minor ticks are affected
    #     bottom=False,  # ticks along the bottom edge are off
    #     top=False,  # ticks along the top edge are off
    #     labelbottom=False)  # labels along the bottom edge are off
    # plt.title(title,fontsize=18)
    # plt.xlabel("Number of robots",fontsize=18)

    plt.subplots_adjust(left=0.3,
                        bottom=0.1,
                        right=0.99,
                        top=0.99,
                        wspace=0.0,
                        hspace=0.0)
    plt.ylabel(ylabel,fontsize=15)
    plt.savefig(os.path.join(save_dir,title+'.png'))
root_dir="/home/xinchi/GNN-control/data_final"

# dir4= os.path.join(root_dir,"model_4")
# converge_time_all_4,average_formation_all_4,average_formation_error_all_4=process_data(dir4)
# dir5= os.path.join(root_dir,"model_5")
# converge_time_all_5,average_formation_all_5,average_formation_error_all_5=process_data(dir5)
# dir6= os.path.join(root_dir,"model_6")
# converge_time_all_6,average_formation_all_6,average_formation_error_all_6=process_data(dir6)
# dir7= os.path.join(root_dir,"model_7")
# converge_time_all_7,average_formation_all_7,average_formation_error_all_7=process_data(dir7)
# dir8= os.path.join(root_dir,"model_8")
# converge_time_all_8,average_formation_all_8,average_formation_error_all_8=process_data(dir8)
# dir9= os.path.join(root_dir,"model_9")
# converge_time_all_9,average_formation_all_9,average_formation_error_all_9=process_data(dir9)
# converge_time_all_model=[converge_time_all_4,converge_time_all_5,converge_time_all_6,converge_time_all_7,converge_time_all_8,converge_time_all_9]
# average_formation_all_model=[average_formation_all_4,average_formation_all_5,average_formation_all_6,average_formation_all_7,average_formation_all_8,average_formation_all_9]
# average_formation_error_all_model=[average_formation_error_all_4,average_formation_error_all_5,average_formation_error_all_6,average_formation_error_all_7,average_formation_error_all_8,average_formation_error_all_9]


# dir= '/home/xinchi/6_robots/model_6'
# dir4_e= os.path.join(root_dir,"expert_adjusted_4")
# converge_time_all_4_e,average_formation_all_4_e,average_formation_error_all_4_e=process_data(dir4_e)
# dir5_e= os.path.join(root_dir,"expert_adjusted_5")
# converge_time_all_5_e,average_formation_all_5_e,average_formation_error_all_5_e=process_data(dir5_e)
# dir6_e= os.path.join(root_dir,"expert_adjusted_6")
# converge_time_all_6_e,average_formation_all_6_e,average_formation_error_all_6_e=process_data(dir6_e)
# dir7_e= os.path.join(root_dir,"expert_adjusted_7")
# converge_time_all_7_e,average_formation_all_7_e,average_formation_error_all_7_e=process_data(dir7_e)
# dir8_e= os.path.join(root_dir,"expert_adjusted_8")
# converge_time_all_8_e,average_formation_all_8_e,average_formation_error_all_8_e=process_data(dir8_e)
# dir9_e= os.path.join(root_dir,"expert_adjusted_9")
# converge_time_all_9_e,average_formation_all_9_e,average_formation_error_all_9_e=process_data(dir9_e)
# converge_time_all_expert=[converge_time_all_4_e,converge_time_all_5_e,converge_time_all_6_e,converge_time_all_7_e,converge_time_all_8_e,converge_time_all_9_e]
# average_formation_all_expert=[average_formation_all_4_e,average_formation_all_5_e,average_formation_all_6_e,average_formation_all_7_e,average_formation_all_8_e,average_formation_all_9_e]
# average_formation_error_all_expert=[average_formation_error_all_4_e,average_formation_error_all_5_e,average_formation_error_all_6_e,average_formation_error_all_7_e,average_formation_error_all_8_e,average_formation_error_all_9_e]


dir5= os.path.join(root_dir,"model_5")
converge_time_all_5,average_formation_all_5,average_formation_error_all_5=process_data(dir5)
converge_time_all_model=[converge_time_all_5]
average_formation_all_model=[average_formation_all_5]
average_formation_error_all_model=[average_formation_error_all_5]


# dir= '/home/xinchi/6_robots/model_6'

dir5_e= os.path.join(root_dir,"expert_adjusted_5")
converge_time_all_5_e,average_formation_all_5_e,average_formation_error_all_5_e=process_data(dir5_e)
converge_time_all_expert=[converge_time_all_5_e]
average_formation_all_expert=[average_formation_all_5_e]
average_formation_error_all_expert=[average_formation_error_all_5_e]


#
# box_1(converge_time_all_model,"Converge time","Convergence Time(s)",root_dir)
# box_1(average_formation_all_model,"Average distance","Distance(m)",root_dir)
# box_1(average_formation_error_all_model,"Average group formation error","Formation Error(%)",root_dir)
box_2(converge_time_all_model,converge_time_all_expert,"Converge time 5","Convergence Time(s)",root_dir)
box_2(average_formation_all_model,average_formation_all_expert,"Average distance 5","Distance(m)",root_dir)
box_2(average_formation_error_all_model,average_formation_error_all_expert,"Average group formation error 5","Formation Error(%)",root_dir)