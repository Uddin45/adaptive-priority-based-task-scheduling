import random
import threading
import time
import numpy as np
import math


class User:
    def __init__(self, user_cnt=1, evn_queue=None,evn_type=1, max_number_task_per_user=5):
        self.user_cnt = user_cnt
        self.evn_type=evn_type
        self.max_transmit_speed = 5500000
        self.max_frequency = 16 * 1e9
        self.max_number_task_per_user = max_number_task_per_user
        self.evn_queue = evn_queue
        self.max_number_task_list = 1e4
        self.send_task = threading.Thread(target=self.generate_send_task)
        self.send_task.start()

    def generate_send_task(self):
        tasks_number = self.max_number_task_per_user * self.user_cnt

        while True:
            task_list = []
            for n in range(tasks_number):
                u = n % self.user_cnt
                task = self.create_task(u)
                #if task and np.random.uniform(0, 1, 1)[0] > 0.2:
                    #task_list.append(task)
                task_list.append(task)
            #print("produced tasks:", len(task_list))
            if self.evn_queue.qsize() < self.max_number_task_list:
                # print("produced tasks:", task_list)
                task_list.reverse()
                self.evn_queue.put(task_list)
            time.sleep(np.random.random_sample()*0.01)

    def create_task(self, index):
        """
        implement the Task
        data_size: is the size of data in the task 20kB-300kB
        circle:required number of CPU circles 6*10^8 to 9*10^9
        delta_max: maximum tolerate time for the task 5s to 20s
        :return: only return tasks that possible finished on the MEC server

        It is not make sense to offloading task that might out of time during transmission; therefore we only keep
        tasks that possibly transmit to MEC servers to offloading.

        Note: A normal distribution of for the simulation may better

        """
        task = dict()
        # while True:
        task['data_size'] = random.randint(1 * math.pow(10, 4), 2 * math.pow(10, 4))
        task['circle'] = random.randint(8 * math.pow(10, 6), 10*math.pow(10, 6))
        #task['delta_max'] = random.randint(60, 90)
        task["user_index"] = index
        
       # task['priority']=random.randint(1,3) #if random.rand()<0.1 priority=3.
      #  if self.evn_type==1:
        #task['priority']=1+np.random.choice(3, p=[0.5,0.4,0.1])
        task['priority']=random.randint(1,3)
        
        mec_cnt=3
        p=random.randint(1,mec_cnt)
        dis=[0 for _ in range(mec_cnt)]

        if random.random()>=0.5:
            s = 1
        else:
            s = -1
        
        #print(p,s)
        R=300
        for i in range(mec_cnt):
            if p-1==i:
                #d=25
                d=random.uniform(0,150)
                dis[p-1]=math.sqrt(d**2+10**2)
        if s==1:
            for i in range(mec_cnt):
                if dis[i]==0 and i<=p-1:
                    dis[i]=math.sqrt(((p-1-i)*R+d)**2+10**2)
                if dis[i]==0 and i>p-1:
                    dis[i]=math.sqrt((((mec_cnt-p)-(mec_cnt-(i+1)))*R-d)**2+10**2)



        else:
            for i in range(mec_cnt):
                if dis[i]==0 and i>=p-1:
                    dis[i]=math.sqrt((((mec_cnt-p)-(mec_cnt-(i+1)))*R+d)**2+10**2)

                if dis[i]==0 and i<p-1:
                    dis[i]=math.sqrt(((p-1-i)*R-d)**2+10**2)

        
        
    

        task['user_distance']=dis
        #else: 
           # task['priority']=random.randint(1,3)
       # random
                #a=10*task['priority']
                #b=20*task['priority']
        if task['priority']==3:
           
            task['delta_max'] = random.randint(170,180)*0.001
        elif task['priority']==2:

            task['delta_max'] = random.randint(180,190)*0.001

        else :
            task['delta_max'] = random.randint(190,200)*0.001
        # return task
        #if (task['data_size'] / self.max_transmit_speed + task['circle'] / self.max_frequency) <= task['delta_max']*1.2:
            # print(self.index, ": has  task" )
        return task
        #else:
            #return None

#
# if __name__ == '__main__':
#     u = User()
