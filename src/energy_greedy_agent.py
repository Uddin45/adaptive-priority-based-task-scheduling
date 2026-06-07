import numpy as np


class GreedyAgent:
    def __init__(self, action_size=5):
        self.action_size = action_size

    def immediate_rewards(self, task, mec_evn):
        rewards = []
        task_done_status=[]
        
        frequency_vector=[]
        server_vector=[]
        Speed_Matrix=mec_evn.trans_speed_matrix
        #print(Speed_Matrix)
        for a in range(self.action_size):
            actions = mec_evn.actions[a]
            rec_mec_index = actions[0]
            re_freq = actions[1]
            task['req_freq_percent'] = re_freq
            
            trans_speed = Speed_Matrix[task['user_index']]['speed'][rec_mec_index]
            feedback = mec_evn.mec_servers[rec_mec_index].mec_reward(re_freq, task, trans_speed,2)
            rewards.append(feedback['energy'])
            task_done_status.append(feedback['task_done'])
            frequency_vector.append(re_freq)
            server_vector.append(rec_mec_index)
        return rewards,task_done_status,frequency_vector,server_vector

    def action(self, task, mec_evn):
        Rewards=[]
        Task_Done_Status=[]
        Server_Vector=[]
        Frequency_Vector=[]
        
    
        for tsk in task:
            
            rewards,task_done_status,frequency_vector,server_vector= self.immediate_rewards(tsk, mec_evn)
            Rewards.append(rewards)
            Task_Done_Status.append(task_done_status)
            Server_Vector.append(server_vector)
            Frequency_Vector.append(frequency_vector)
            
        max_reward=float('-inf')
        max_reward_idx=float('-inf')
        found_task_done_high_priority = False
        max_reward_server=float('-inf')
        max_reward_task=float('-inf')
        max_reward_frequency=float('-inf')
        
        for i in range(len(Rewards) - 1, -1, -1):  # Iterate through rows in reverse
            if 1 in Task_Done_Status[i]:
                task_done_indices = [idx for idx, val in enumerate(Task_Done_Status[i]) if val == 1]

                # Fetch rewards for these indices
                rewards_vector = [Rewards[i][idx] for idx in task_done_indices]
                max_reward = min(rewards_vector)
                max_reward_index = rewards_vector.index(max_reward)  # Index in the filtered list

                # Get the corresponding global action index
                action_index = task_done_indices[max_reward_index]  # Corrected to map to global actions

                max_reward_server = mec_evn.actions[action_index][0]  # Correctly accessing the global actions
                max_reward_task = i
                max_reward_frequency = mec_evn.actions[action_index][1]
               # max_reward_frequency = 0.55
                found_task_done_high_priority = True
                break
       
        if not found_task_done_high_priority:
            max_reward_vector=[]
            max_reward_idx_vector=[]
            for i in range(len(Rewards)):
                max_reward_vector.append(min(Rewards[i]))
                max_reward_idx_vector.append(Rewards[i].index(min(Rewards[i])))
           
                                             
            max_reward=min(max_reward_vector)
            max_reward_task=max_reward_vector.index(max_reward)
            action_index=Rewards[max_reward_task].index( max_reward)
            max_reward_server= mec_evn.actions[action_index][0]
            max_reward_frequency=mec_evn.actions[action_index][1]
           # max_reward_frequency = 0.55
        
                    
            
        # print(rewards)
        return max_reward_task,max_reward_server,max_reward_frequency


