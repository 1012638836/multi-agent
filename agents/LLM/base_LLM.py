from transformers import AutoTokenizer, AutoModel
import os
from openai import OpenAI

class LLM(object):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.llm_type = kwargs['LLM_type']
        self.model_name = kwargs['LLM']['OpenAI']['model'] if kwargs['LLM_type'] == 'OpenAI' else None
        self.temperature = kwargs["temperature"] if "temperature" in kwargs else 0.8
        self.model = self.init_model(**kwargs)
        self.past_key_values = None

    def init_model(self, **kwargs):
        if kwargs['LLM_type'] == 'OpenAI':
            model = OpenAI()

        elif kwargs['LLM_type'] == 'Local':
            model_path = kwargs['LLM']['Local']['model_path']
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            model = AutoModel.from_pretrained(model_path, trust_remote_code=True, device_map='auto').half()
            model.eval()
        else:
            model = None
        return model

    def get_response(self, chat_history, system_prompt, last_prompt=None):
        messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        messages += chat_history  # chat_history = ["role": "user", "content": agent 从环境中观察到的信息]

        if last_prompt: messages[-1]["content"] += '\n' + last_prompt

        print('LLM imputs: {}'.format(messages))
        if self.llm_type == 'OpenAI':
            completion = self.model.chat.completions.create(model=self.model_name,
                                                            messages=messages,
                                                            temperature=self.temperature,
                                                            )
            response = completion.choices[0].message.content
            return response
        elif self.llm_type == 'Local':
            response, history = self.model.chat(self.tokenizer, messages[-1]["content"], messages[:-1])

            return response
        else:
            return None
    
if __name__ == '__main__':
    print(os.environ["OPENAI_API_KEY"])

