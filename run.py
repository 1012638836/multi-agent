import os
import argparse

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
os.environ["OPENAI_API_BASE"] = "https://prod-az-ce-ai-openai07.openai.azure.com/"
os.environ["OPENAI_API_KEY"] = "3065b5b872084362b3785e210f973c51"
os.environ["Embed_Model"] = 'prod-az-ce-ai-openai07-text-embedding-ada-002'

from agents.SOP import SOP
from agents.Agent import Agent
from agents.config import software
from agents.LLM.base_LLM import LLM

def init(config):
    if not os.path.exists("logs"):
        os.mkdir("logs")
    sop = SOP.from_config(config)
    agents, roles_to_names, names_to_roles = Agent.from_config(config)
    print('agents: {}'.format(agents))
    sop.roles_to_names, sop.names_to_roles = roles_to_names, names_to_roles
    print('states: {}'.format(sop.states))
    # print('roles_to_names: {}'.format(roles_to_names))
    # print('names_to_roles: {}'.format(names_to_roles))

    return agents, sop


def run(agents, sop:SOP):
    while True:

        current_state, current_agent = sop.next(agents)

        if sop.finished:
            print("finished!")
            os.environ.clear()
            exit()

        current_role = current_agent.state_roles[current_state.name]
        print('更新完毕: current_state: {}, current_agent: {}({})'.format(current_state.name, current_agent.name, current_role))
        user_input = input('请输入任意内容以继续: ')

        action = current_agent.step(current_state)
        memory = action.process()
        current_state.update_memory(memory)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='A demo of chatbot')
    # parser.add_argument('--agent', default="F:/Datasets/agents-master/examples/Multi_Agent/software_company/config.json")
    # args = parser.parse_args()

    model = LLM(**software)
    software['model'] = model

    # ===================================
    agents, sop = init(software)
    # ===================================
    run(agents, sop)
