
software = {'environ_varibale': {'MAX_CHAT_HISTORY': '3'},

             # 模型参数
             'LLM_type': 'Local',
             'LLM': {
                 # 'OpenAI': {'model': 'gpt-3.5-turbo-16k-0613'},
                 'Local': {'model_path': "/llms-data/ljz/chatglm3-32k/ZhipuAI/chatglm3-6b-32k"}
            },
            'temperature': 0.5,

            # 不同 state 之间的递进关系
             'relations': {'design_state': {'0': 'design_state', '1': 'develop_state'},
                           'develop_state': {'0': 'develop_state', '1': 'debug_state'},
                           'debug_state': {'0': 'debug_state', '1': 'end_state'}},

            # 明确所有的 agents
             'agents': {'Alice': {'style': 'professional', 'roles': {'design_state': 'Leader1'}},
                        'Bob': {'style': 'professional', 'roles': {'design_state': 'Architect'}},
                        'Candy': {'style': 'professional', 'roles': {'develop_state': 'Leader2'}},
                        'Carl': {'style': 'professional', 'roles': {'develop_state': 'Developer', 'debug_state': 'Developer'}},
                        'David': {'style': 'professional', 'roles': {'debug_state': 'Debugger'}},
                        },

            # 初始 state
            'root': 'design_state',

            # 不同 states 的初始化参数
             'states': {'design_state': {'environment_prompt': "The current work objective: <target>a greedy snake game with python</target>. In this phase there are 2 roles: Leader1, Architect. The workflow of this phase is as follows: Step 1: Leader1 arranges the work to Architect according to the work objective. Step 2: Architect proposes the program framework according to the work objective and Leader1's requirements. Step 3: Leader1 evaluates the framework proposed by Architect and gives feedback suggestions. Repeat steps 2 and 3 until Leader1 believes that Architect's work has met all the requirements. At this point proceed to the next stage. ",
                                         'roles': ['Leader1', 'Architect'],
                                         'begin_role': 'Leader1',
                                         'begin_query': 'Please propose a detailed framework based on the work objective',
                                         'agent_states': {'Leader1': {'style': {'role': 'Leader1', 'style': 'professional'},
                                                                      'task': {'task': 'Evaluate the architecture proposal and provide effective feedback'},
                                                                      'rule': {'rule': "Please reply directly with 'Accepted'. Otherwise, please provide specific suggestions for improvement."},
                                                                      'demonstrations': {'demonstrations': "Review Architect's proposal meticulously and provide suggestions for improvement if you think the proposal is not perfect. Ensure the suggestions is specific and includes actionable suggestions for improvement. For instance, you can point out areas that need improvement and explain how suggested changes align with project goals."},
                                                                      'last': {'last_prompt':'You need to judge whether the objectives of the work under the current stage have been achieved based on the information provided above. If you think the objectives of the work under the current stage have been achieved, all you have to do is reply with one word: Accepted, otherwise give specific feedback.'}
                                                                      },
                                                          'Architect': {'style': {'role': 'Architect', 'style': 'professional'},
                                                                        'task': {'task': "Propose a Python framework based on the work objectives and Leader1's requirements."},
                                                                        'rule': {'rule': "Thoroughly analyze the project requirements, evaluate potential technologies, and select suitable design principles to meet the project's needs."},
                                                                        'demonstrations': {'demonstrations': "Create a detailed architect proposal document, including the rationale for choosing the proposed framework and accompanying design diagrams. For instance, provide an Architect diagram outlining the framework's high-level structure and a detailed explanation of why this architecture was selected."},
                                                                        'last': {'last_prompt': 'Output the framework only. The output strictly follows the following format:<architect>{content of framework}</architect>'}
                                                                        },
                                                          },
                                         'controller': {'decision_role': 'Leader1', 'decision_word': 'Accepted'},
                                         },

                        'develop_state': {'environment_prompt': "The current work objective: <target>a greedy snake game with python</target>. In this phase there are 2 roles: Leader2, Developer. The workflow of this phase is as follows: Step 1: Leader2 arranges Developer to develop the program based on the work objectives and the architecture provided in the previous phase; Step 2: Developer writes the code based on the work objectives and the architecture formulated in the previous phase as well as Leader2's requirements; Step 3: Leader2 evaluates the written code for elegance, readability and functionality and provides feedback. Repeat steps 2 and 3 until Leader2 thinks that Developer's work has met all the requirements. Then move on to the next stage.",
                                          'roles': ['Leader2', 'Developer'],
                                          'begin_role': 'Leader2',
                                          'begin_query': 'Please write code for the target game based on the framework provided.',
                                          'agent_states': {'Leader2': {'style': {'role': 'Leader2', 'style': 'professional'},
                                                                       'task': {'task': 'Evaluate the written code for elegance, readability, and functionality.'},
                                                                       'rule': {'rule': 'Provide constructive feedback that helps improve code quality and alignment with project goals.'},
                                                                       'demonstrations': {'demonstrations': 'Thoroughly review the code written by Developer1. Offer feedback on code organization, naming conventions, code efficiency, and any functional improvements needed. For instance, provide specific examples of code sections that require refinement and explain how these changes enhance code quality.'},
                                                                       'last': {'last_prompt':'You need to judge whether the objectives of the work under the current stage have been achieved based on the information provided above. If you think the objectives of the work under the current stage have been achieved, you only need to answer "Accepted", otherwise give specific feedback.'}
                                                                      },
                                                           'Developer': {'style': {'role': 'Developer', 'style': 'professional'},
                                                                         'task': {'task': 'write elegant, readable, extensible, and efficient code'},
                                                                         'rule': {'rule': '1.write code that conforms to standards like PEP8, is modular, easy to read, and maintainable. 2.Output the code only,Ensure that the code adheres to the Architect guidelines, coding standards, and best practices.3.The output strictly follows the following format:<title>{the file name}</title>\n<python>{the target code}</python>'},
                                                                         'demonstrations': {'demonstrations': 'Follow the Architect proposal closely while writing code. Document the code adequately, use meaningful variable names, and maintain proper code structure. For example, provide code snippets that demonstrate adherence to coding standards and Architect design.Output the code only.'},
                                                                         'last': {'last_prompt': 'The output strictly follows the following format:<title>{the file name}</title>\n<python>{the target code}</python>'}
                                                                         },
                                                           },
                                          'controller': {'decision_role': 'Leader2', 'decision_word': 'Accepted'},
                                          },

                        'debug_state': {'environment_prompt': "The current work objective: <target>a greedy snake game with python</target>. There are 2 roles in this stage: Debugger, Developer. The workflow of this phase is as follows: Step 1: Debugger simulates the compiler to run the code provided in the previous phase, determines whether the code runs properly, whether the run results meet the requirements, and provides feedback. Step 2: Developer modifies the code based on Debugger's feedback. Repeat steps 1 and 2 until Debugger believes that Developer's work has met all requirements. Then move on to the next stage.",
                                        'roles': ['Debugger', 'Developer'],
                                        'begin_role': 'Developer',
                                        'begin_query': 'Please make the code both runnable and more efficient.',
                                        'agent_states': {'Developer': {'style': {'role': 'Developer', 'style': 'professional'},
                                                                       'task': {'task': "write elegant, readable, extensible, and efficient code based on the debugger's feedback."},
                                                                       'rule': {'rule': "1.write code that conforms to standards like PEP8, is modular, easy to read, and maintainable.\n2.Address the issues identified by the Debugger and ensure that the code meets the project's requirements.\n3.The output strictly follows the following format:<title>{the file name}</title>\n<python>{the target code}</python>"},
                                                                       'demonstrations': {'demonstrations': 'Review the feedback provided by the Debugger and make the necessary modifications to the code. Document the changes made and ensure that the code is free of errors and warnings. Provide examples of code segments before and after the modifications.Output the code only.'},
                                                                       'last': {'last_prompt': 'The output strictly follows the following format:<title>{the file name}</title>\n<python>{the target code}</python>'},
                                                                         },
                                                         'Debugger': {'style': {'role': 'Debugger', 'style': 'professional'},
                                                                      'task': {'task': 'Simulate a compiler to determine whether the code is runnable and provide feedback.'},
                                                                      'rule': {'rule': 'Thoroughly test the code for syntax errors, logical issues, and other potential problems. Offer detailed feedback that helps the developer understand and resolve any issues.Please pay special attention to some logic bugs in the game, such as whether the game can run normally.'},
                                                                      'demonstrations': {'demonstrations': 'Run the code provided by developers through a simulated compiler or debugger. Document any errors, warnings, or issues encountered during the process. Provide feedback that includes specific examples of code problems and suggested solutions.'},
                                                                      'last': {'last_prompt':'You need to judge whether the objectives of the work under the current stage have been achieved based on the information provided above. If you think the objectives of the work under the current stage have been achieved, you only need to answer "Accepted", otherwise give specific feedback.'}
                                                                      },

                                                         },
                                        'controller': {'decision_role': 'Debugger', 'decision_word': 'Accepted'},
                                        },

                        'end_state': {'agent_states': {}},
                        }
             }





