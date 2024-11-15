# coding=utf-8

import random
from .State import State
import json
import os

class SOP(object):

    def __init__(self, **kwargs):

        # 初始化不同状态
        self.states = {}
        self.init_states(kwargs["states"])

        # 设置不同状态之间的关系
        self.init_relation(kwargs["relations"])

        # 设置不同状态的决策者
        self.controller_dict = {}
        for state_name, states_dict in kwargs["states"].items():
            if state_name != "end_state" and "controller" in states_dict:
                self.controller_dict[state_name] = states_dict["controller"]

        self.root = self.states[kwargs["root"]]
        self.current_state = self.root
        self.finish_state_name = kwargs["finish_state_name"] if "finish_state_name" in kwargs else "end_state"
        self.roles_to_names = None
        self.names_to_roles = None
        self.finished = False

    @classmethod
    def from_config(cls, config_file):
        if isinstance(config_file, str):
            with open(config_file, encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = config_file

        os.environ.clear()
        for key, value in config["environ_varibale"].items(): os.environ[key] = value
        sop = SOP(**config)

        return sop

    def init_states(self, states_dict):
        for state_name, state_dict in states_dict.items():
            state_dict["name"] = state_name
            # print(state_name, state_dict)
            self.states[state_name] = State(**state_dict)

    def init_relation(self, relations):
        for state_name, state_relation in relations.items():
            for idx, next_state_name in state_relation.items():
                self.states[state_name].next_states[idx] = self.states[next_state_name]
                # print(self.states)

    def next(self, agents):
        """ 基于当前的 agents 确定下一个 state 和 agent """
        print('更新 next state 与 next agent')

        # 刚进入 state
        if self.current_state.is_begin and self.current_state.begin_query:
            agent_name = self.roles_to_names[self.current_state.name][self.current_state.begin_role]
            agent = agents[agent_name]
            return self.current_state, agent


        # 如果当前 role 就是 decision_role, 则根据其最新回应, 判断当前状态的工作目标是否以顺利完成，以进入下一个阶段
        next_state = self.current_state
        current_role = self.current_state.roles[self.current_state.index]
        controller = self.controller_dict[self.current_state.name]
        if controller['decision_role'] == current_role and len(self.current_state.chat_history) > 0:

            latest_response = self.current_state.chat_history[-1].content
            if controller['decision_word'] in latest_response[: len(controller['decision_word']) + 3] or self.current_state.chat_nums >= 6:
                next_state = self.current_state.next_states['1']

                # 如果下一个状态是结束, 则终止
                if next_state.name == self.finish_state_name:
                    self.finished = True
                    return None, None
                else:
                    # 将当前状态得到的结果传递给下一个状态
                    last_state_achievement = self.current_state.chat_history[-2].content
                    next_environment_prompt = next_state.environment_prompt
                    next_state.environment_prompt = f'{next_environment_prompt}\nHere is the information provided by the previous state:\n{last_state_achievement}'

                    self.current_state = next_state
                    agent_name = self.roles_to_names[self.current_state.name][self.current_state.begin_role]
                    agent = agents[agent_name]
                    return self.current_state, agent

        # 仍然停留在当前状态，寻找 next agent
        if next_state.name == self.current_state.name:
            self.current_state.index = (self.current_state.index + 1) % len(self.current_state.roles)
            next_role = self.current_state.roles[self.current_state.index]
            self.current_state.current_role = next_role
            agent = agents[self.roles_to_names[self.current_state.name][next_role]]
            return self.current_state, agent
