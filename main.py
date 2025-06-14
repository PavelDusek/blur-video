import rich
import time
import subprocess
import click
from pydantic import BaseModel

class Area(BaseModel):
    x: int
    y: int
    w: int
    h: int
    start: int
    end: int

def get_user_input(question: str) -> str:
    rich.print(question)
    answer = input(">>").strip().lower()
    return answer

@click.command()
@click.argument('videofile', type=click.Path(exists=True))
def main(videofile):

    #subprocess.Popen(["mplayer", videofile])
    areas = []
    rich.print("New area [blue](N)[/blue] or quit [red](Q)[/red]?")
    while ( (command := input(">>").lower().strip()) not in ["q", "quit"] ):
        print(command)
        if command.lower() in ["n", "new"]:
            delay = int(get_user_input("How long should be slurp delayed (in seconds)?"))
            rich.print("Move to window.")
            time.sleep(delay)
            cmd = "slurp"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # wait for the process to terminate
            out, err = process.communicate()
            errcode = process.returncode
            xy, wh = out.decode().strip().split(" ")
            x, y = xy.split(",")
            w, h = wh.split("x")
            x, y, w, h = int(x), int(y), int(w), int(h)

            start = int(get_user_input("When should the blur start (in seconds)?"))
            end = int(get_user_input("When should the blur end (in seconds)?"))
            area_dict = {'x': x, 'y': y, 'w': w, 'h': h, 'start': start, 'end': end}
            area = Area(**area_dict)
            print(area)
            areas.append(area)
            rich.print("New area [blue](N)[/blue] or quit [red](Q)[/red]?")

    print(areas)
    for i, area in enumerate(areas):
        print(f"[bl{i}]crop=w={area.w}:h={area.h}:x={area.x}:y={area.y}[blur{i+1}]; \\")

if __name__ == "__main__":
    main()
