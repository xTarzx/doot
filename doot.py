#!/usr/bin/env python3

import os
import curses
from typing import TYPE_CHECKING
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any


@dataclass_json
@dataclass
class Todo:
    text: str
    done: bool = False


filepath = os.path.join(os.path.dirname(__file__), "doots")


def load_todos() -> list[Todo]:
    try:
        with open(filepath, "r") as f:
            todos = json.load(f)
        return [Todo.from_dict(todo) for todo in todos]
    except FileNotFoundError:
        return []


def save_todos(todos: list[Todo]):
    saveable = [todo.to_dict() for todo in todos]
    with open(filepath, "w") as f:
        json.dump(saveable, f)


def main(stdscr: Window):
    todos = load_todos()
    selected = 0

    stdscr.clear()

    while True:
        stdscr.erase()
        for y, todo in enumerate(todos):
            stdscr.move(y, 0)
            stdscr.addstr(f"[{'■' if todo.done else ' '}]{todo.text}")
        if selected > len(todos)-1 and len(todos):
            selected = len(todos)-1

        stdscr.move(selected, 1)

        stdscr.refresh()

        c = stdscr.getch()
        if c == ord("q"):
            break
        elif c == curses.KEY_DOWN:
            if len(todos):
                selected = (selected + 1) % len(todos)
        elif c == curses.KEY_UP:
            if len(todos):
                selected = (selected - 1) % len(todos)
        elif c == ord(" "):
            if len(todos):
                todos[selected].done = not todos[selected].done
                save_todos(todos)
        elif c == ord("a"):
            stdscr.addstr(len(todos)+2, 0,
                          "enter to confirm. esc to cancel")
            stdscr.addstr(len(todos)+1, 0,
                          "add todo > ")

            addtodo = False
            le_text = ""
            while True:
                c = stdscr.getch()
                if c == 27:  # esc key
                    break
                elif c == 10:  # enter key
                    addtodo = True
                    break
                elif c == 127:  # backspace
                    if le_text:
                        le_text = le_text[:-1]
                        y, x = stdscr.getyx()
                        stdscr.move(y, x-1)
                        stdscr.delch()
                else:
                    stdscr.addstr(chr(c))
                    le_text += chr(c)

            if addtodo and le_text:
                todos.append(Todo(le_text))
                save_todos(todos)

        elif c == ord("d"):
            if len(todos):
                stdscr.addstr(len(todos)+1, 0, "press again to confirm")
                stdscr.move(selected, 1)
                if stdscr.getch() == ord("d"):
                    todos.pop(selected)
            save_todos(todos)


if __name__ == "__main__":
    os.environ.setdefault('ESCDELAY', '25')
    curses.wrapper(main)
