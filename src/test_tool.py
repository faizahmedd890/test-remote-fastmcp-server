import sys
import os

sys.path.insert(
    0,
    r"C:\Users\faiza\OneDrive\Desktop\manim-mcp-server\src"
)

from manim_server import execute_manim_code


code = """
from manim import *

class TestScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait(1)
"""

print("Starting execute_manim_code...")
result = execute_manim_code(code)
print("Tool returned:")
print(result)