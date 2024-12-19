from collections import deque
from typing import Any, Deque, Dict


class Memory:

    def __init__(self, name: str):
        self.name = name
        self.memory: Dict[str, Any] = {}

    def has_key(self, name: str):
        return name in self.memory

    def get(self, name: str):
        return self.memory[name]

    def put(self, name: str, value: Any):
        self.memory[name] = value


class MemoryStack:
                                                                             
    def __init__(self, memory=None): # initialize memory stack with memory <memory>
        self.stack: Deque[Memory] = deque()
        if memory:
            self.stack.appendleft(Memory(name=memory))

    def get(self, name):             # gets from memory stack current value of variable <name>
        for memory in self.stack:
            if memory.has_key(name):
                return memory.get(name)

    def insert(self, name: str, value: Any): # inserts into memory stack variable <name> with value <value>
        self.stack[0].put(name, value)

    def set(self, name: str, value: Any): # sets variable <name> to value <value>
        for memory in self.stack:
            if memory.has_key(name):
                memory.put(name, value)
                return

        self.insert(name, value)

    def push(self, memory: str): # pushes memory <memory> onto the stack
        self.stack.appendleft(Memory(name=memory))

    def pop(self):          # pops the top memory from the stack
        self.stack.popleft()


