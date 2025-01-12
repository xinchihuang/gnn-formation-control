# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 23:09:34 2017
This test file is dependent on vrep.
To run this file, please open vrep file scene/scene_double.ttt first
@author: cz
"""
import os
from scene import Scene
from scene import VrepError
from sceneplot import ScenePlot
# from robot import Robot
import numpy as np
import math
import random
# from data import Data
#from DeepFCL import DeepFCL
from suhaas_agent import Agent
from plots.plot_scene import plot_scene
import torch
import saver
import time
import matplotlib.pyplot as plt


import argparse
parser = argparse.ArgumentParser(description='Args for demo')

parser.add_argument('--expert_only', dest='expert_only', default=False,type=bool,help='Use expert control only')
parser.add_argument('--use_dagger', dest='use_dagger', default=False,type=bool,help='Use dagger for training only')
parser.add_argument('--if_train', dest='if_train', default=False,type=bool,help='Control demo mod(train/test)')
parser.add_argument('--if_continue', dest='if_continue', default=False,type=bool,help='Continue training')
parser.add_argument('--use_cuda', dest='use_cuda', default=True,type=bool,help='Use cuda')
parser.add_argument('--expert_velocity_adjust', dest='expert_velocity_adjust', default=True,type=bool,help=' Adjust controller output accoring to the ralative distance output when using expert control')
parser.add_argument('--model_path', dest='model_path', default='pretrained_model',type=str,help='Path to save model')
parser.add_argument('--model_name', dest='model_name', default='model_5.pth',type=str,help='Name of model')
parser.add_argument('--robot_num', dest='robot_num', default=5,type=int,help='Number of robot for simulation')
parser.add_argument('--position_range', dest='position_range', default=5,type=int,help='Set robots position within the range')
parser.add_argument('--sim_dt', dest='sim_dt', default=0.05,type=float,help='Simulation time step')
parser.add_argument('--sim_time', dest='sim_time', default=100,type=float,help='Simulation time for one simulation')
parser.add_argument('--stop_thresh', dest='stop_thresh', default=0.1,type=float,help='Stopping thresh')
parser.add_argument('--stop_waiting_time', dest='stop_waiting_time', default=5,type=float,help='Stopping after this time')
parser.add_argument('--desire_distance', dest='desire_distance', default=2.0,type=float,help='Desire formation distance')
parser.add_argument('--train_episode', dest='train_episode', default=1000,type=int,help='Episode for training')
parser.add_argument('--batch_size', dest='batch_size', default=16,type=int,help='Batch size for training')
parser.add_argument('--iter', dest='iter', default=1,type=int,help='Iter for testing multiple round')
parser.add_argument('--inW', dest='inW', default=100,type=int,help='Dataset shape')
parser.add_argument('--inH', dest='inH', default=100,type=int,help='Dataset shape')
parser.add_argument('--save_iteration', dest='save_iteration', default=10,type=int,help='Save after certain iterations')
parser.add_argument('--saved_figs', dest='saved_figs', default="results",type=str,help='Save after certain iterations')
# # modelname='model_'+str(robot_num)+'robots_'+str(simTime)+'s_'+str(trainEpisode)+'rounds'+'.pth'
args = parser.parse_args()

def set_robot_positions(sc,position_list):
    for i in range(len(position_list)):
        sc.robots[i].setPosition(position_list[i])
    return sc


def Test(args):
    for iteration in range(1,0,-1):
        fcl = Agent(batch_size=args.batch_size, inW=args.inW, inH=args.inH, nA=args.robot_num,cuda=args.use_cuda)
        #### Initial Agent

        ##### Initial and record scene
        sc = generate_scene(dt=args.sim_dt, num_run=0, robot_num=args.robot_num, if_train=args.if_train,
                            expert_only=args.expert_only,
                            use_dagger=args.use_dagger, sim_time=args.sim_time, position_range=args.position_range,
                            desired_distance=args.desire_distance, stop_thresh=args.stop_thresh,
                            expert_velocity_adjust=args.expert_velocity_adjust,
                            agent=fcl)
        position_list=[]
        for i in range(len(sc.robots)):
            position=[sc.robots[i].xi.x,sc.robots[i].xi.y,sc.robots[i].xi.theta]
            position_list.append(position)

        ##### Test model
        # position_list=[[-4, -4, 0],
        #                     [-4, 4, 0],
        #                     [4, 4, 0],
        #                     [4, -4, 0],
        #                     [0, 0, 0]]


        ##### Test model

        model_type = "model_" + str(args.robot_num)
        print(model_type)
        print(position_list)
        if (not args.if_train):
            # model_name="suhaas_model_v13_dagger_final_more.pth"
            model_name = args.model_name
            # fcl.model.to('cpu')
            # fcl.model.load_state_dict(torch.load(os.path.join(args.model_path, model_name)))
            if args.use_cuda:
                fcl.model.to('cpu')
                fcl.model.load_state_dict(torch.load(os.path.join(args.model_path, model_name)))
                fcl.model.to('cuda')
            else:
                fcl.model.to('cpu')
                fcl.model.load_state_dict(torch.load(os.path.join(args.model_path, model_name),map_location=torch.device('cpu')))
        sc = generate_scene(dt=args.sim_dt, num_run=0, robot_num=args.robot_num, if_train=args.if_train,
                            expert_only=False,
                            use_dagger=args.use_dagger, sim_time=args.sim_time, position_range=args.position_range,
                            desired_distance=args.desire_distance, stop_thresh=args.stop_thresh,
                            expert_velocity_adjust=args.expert_velocity_adjust,
                            agent=fcl)

        sc = set_robot_positions(sc, position_list)
        sc0 = simulate(args.sim_time, args.sim_dt, args.stop_waiting_time, args.desire_distance, args.stop_thresh, sc)
        sc0.save_robot_states(os.path.join(args.saved_figs, model_type, "demo"))
        plot_scene(sc0,"", os.path.join(args.saved_figs, model_type, "demo"))



def initRef(sc):

    # set desired velocity vector
    sc.xid.vRefMag = 0.7
    sc.xid.vRefAng = 2 * math.pi * random.random()#0.982793723# 2 * math.pi * random.random()
    sc.xid.theta = 0
    sc.xid.sDot = 0
    sc.xid.thetaDot = 0
    # scale desired formation separation
    #alphaList = [1.0, 1.5, 2.0]
    #alphaList = [1.0,2.0,3.0,4.0,4.5]
    alphaList = [2.0]
    alpha = random.choice(alphaList)
    sc.scaleDesiredFormation(alpha)
    message = "vRefMag: {0:.3f}, vRefAng: {1:.3f}, alpha: {2:.3f}"
    message = message.format(sc.xid.vRefMag, sc.xid.vRefAng, alpha)
    sc.log(message)
    print(message)

def generate_scene(dt,num_run,robot_num,if_train,expert_only,use_dagger,sim_time,position_range,
                   desired_distance,stop_thresh,expert_velocity_adjust,agent):

    sc = Scene(dt,num_run,robot_num,if_train,expert_only,use_dagger,desired_distance,stop_thresh,expert_velocity_adjust,fileName=__file__, recordData=True)
    sp = ScenePlot(sc)
    sp.saveEnabled = True  # save plots?
    sc.occupancyMapType = sc.OCCUPANCY_MAP_BINARY
    # sc.dynamics = 18 # robot dynamics
    sc.errorType = 0
    for i in range(robot_num):
        sc.addRobot(np.float32([[i, 0, 1], [0.0, 0.0, 0.0]]),learnedController=agent.test)
    # No leader
    I = np.identity(robot_num, dtype=np.int8)
    M = np.ones(robot_num, dtype=np.int8)
    sc.setADjMatrix(M - I)

    # Set robot 0 as the leader.desired_distance,expert_velocity_adjust

    # vrep related
    sc.initVrep()
    # Choose sensor type
    # sc.SENSOR_TYPE = "VPL16" # None, 2d, VPL16, kinect
    sc.SENSOR_TYPE = "VPL16"  # None, 2d, VPL16, kinect
    sc.objectNames = ['Pioneer_p3dx', 'Pioneer_p3dx_leftMotor', 'Pioneer_p3dx_rightMotor']
    # change the # of instantiations according to "robot_num"
    # print(sc.SENSOR_TYPE)
    if sc.SENSOR_TYPE == "None":
        sc.setVrepHandles(0, '')
        for i in range(1, robot_num + 1):
            sc.setVrepHandles(i, '#' + str(i))
        # sc.setVrepHandles(1, '#0')

    elif sc.SENSOR_TYPE == "VPL16":
        sc.objectNames.append('velodyneVPL_16')  # _ptCloud
        print(sc.objectNames)
        for i in range(robot_num):
            checkn = i - 1
            s = ''
            if (i >= 1):
                s += '#' + str(checkn)
            sc.setVrepHandles(i, s)

    # sc.renderScene(waitTime = 3000)
    tf = sim_time  ## must lager than 3

    CheckerEnabled = False
    initRef(sc)  # sc.resetPosition(robot_num*np.sqrt(2)) # Random initial position
    sc.resetPosition(position_range)
    return sc
def simulate(sim_time,sim_dt,stop_waiting_time,desire_distance,stop_thresh,sc):
    try:
        tf = sim_time ## must lager than 3
        initRef(sc) #sc.resetPosition(robot_num*np.sqrt(2)) # Random initial position
        # sp.plot(4, tf,expert=args.expert_only)
        realstop = int(stop_waiting_time/sim_dt)
        stop=False
        while sc.simulate():
            # if sc.check_stop_condition(desire_distance,stop_thresh):
            #     stop=True
            if sc.t > tf or stop:
                break
                # print("stop")
                # if realstop>0:
                #     realstop-=1
                # else:
                #     print("Stop at")
                #     print(sc.t)
                #     break
            # else:
            #     realstop=int(stop_waiting_time/sim_dt)
    except KeyboardInterrupt:
        x = input('Quit?(y/n)')
        if x == 'y' or x == 'Y':
            tf = sc.t - 0.01
            raise Exception('Aborted.')
    except VrepError as err:
        sc.log(err.message)
        print(err.message)
        return None
    except:
        raise
    finally:
        sc.deallocate()
    return sc


Test(args)


