from typing import Dict, Type

from src.gpt.gpt_comand import GptCliCommand, CommandException, ListFiles, DeleteFile


class GptCli:
    cmds: Dict[str, Type[GptCliCommand]]

    def __init__(self):
        self.cmds = {
            "fls": ListFiles,
            "fd": DeleteFile
        }

    def run(self):
        done = False
        while not done:
            cmd_str = input("Enter the command:\n")
            try:
                cmd = self.parse_cmd(cmd_str)
                output = cmd.execute()
                print(f"Output:\n{output}\n")
            except CommandException as e:
                print(f"Command failed:\n{e}\n")

    def parse_cmd(self, cmd_str: str) -> GptCliCommand:
        cmd_args = cmd_str.split(" ")
        cmd_word = cmd_args[0]
        cmd_args = cmd_args[1:]

        if cmd_word not in self.cmds:
            raise CommandException(f"Unknown command: {cmd_word}")

        cmd = self.cmds[cmd_word](*cmd_args)
        return cmd


def main():
    cli = GptCli()
    cli.run()


if __name__ == '__main__':
    main()
