from ..Memory import Memory
from ..utils import extract
import os, datetime
class Action:
    """
    The basic action unit of agent
    """
    def __init__(self,**kwargs):
        self.response = None
        self.is_user = False
        self.name = ""
        self.role = ""
        for key, value in kwargs.items(): setattr(self, key, value)
    
    def process(self):
        """
        processing action
        Rerutn : memory(Memory)
        """
        response = self.response
        send_name = self.name
        send_role = self.role
        all = ""
        for res in response:
            all += res
        parse = f"{send_name}:"
        # print('all: {}'.format(all))
        
        # 将里面对话的第三人称删了
        while parse in all:
            index = all.index(parse) + len(parse)
            all = all[index:]
        
        if not self.is_user: print(f"{send_name}({send_role}):{all}")

        # 根据限定的程序格式: <title>{the file name}</title>\n<python>{the target code}</python>', 先提取保存的文件名the file name, 然后提取 python 程序并保存到本地
        if "<title>" in all:
            title = extract(all, "title")
            title = "CoT.py" if title == "" else title
            python = extract(all, "python")
            os.makedirs("output_code", exist_ok=True)
            file_name = "output_code/" + send_name + '_' + title[:-3] + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".py"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(python)

        memory = Memory(send_role, send_name, all)
        return memory
    
    
