from mec_environment import MECEnvironment
from random_agent import RandomAgent

mec_evn = MECEnvironment(user_cnt=5, mec_cnt=5)
agent = RandomAgent(mec_cnt=mec_evn.mec_cnt)


cnt = 0
for ep in range(2):
    mec_evn.reset()
    acc_reward = 0
    while True:
        task = mec_evn.tasks_queue.get()
        if task:
            action = agent.action()
            # print("action=", action)
            # print("state=", mec_evn.get_state(task))
            mec_evn.get_state(task)
            r, done = mec_evn.step(action, task)
            acc_reward += r

            if done:
                cnt += 1
                print("=====================epoch=", cnt)
                print("reward=", r)
                print("total_reward =", acc_reward)
                break




