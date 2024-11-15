from .Component import *
from .Memory import Memory
# from .Component.PromptComponent import *

class State:
    """
    Sub-scenes of role activities, responsible for storing the tasks that each role needs to do
    """
    def __init__(self, **kwargs):
        self.next_states = {}
        self.name = kwargs["name"]
        self.environment_prompt = (kwargs["environment_prompt"] if "environment_prompt" in kwargs else "")

        self.roles = kwargs["roles"] if "roles" in kwargs else (list(kwargs["agent_states"].keys()) if "agent_states" in kwargs else [0])
        if len(self.roles) == 0: self.roles = [0]

        self.begin_role = (kwargs["begin_role"] if "begin_role" in kwargs else self.roles[0])
        self.begin_query = kwargs["begin_query"] if "begin_query" in kwargs else None
        self.is_begin = True

        self.current_role = self.begin_role
        self.components = self.init_components(kwargs["agent_states"]) if "agent_states" in kwargs else {}
        # print('components: {}'.format(self.components))

        self.index = (self.roles.index(self.begin_role) if self.begin_role in self.roles else 0)  # 当前状态对应的 role
        self.chat_history = []  # 当前状态环境信息
        self.chat_nums = 0  # 当前状态包含的对话数

    def init_components(self, agent_states_dict: dict):
        agent_states = {}
        for role, components in agent_states_dict.items():
            component_dict = {}
            for component, component_args in components.items():
                if component:

                    if component == "style":
                        component_dict["style"] = StyleComponent(component_args["role"])

                    elif component == "task":
                        component_dict["task"] = TaskComponent(component_args["task"])

                    elif component == "rule":
                        component_dict["rule"] = RuleComponent(component_args["rule"])

                    elif component == "demonstrations":
                        component_dict["demonstrations"] = DemonstrationComponent(component_args["demonstrations"])

                    elif component == "output":
                        component_dict["output"] = OutputComponent(component_args["output"])

                    elif component == "last":
                        component_dict["last"] = LastComponent(component_args["last_prompt"])

                    elif component == "cot":
                        component_dict["cot"] = CoTComponent(component_args["demonstrations"])

                    elif component == "CustomizeComponent":
                        component_dict["CustomizeComponent"] = CustomizeComponent(component_args["template"],
                                                                                  component_args["keywords"])
                    
                    elif component == "system" : 
                        component_dict["system"] = SystemComponent(component_args["system_prompt"])

                    # =================================================================================#
                    elif component == "StaticComponent":
                        component_dict["StaticComponent"] = StaticComponent(component_args["output"])

                    # "top_k"  "type" "knowledge_base" "system_prompt" "last_prompt"
                    elif component == "KnowledgeBaseComponent":
                        component_dict["tool"] = KnowledgeBaseComponent(
                            component_args["top_k"],
                            component_args["type"],
                            component_args["knowledge_path"])
                        # print('kb_questions: {}'.format(component_dict["tool"].kb_questions))
                        # print('kb_answers: {}'.format(component_dict["tool"].kb_answers))
                        # print('kb_chunks: {}'.format(component_dict["tool"].kb_chunks))
                        # print(component_dict["tool"].kb_embeddings.shape)
                        # exit()

                    elif component == "CategoryRequirementsComponent":
                        component_dict["CategoryRequirementsComponent"] = CategoryRequirementsComponent(
                            component_args["information_path"])

                    elif component == "FunctionComponent":
                        component_dict["FunctionComponent"] = FunctionComponent(component_args[""])

                    # "short_memory_extract_words"  "long_memory_extract_words" "system_prompt" "last_prompt"
                    elif component == "ExtractComponent":
                        component_dict["ExtractComponent"] = ExtractComponent(
                            component_args["extract_words"],
                            component_args["system_prompt"],
                            component_args["last_prompt"])

                    elif component == "WebSearchComponent":
                        component_dict["WebSearchComponent"] = WebSearchComponent(component_args["engine_name"],
                                                                                  component_args["api"])
                    elif component == "FlightComponent":
                        component_dict["FlightComponent"] = FlightComponent(component_args["api"], component_args["secret"])

                    elif component == "WebCrawlComponent":
                        component_dict["WebCrawlComponent"] = WebCrawlComponent(component_args["name"])

                    elif component == "CodeComponent":
                        component_dict["CodeComponent"] = CodeComponent(component_args["file_name"], component_args["keyword"])

                    else:
                        continue

            agent_states[role] = component_dict

        return agent_states


    def update_memory(self, memory:Memory):
        self.chat_history.append(memory)


