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

    outfile = videofile.replace(".mp4", "_blurred.mp4")
    ffmpeg = f"ffmpeg -i {videofile} -filter_complex \"\\\n"
    ffmpeg += "[0:v]boxblur=luma_radius=10:luma_power=1,split="
    #subprocess.Popen(["mplayer", videofile])

    areas = []
    rich.print("New area [blue](N)[/blue] or quit [red](Q)[/red]?")
    while ( (command := input(">>").lower().strip()) not in ["q", "quit"] ):
        print(command)
        if command.lower() in ["n", "new"]:
            cmd = "slurp"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # wait for the process to terminate
            out, err = process.communicate()
            errcode = process.returncode
            out = out.decode().strip()
            err = err.decode().strip()
            if err == "selection cancelled":
                rich.print("[red]Selection cancelled!!![/red]?")
                rich.print("New area [blue](N)[/blue] or quit [red](Q)[/red]?")
                continue
            xy, wh = out.split(" ")
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
    area_count = len(areas)
    split_text, crop_text, overlay_text = "", "", ""
    for i, area in enumerate(areas):
        split_text += f"[bl{i+1}]"
        crop_text += f"[bl{i+1}]crop=w={area.w}:h={area.h}:x={area.x}:y={area.y}[blur{i+1}]; \\\n"
        if i == 0:
            overlay_text += f"[0:v][blur{i+1}]overlay={area.x}:{area.y}:enable='between(t,{area.start},{area.end})'[v{i+1}]; \\\n"
        else:
            overlay_text += f"[v{i}][blur{i+1}]overlay={area.x}:{area.y}:enable='between(t,{area.start},{area.end})'[v{i+1}]; \\\n"

    ffmpeg += f"{area_count}{split_text}; \\\n"
    ffmpeg += crop_text
    ffmpeg += overlay_text
    ffmpeg += f"[v{area_count}]format=yuv420p[out]\" \\\n"
    ffmpeg += f"-map \"[out]\" -c:v libx264 -preset veryfast -crf 23 -an {outfile}" 
    print(ffmpeg)
if __name__ == "__main__":
    main()
