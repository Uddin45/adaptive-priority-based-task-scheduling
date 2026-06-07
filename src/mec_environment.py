import multiprocessing
import random
import collections
from collections import deque
from multiprocessing import Queue
import time

from queue import Empty

import numpy as np

from mec_server import MECServer
from user_tasks import User


class MECEnvironment:
    def __init__(self, user_cnt=1, mec_cnt=1,Env_Type=0, frequency=[2,4,8,16], frequency_ratio_resolution=5):
        """

        :param user_cnt: initialize the number of users
        :param mec_cnt:  initialize the number of MEC servers
        """
        self.freq=frequency
        self.env_type=Env_Type
        self.mec_servers = []
        self.user_cnt = user_cnt
        self.mec_cnt = mec_cnt
        self.num_priority_class=3
        self.frequency_ratio_resolution = frequency_ratio_resolution
        self.speed_matrix = np.zeros((1, mec_cnt))
        self.speed_matrix_tasks = np.zeros(( self.num_priority_class,mec_cnt))
        self.trans_speed_matrix={}
        self.user_speeds={}
        self.tasks_queue = multiprocessing.Queue()
        self.users = User(user_cnt, self.tasks_queue,self.env_type)
        self.actions = self.generate_actions()
        self.current_tasks = []
        if self.env_type!=2:
            self.max_freq_server=[np.random.choice(self.freq)*1e9 for _ in range (3)]
        else: 
            self.max_freq_server=[8*1e9,16*1e9,4*1e9]
        # for i in range(user_cnt):
        #     self.users.append(User(index=i, evn_queue=self.tasks_queue))
        self.min_freq_server=2*1e9
        for j in range(mec_cnt):
            max_frequency =  self.max_freq_server[j]
            self.mec_servers.append(MECServer(index=j, max_frequency=max_frequency))
           
        self.get_current_speed(1,[10,10,10])
        
        # Create three collections deque according to priority
        self.priority_queues = [list() for _ in range(self.num_priority_class)]
        
       
        self.tasks= self.tasks_queue.get()
        print(len(self.tasks))
        print(self.trans_speed_matrix)
        for task in self.tasks:
            self.priority_queues[task['priority']-1].append(task)
        #time.sleep(np.random.random_sample()*0.01)
        
           
       # print(self.priority_queues[0][0])
        #print(self.priority_queues[1][0])
        #print(self.priority_queues[2][0])
        print(len(self.priority_queues[0]))
        print(len(self.priority_queues[1]))
        print(len(self.priority_queues[2]))
        print(self.priority_queues[0][0])
        print(self.priority_queues[1][0])
        print(self.priority_queues[2][0])
        
        
        
       # self.current_tasks = [list() for _ in range(3)]
                
       # self.current_tasks_P1=[]
       # self.current_tasks_P2=[]
       # self.current_tasks_P3=[]
        
        
      
        
        
                

    def generate_actions(self):
        if self.env_type==1:
            actions = []
            #task_index=[0,1,2]
            freq = np.linspace(0.1, 1, num=self.frequency_ratio_resolution)
            for i in range(self.mec_cnt):
                for j in range(freq.shape[0]):
                    for k in range(self.num_priority_class):
                        actions.append((i, freq[j], k))
        else: 
            actions = []
            #task_index=[0,1,2]
            freq = np.linspace(0.1, 1, num=self.frequency_ratio_resolution)
            for i in range(self.mec_cnt):
                for j in range(freq.shape[0]):
                    
                    
                    actions.append((i, freq[j]))
        return actions

    # def generate_multi_action(self):
    #     actions = []
    #     freq = np.linspace(0.2, 1, num=self.frequency_ratio_resolution)
    #     for u in range(self.user_cnt):
    #         for m in range(self.mec_cnt):
    #             for f in range(freq.shape[0]):
    #                 actions.append((u, m, freq[f]))
    #     return actions

   
    def transmission_speed(self,user_id,user_distance,alpha=2e7, power=150, distance=50, noise=0.01):
        """
        compute the transmission speed
        :param alpha: the bandwith value 10MHz
        :param power: current power for transmit the data 32mW-197mW
        :param distance: distance of transmit
        :param noise: the variance of complex white Gaussian channel noise
        :return:
        """
        power=300
            
        distance=user_distance
        #print(distance)
        path_loss = np.power(distance, -3.5)
        h = np.random.rayleigh()  # channel gain is Rayleigh distribution
        if distance==0:
            speed=0
        else: 
            speed = alpha * np.log2(1 + power * h ** 2 * path_loss / noise)
       
        return speed  # average speed is around 473888.88 bit/s

    def get_current_speed(self,priority_user_idx,user_distance):

        #if priority_user_idx in self.user_speeds:
          #  speed = self.user_speeds[priority_user_idx]
        #else:
         #   speed = self.transmission_speed(priority_user_idx)
         #   self.user_speeds[priority_user_idx] = speed
    
        for i in range(self.mec_cnt):
            self.speed_matrix[0, i] = self.transmission_speed(priority_user_idx,user_distance[i])
    
        return self.speed_matrix

    def get_mec_states(self):
        mec_states = []
        for mec in self.mec_servers:
            mec_states.append(mec.get_state())
        return np.array(mec_states)

    def get_state(self, task, new_step=True):
        
        if self.env_type != 3:
            for tsk in task:
                if not tsk:
                    
                    task.remove(tsk)
                    
                    tsk = {
                        'data_size': 0,
                        'circle': 0,
                        'delta_max': 0,
                        'user_index': 0,
                        'priority': 0,
                        
                        'user_distance':[1000,1000,1000],
                        'req_freq_percent': 0
                    }
                    task.append.tsk
                 
            
           # task[0]['user_distance']=random.randint(26,75)
           # task[1]['user_distance']=random.randint(26,75)
           # task[2]['user_distance']=random.randint(26,75)
            
            self.speed_matrix_tasks[0, :] = self.get_current_speed(task[0]['user_index'],task[0]['user_distance'])
            if task[1]['user_index']==task[0]['user_index']:
                self.speed_matrix_tasks[1, :] = self.speed_matrix_tasks[0, :]
            else:
                self.speed_matrix_tasks[1, :] = self.get_current_speed(task[1]['user_index'],task[1]['user_distance'])
            if task[2]['user_index']==task[1]['user_index'] :
                self.speed_matrix_tasks[2, :] = self.speed_matrix_tasks[1, :]
            elif task[2]['user_index']==task[0]['user_index'] :
                self.speed_matrix_tasks[2, :] = self.speed_matrix_tasks[0, :]
            else:
                self.speed_matrix_tasks[2, :] = self.get_current_speed(task[2]['user_index'],task[2]['user_distance'])
            
            self.trans_speed_matrix = {item['user_index']: { 'speed': self.speed_matrix_tasks[i,:]} for i, item in enumerate(task)}
            
        

            
            
            self.speed_matrix_tasks = self.speed_matrix_tasks / np.linalg.norm(self.speed_matrix_tasks)
            mec_states = self.get_mec_states()
    
            state = self.speed_matrix_tasks.flatten('F').tolist() + mec_states.flatten('F').tolist()
            task_states=np.array([])
            for i in range(len(task)):
                
                new_task_state = np.array([task[i]['data_size']/2e4, task[i]['circle']/10e6, task[i]['delta_max']/0.2, task[i]['priority']/3])
                task_states = np.append(task_states, new_task_state)
            
            # task_states = task_states / np.linalg.norm(task_states)
            state = np.array(state + task_states.flatten('F').tolist())
            
        else:
            
            if not task:
                task = {'data_size': 0, 'circle': 0, 'delta_max': 0, 'user_index': 0,'priority':0,'user_distance':[1000,1000,1000],'req_freq_percent': 0}
                print("*************Task is empty*******************************")
            #task['user_distance']=random.randint(26,75)
            speeds = self.speed_matrix
            if new_step and np.random.random_sample() > 0.0:
                speeds = self.get_current_speed(task['user_index'],task['user_distance'])
            speeds = speeds / np.linalg.norm(speeds)
            mec_states = self.get_mec_states()
    
            state = speeds.flatten('F').tolist() + mec_states.flatten('F').tolist()
            task_states = np.array([task['data_size'] / (2e4), task['circle'] / (10e6),
                                     task['delta_max']])
            # task_states = task_states / np.linalg.norm(task_states)
            state = np.array(state + task_states.flatten('F').tolist())
        # state = state / np.linalg.norm(state)
            # state = state / np.linalg.norm(state)
        return state

    def action_size(self):
        return len(self.actions)
        
    def get_task(self):
        if self.env_type!=3:
            priority_task=[dict() for _ in range( self.num_priority_class) ]
            if np.any([len(q)<=1 for q in self.priority_queues]):
                # while True:
                    tasks = self.tasks_queue.get()
                    if tasks:
                        for task in tasks:
                            self.priority_queues[task['priority']-1].append(task)
                        # break
                        
            for i in range (self.num_priority_class):
                if (len(self.priority_queues[i])) > 0:
                    priority_task[i] = self.priority_queues[i][0]
                else:
                    priority_task[i]={'data_size': 0, 'circle': 0, 'delta_max':0, 'priority':0,'user_index': 0,'user_distance':[1000,1000,1000],'req_freq_percent': 0}
    
                #else:
                   # priority_task[i]={'data_size': 0, 'circle': 0, 'delta_max':0, 'priority':0,'user_index': 0,'req_freq_percent': 0}
                    #print(f"Queue {i} is empty at {t_step}")
                    
            return priority_task
        else: 
            if len(self.current_tasks) > 0:
                task = self.current_tasks.pop()
                
                return task

            else:
                while True:
                    tasks = self.tasks_queue.get()
                    if tasks:
                        self.current_tasks = self.current_tasks + tasks
                        return self.current_tasks.pop()
       
    def state_size(self):
        """
        state size is equal to shape of speed matrix + MEC server states + size of task
        MEC server states has two elements including waiting time time and max frequency
        :return:
        """
        # state_size = self.mec_cnt * self.user_cnt + self.mec_cnt * 2 + 4
        if self.env_type!=3:
            
            state_size = 3*self.mec_cnt + self.mec_cnt * 2 + 4*3
        else: 
            state_size = self.mec_cnt + self.mec_cnt * 2 + 3
        return state_size

    def step(self, action, task, max_waiting=25):
        """
        choose action given by the task
        :param action:
        :param task:
        :param max_waiting: threshold of maximum waiting time of all the MEC sever
        :return:
        """
        if self.env_type==1:
            actions = self.actions[action]
            rec_mec_index = actions[0]
            re_freq = actions[1]
            task_idx=actions[2]
            
            if (len(self.priority_queues[task_idx])) > 0:
                action_task=self.priority_queues[task_idx].pop(0)
                user=action_task['user_index']
                
                action_task['req_freq_percent'] = re_freq
                action_task['req_server_id']=rec_mec_index
                self.mec_servers[rec_mec_index].receive_task(action_task)
                trans_speed = self.trans_speed_matrix[user]['speed'][rec_mec_index]
                
                #print(user, rec_mec_index, trans_speed,self.trans_speed_matrix )
    
                reward = self.mec_servers[rec_mec_index].mec_reward(re_freq, action_task, trans_speed,self.env_type)
            else:
                action_task={'data_size': 0, 'circle': 0, 'delta_max':0, 'priority':0,'user_index': 0,'user_distance':  [1000,1000,1000],'req_freq_percent': 0}          
                reward = {'reward': round(-100.0, 2), 'task_done': 0, 'energy': 0,'latency': 0.0,'lat_vec':[0,0,0]}
    
            max_queue_time = max([mec.queue_time for mec in self.mec_servers])
            if any(item < 0 for item in [mec.queue_time for mec in self.mec_servers]):
                print("negative")
    
            done = True if max_queue_time >= max_waiting else False
            
            
            next_task=self.get_task()
        
            next_state = self.get_state( next_task, new_step=True)
            return next_state, reward, done ,action_task,next_task,rec_mec_index
        else:
            actions = self.actions[action]
            rec_mec_index = actions[0]
            re_freq = actions[1]
            
            task['req_freq_percent'] = re_freq
            self.mec_servers[rec_mec_index].receive_task(task)
            trans_speed = self.speed_matrix[0, rec_mec_index]
    
            reward = self.mec_servers[rec_mec_index].mec_reward(re_freq, task, trans_speed,self.env_type)
            max_queue_time = max([mec.queue_time for mec in self.mec_servers])
            # print("max_queue_time=", max_queue_time)
            done = True if max_queue_time >= max_waiting else False
            #print(task)
            action_task=task
            
            next_task=self.get_task()
        
            next_state = self.get_state( next_task, new_step=True)
            return next_state, reward, done ,action_task,next_task,rec_mec_index
    def greedy_step(self, action, task,greedy_task_idx, max_waiting=25):
        """
        choose action given by the task
        :param action:
        :param task:
        :param max_waiting: threshold of maximum waiting time of all the MEC sever
        :return:
        """
        
        
        rec_mec_index = action[0][0]
        re_freq = action[0][1]
        
        
        if (len(self.priority_queues[greedy_task_idx])) > 0:
            action_task=self.priority_queues[greedy_task_idx].pop(0)
            user=action_task['user_index']
            
            action_task['req_freq_percent'] = re_freq
            self.mec_servers[rec_mec_index].receive_task(action_task)
            trans_speed = self.trans_speed_matrix[user]['speed'][rec_mec_index]
            
            #print(user, rec_mec_index, trans_speed,self.trans_speed_matrix )

            reward = self.mec_servers[rec_mec_index].mec_reward(re_freq, action_task, trans_speed,self.env_type)
        else:
            action_task={'data_size': 0, 'circle': 0, 'delta_max':0, 'priority':0,'user_index': 0,'user_distance':[1000,1000,1000],'req_freq_percent': 0}
            reward = {'reward': round(-100.0, 2), 'task_done': 0, 'energy': 0,'latency': 0.0,'lat_vec':[0,0,0]}

        max_queue_time = max([mec.queue_time for mec in self.mec_servers])
        # print("max_queue_time=", max_queue_time)
        done = True if max_queue_time >= max_waiting else False
        
        
        next_task=self.get_task()
        
        next_state = self.get_state( next_task, new_step=True)
        return next_state, reward, done ,action_task,next_task,rec_mec_index
        

    @staticmethod
    def clear_queue(queue):
        try:
            while True:
                queue.get_nowait()
        except Empty:
            pass

    def reset(self):
        # for user in self.users:
        # user.send_task.join()
        # user.send_task.start()
        for mec in self.mec_servers:
            # mec.processing.join()
            # mec.processing.start()
            self.clear_queue(mec.tasks_queue)
            mec.queue_time = 0
        self.priority_queues = [list() for _ in range(self.num_priority_class)]
        self.clear_queue(self.tasks_queue)
        if self.env_type==4:
            
            self.mec_servers = []
            for j in range(self.mec_cnt):
                max_frequency =  self.max_freq_server[j]
                self.mec_servers.append(MECServer(index=j, max_frequency=max_frequency))
        else: 
            self.max_freq_server=[np.random.choice(self.freq)*1e9 for _ in range (3)]
            self.mec_servers = []
            for j in range(self.mec_cnt):
                max_frequency =  self.max_freq_server[j]
                self.mec_servers.append(MECServer(index=j, max_frequency=max_frequency))

    def close(self):
        self.users.send_task.join()
        for m in self.mec_servers:
            m.processing.join()


if __name__ == '__main__':
    mec_evn = MECEnvironment(user_cnt=3, mec_cnt=5)
    print('Hello')
    # print("speed_matrix=", mec_evn.speed_matrix)
    # print("speed_transform_prob_matrix=", mec_evn.speed_transform_prob_matrix)
    # print("current_speed_matrix=", mec_evn.current_speed_matrix)
    # print("next_speed=", mec_evn.next_speed_matrix())
    # print("state=", mec_evn.get_state())
    # print('not')