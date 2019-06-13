import argparse
import time
import numpy as np
import collections
import torch
import torch.nn as nn
import torch.optim as optim
import gym
import roboschool

# returns a namedtuple with (state, action, reward...)
Experience = collections.namedtuple("Experience", field_names=['state', 'action', 'reward', 'done', 'new_state'])


class ExperienceBuffer:
    """
    Buffer of fixed capacity to handle previous experiences for bootstrap sampling.
    """
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)

    def __len__(self):
        return len(self.buffer)

    def append(self, experience):
        self.buffer.append(experience)

    # [self.buffer[idx] for idx in indices] is a list of [exp, exp,..., exp]
    # *[exp,exp,exp] returns then exp, exp, exp as arguments to a function
    # zip(exp, exp, exp) then rearranges the tuples such that new tuples are created
    # where the first elements of every exp tuple is in one tuple,
    # the second elements of every exp tuple are in one tuple etc

    # TODO standardize variable type declarations
    def sample(self, batch_size):
        """
        Sample random batch from past experiences.
        """
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        states, actions, rewards, dones, next_states = zip(*[self.buffer[idx] for idx in indices])
        return states, np.array(actions), np.array(rewards, dtype=np.float32), \
               np.array(dones, dtype=np.uint8), np.array(next_states)


class Agent:
    def __init__(self, env, exp_buffer):
        self.env = env
        self.exp_buffer = exp_buffer
        self._reset()

    def _reset(self):
        self.state = self.env.reset()
        self.total_reward = 0.0

    def play_step(self, net, epsilon=0.0, device="cpu"):
        """
        Epsilon greedy step. With probability epsilon, a random action is taken (exploration),
        else the action ist chosen to maximize the q-value as approximated by net (exploitation).
        """
        done_reward = None

        if np.random.random() < epsilon:
            action = self.env.action_space.sample()
        else:
            state_a = np.array([self.state], copy=False)
            state_v = torch.FloatTensor(state_a).to(device)
            q_vals_v = net(state_v)
            _, act_v = torch.max(q_vals_v, dim=1)
            action = int(act_v.item())

        # do step in the environment
        new_state, reward, is_done, _ = self.env.step(action)
        self.total_reward += reward

        exp = Experience(self.state, action, reward, is_done, new_state)
        self.exp_buffer.append(exp)
        self.state = new_state
        if is_done:
            done_reward = self.total_reward
            self._reset()
        return done_reward


# TODO implement double q learning
def calc_loss(batch, net, tgt_net, GAMMA, double=False, device="cpu"):
    """
    Calculate mean squared error as loss function.
    """
    states, actions, rewards, dones, next_states = batch

    states_v = torch.tensor(states, dtype=torch.float32).to(device)
    next_states_v = torch.tensor(next_states, dtype=torch.float32).to(device)
    actions_v = torch.tensor(actions).to(device)
    rewards_v = torch.tensor(rewards).to(device)
    done_mask = torch.ByteTensor(dones).to(device)

    state_action_values = net(states_v).gather(1, actions_v.unsqueeze(-1)).squeeze(-1)
    if double:
        next_state_actions = net(next_states_v).max(1)[1]
        next_state_values = tgt_net(next_states_v).gather(1, next_state_actions.unsqueeze(-1)).squeeze(-1)
    else:
        next_state_values = tgt_net(next_states_v).max(1)[0]
    next_state_values[done_mask] = 0.0  # final states have a future reward of 0
    next_state_values = next_state_values.detach()  # detach it from the current graph

    expected_state_action_values = next_state_values * GAMMA + rewards_v
    return nn.MSELoss()(state_action_values, expected_state_action_values)


# Work in progress. Want to create a buffer which sees every n steps as 1 step and appropriately discounts the rewards
# For off policy DQN, this speeds up training if n is kept small (<4)
# For larger n, on policy corrections are needed
class Nstep_ExperienceBuffer:
    # TODO finish n step TD method by buffer
    def __init__(self, n_steps):
        self.counter = 0
        self.buffer = 0
        self.subbuffer = 0
        pass

    def __len__(self):
        pass

    def append(self):
        counter += 1
        subbuffer.append()
        if counter == 4:
            buffer.append()

    def sample(self):
        pass


if __name__ == '__main__':
    pass

