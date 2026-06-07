from datetime import datetime

from enum import Enum
import time
import multiprocessing
import threading
import math
import numpy as np


class State(Enum):
    """
    flag of the server status
    """
    RUNNING = 0
    IDLE = 1


class MECServer:
    """
     MEC server
    """

    def __init__(self, index=0, queue_time=0,
                 power=0.6,
                 min_frequency=2 * 1e9,
                 max_frequency=16* 1e9,
                 max_queue_size=500,
                 max_queue_wait=10,
                 alpha=0.5):
        """
        tasks_queue : store the information of the tasks in the queue waiting for processing
        :param index : index of the object
        :param queue_time : waiting for task queue time
        :param power: current power for transmit the data 32mW-197mW
        :param min_frequency: the frequency of CPU when IDLE status Hz
        :param max_frequency: maximum frequency of the server CPU GZ (1GHz = 10^9 clock cycles per second)
        """
        self.index = index
        self.tasks_queue = multiprocessing.Queue()
        self.queue_time = queue_time
        self.power = power
        self.min_frequency = min_frequency
        self.max_frequency = max_frequency
        self.current_frequency = self.min_frequency  # IDLE
        self.queue_time = 0  # maintain waiting time in the queue
        self.current_task_start_time = None  # record of current task start time
        self.running_task = None
        self.max_queue_wait = max_queue_wait
        self.max_queue_size = max_queue_size
        self.alpha = alpha
        self.state = State.IDLE
        self.processing = threading.Thread(target=self.execute_task)
        self.processing.start()

    def update_waiting_time(self):
        """
        computing waiting time
        waiting time = Queue time + remain running task time
        :return:
        """
        if self.state == State.RUNNING and self.running_task:
            running_time = datetime.now() - self.current_task_start_time
            req_freq = max(self.min_frequency, self.running_task['req_freq_percent'] * self.max_frequency)
            remain_time = self.running_task['circle']/req_freq - running_time.total_seconds()
            remain_time=max(0,remain_time)
            waiting_time = self.queue_time + remain_time
            return waiting_time
        else:
            return self.queue_time

    def receive_task(self, task):
        if self.tasks_queue.qsize() < self.max_queue_size:
            self.tasks_queue.put(task)
            req_freq = max(self.min_frequency, task['req_freq_percent'] * self.max_frequency)
            self.queue_time += task['circle'] / req_freq
        else:
            self.queue_time = self.max_queue_wait

    def get_state(self):
        waiting_time = self.update_waiting_time()
        states = [waiting_time / 25, self.max_frequency / (16e9)]
        return states

    def energy_consumption(self, rec_freq, task, trans_speed,total_time,Env_Type):
        
        self.power=0.3
        k = math.pow(10, -26)
        transmit_energy = self.power * (task['data_size'] / trans_speed)
        compute_energy = k * (rec_freq ** 2) * task['circle']
        
        return transmit_energy+compute_energy ,transmit_energy,compute_energy

    def mec_reward(self, rec_freq_percent, task, trans_speed,Env_Type, continue_reward=0.5,
                   task_weight=3, energy_weight=1):
        
        rec_freq = self.max_frequency * rec_freq_percent
        rec_freq = max(rec_freq, self.min_frequency)
        transmit_time = task['data_size'] / trans_speed
        compute_time = task['circle'] / rec_freq
        wait_time=self.update_waiting_time()
        total_time = transmit_time + compute_time + wait_time
        task_done = 0
        energy_weight=1
        if total_time<=task['delta_max']:
            task_done=1
        energy,trans_energy,comp_energy = self.energy_consumption(rec_freq, task, trans_speed,total_time,Env_Type) 
        lat_vector=[transmit_time,  compute_time,  wait_time]
        eng_vector=[trans_energy,comp_energy]
        if Env_Type==1:
            #scale_factor=0.25
            if task['priority']==3:
                continue_reward=0.25
    
                #task_weight=3+(task['priority']-1)* scale_factor
                #time_weight=1
                self.alpha=0.5
                
                
                energy_weight=1
                task_weight=0.2
                
                time_weight=1.35
                
                    
                #scale_factor=1/min(task_weight,energy_weight)
            elif task['priority']==2:
                continue_reward=0.25
                self.alpha=0.5
                
    
              #  task_weight=3+(task['priority']-1)* scale_factor
                
                energy_weight=1
                task_weight=1.15
                
                time_weight=1.15
                
                #time_weight=1
                
                #scale_factor=1/min(task_weight,energy_weight)
                
            else: 
                
                continue_reward=0.25
                self.alpha=0.5
               # task_weight=3+(task['priority']-1)* scale_factor
                time_weight=1.0 #0.525
                energy_weight=1
                task_weight=0.3
               # time_weight=1
               
                #scale_factor=1/min(task_weight,energy_weight)
            delta_delay=task['delta_max']-total_time
            
            #if delta_delay>=0:
            reward_lat= 1*time_weight *  self.alpha  * np.log2(1+abs(delta_delay))*task_done
            reward_eng=1*self.alpha * energy_weight * np.log2(energy+1)
            reward = continue_reward + reward_lat-reward_eng
            reward = float(np.clip(reward, -15, 15))
            #else:
              #  reward = continue_reward  +task_weight*task_done*self.alpha- time_weight *  self.alpha  * np.log2(1+abs(delta_delay))- self.alpha * energy_weight * np.log2(energy+1)
              #  reward = float(np.clip(reward, -15, 15))




            
            
            
    
        else: 
            continue_reward=0.25
            delta_delay=task['delta_max']-total_time
            time_weight=1.15
            energy_weight=1
            
            reward_lat= 1*time_weight *  self.alpha  * np.log2(1+abs(delta_delay))*task_done
            reward_eng=1*self.alpha * energy_weight * np.log2(energy+1)
            reward = continue_reward + reward_lat-reward_eng
            reward = float(np.clip(reward, -15, 15))
        
        return {'reward': round(reward, 2), 'task_done': task_done, 'energy': energy,'latency':total_time,'lat_vec':lat_vector,'eng_vector':eng_vector,'reward_lat':reward_lat,'reward_eng':reward_eng}

    def execute_task(self):
        while True:
            task = self.tasks_queue.get()
            if task:
                if self.state == State.IDLE:
                    self.state = State.RUNNING
                self.running_task = task
                self.current_task_start_time = datetime.now()
                self.current_frequency = task['req_freq_percent'] * self.max_frequency
                self.current_frequency = max(self.current_frequency, self.min_frequency)
                run_time = task['circle'] / self.current_frequency
                # print("MEC[{}] is a running task from User[{}] ...".format(self.index, task['user_index']))
                time.sleep(run_time)  # simulate run time
                self.queue_time -= task['circle'] / self.current_frequency
                self.queue_time=max(0,self.queue_time)
                self.state = State.IDLE
                self.running_task = {'data_size': 0,
                             'delta_max': 0,
                             'circle': 0,
                             'user_index': 0,'user_distance':[1000,1000,1000],'req_freq_percent':0}
                self.current_frequency = self.min_frequency


if __name__ == '__main__':
    s = MECServer()
    print(s.get_state())
