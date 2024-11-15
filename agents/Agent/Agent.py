# coding=utf-8
"""LLM autonoumous agent"""
from ..Component import *
from ..Action import Action
from ..Memory import Memory
import json

class Agent:
    """
    Auto agent, input the JSON of SOP.
    """

    def __init__(self, name, agent_state_roles, **kwargs) -> None:
        self.state_roles = agent_state_roles
        self.name = name
        self.style = kwargs["style"]
        self.LLMs = kwargs["LLMs"]
        self.LLM = None
        self.begins = kwargs["begins"] if "begins" in kwargs else False
        self.current_role = ""
        self.current_state = None

    @classmethod
    def from_config(cls, config_file):
        """
        Initialize agents based on json file
        Return:
        agents(dict) : key:agent_name;value:class(Agent-ReAct)
        names_to_roles(dict) : key:state_name  value:(dict; (key:agent_name ; value:agent_role))
        roles_to_names(dict) : key:state_name  value:(dict; (key:agent_role ; value:agent_name))
        """
        if isinstance(config_file, str):
            with open(config_file, encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = config_file
        
        roles_to_names = {}
        names_to_roles = {}
        agents = {}

        for agent_name, agent_dict in config["agents"].items():
            agent_state_roles = {}
            agent_LLMs = {}
            agent_begins = {}
            for state_name, agent_role in agent_dict["roles"].items():
                agent_state_roles[state_name] = agent_role
                
                if state_name not in roles_to_names: roles_to_names[state_name] = {}
                if state_name not in names_to_roles: names_to_roles[state_name] = {}
                roles_to_names[state_name][agent_role] = agent_name
                names_to_roles[state_name][agent_name] = agent_role

                current_state = config["states"][state_name]
                current_state["roles"] = list(current_state["agent_states"].keys()) if "roles" not in current_state else current_state["roles"]
                current_state_begin_role = current_state["begin_role"] if "begin_role" in current_state else current_state["roles"][0]

                agent_begins[state_name] = {}
                agent_begins[state_name]["is_begin"] = current_state_begin_role == agent_role if "begin_role" in current_state else False
                agent_begins[state_name]["begin_query"] = current_state["begin_query"] if "begin_query" in current_state else " "

                if "LLM_type" not in current_state["agent_states"][agent_role]:
                    current_state["agent_states"][agent_role]["LLM_type"] = config["LLM_type"]
                if "LLM" not in current_state["agent_states"][agent_role]:
                    current_state["agent_states"][agent_role]["LLM"] = config["LLM"]
                agent_LLMs[state_name] = config['model']

            # print('agent_state_roles: {}'.format(agent_state_roles))
            agents[agent_name] = cls(
                agent_name,
                agent_state_roles,
                LLMs=agent_LLMs,
                style=agent_dict["style"],
                begins=agent_begins
            )

        return agents, roles_to_names, names_to_roles

    def step(self, current_state):
        """
        根据 current_state 与 environment 采取行动
        """
        print('{} 根据 current_state, 先观察环境然后再采取行动...'.format(self.state_roles[current_state.name]))

        current_state.chat_nums += 1
        state_begin = current_state.is_begin
        agent_begin = self.begins[current_state.name]["is_begin"]
        self.begins[current_state.name]["is_begin"] = False
        current_state.is_begin = False
        self.current_state = current_state

        current_history = self.observe() if len(self.current_state.chat_history) > 0 else []
        print('从当前阶段的环境中观察信息, 得到: {}'.format(current_history))
        # current_history = json.dumps(current_history, ensure_ascii=False)

        print('采取行动...')
        if agent_begin:
            response = self.begins[current_state.name]["begin_query"]
        else:
            response = self.act(current_history)

        action_dict = {
            "response": response,

            "name": self.name,
            "role": self.state_roles[current_state.name],
            "state_begin": state_begin,
            "agent_begin": agent_begin,
        }
        print('行动结果为: ', end='')
        return Action(**action_dict)

    def observe(self):
        """ Update one's own memory according to the current environment """
        chat_history = Memory.get_chat_history(self.current_state.chat_history)
        chat_history = json.dumps(chat_history, ensure_ascii=False)
        chat_history = f"""Here is the chat history for the current phase: {chat_history}"""
        return [{"role": "user", "content": chat_history}]

    def act(self, current_history):
        """
        return actions by the current state
        """
        current_state = self.current_state
        current_LLM = self.LLMs[current_state.name]

        # system_prompt: environment_prompt + role + name + style + task + rule + demonstrations
        system_prompt, last_prompt = self.get_prompts()
        # print('当前 agent 的system_prompt: {}'.format(system_prompt))
        # print('当前 agent 的last_prompt: {}'.format(last_prompt))
        # print('采取行动: 将当前 agent 的长期记忆 system_prompt 和 last_prompt 送入 LLM.', end=' ')

        response = current_LLM.get_response(current_history, system_prompt, last_prompt)
        return response

    def get_prompts(self):
        """
        从 current state 中获取提示信息
        """
        current_state = self.current_state
        # self.current_roles = self.state_roles[current_state.name]
        self.LLM = self.LLMs[current_state.name]
        components = current_state.components[self.state_roles[current_state.name]]

        system_prompt = self.current_state.environment_prompt
        last_prompt = ""

        for component in components.values():
            if isinstance(component, (OutputComponent, LastComponent)):
                last_prompt = last_prompt + component.get_prompt(self) + "\n"
            elif isinstance(component, PromptComponent):
                system_prompt = system_prompt + "\n" + component.get_prompt(self)
        return system_prompt, last_prompt


