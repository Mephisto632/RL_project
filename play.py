import roboschool
import torch
from dqn_model import DQN
import wrappers
import time
import gym.wrappers


DEFAULT_ENV_NAME = "RoboschoolPong-v1"
MAKE_VIDEO = False  # Set true or false here to record video OR render, not both

env = gym.make(DEFAULT_ENV_NAME)
env = wrappers.action_space_discretizer(env, 3)
net = DQN(env.observation_space.shape[0], env.action_space.n)
# net.load_state_dict(torch.load("RoboschoolPong-v1-best_var_batch.dat"))
# net.load_state_dict(torch.load("RoboschoolPong-v1-best_night_training.dat"))
# net.load_state_dict(torch.load("RoboschoolPong-v1-best_n9_eps300k_batchvar_long_train.dat"))
net.load_state_dict(torch.load("RoboschoolPong-v1-best.dat"))
env.reset()
recorder = gym.wrappers.monitoring.video_recorder.VideoRecorder(env, "./recording.mp4", enabled=MAKE_VIDEO)

if not MAKE_VIDEO:
    env.render()

for i in range(2):
    obs = env.reset()
    while True:
        recorder.capture_frame()
        action = net(torch.tensor(obs, dtype=torch.float32)).max(0)[1]
        action = action.item()
        action = int(action)
        obs, reward, done, _ = env.step(action)
        if not MAKE_VIDEO:
            time.sleep(0.011)
        if done:
            break
recorder.close()
