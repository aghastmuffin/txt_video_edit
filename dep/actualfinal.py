import tkinter as tk #READS GEN.TXT
import difflib
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
def remove_section(video_path, start_time, end_time, output_path):
    video = VideoFileClip(video_path)
    clip1 = video.subclip(0, start_time)
    clip2 = video.subclip(end_time, video.duration)
    final_clip = concatenate_videoclips([clip1, clip2])
    final_clip.write_videofile(output_path, codec='libx264')


def open_file():
	with open("gen.txt", 'r') as file:
		content = file.read()
		text_widget.delete(1.0, tk.END) # Clear previous content
		text_widget.insert(tk.END, content)

st, et = 0, 0
def wv():
    st, et = 0, 0
    loops_count = 0
    all_loops_count = 0
    ran = False
    with open("gen.txt", 'r') as file:
        f = file.readlines()
    content = text_widget.get("1.0", tk.END).splitlines(True)
    diff = difflib.unified_diff(
        f,
        content,
        fromfile='gen.txt',
        tofile='text_widget',
    )
    #VERY SLOW, OPTIMIZE LATER
    diff = list(diff)
    for line in diff:
        all_loops_count += 1
        if line.startswith('-'):
            sline = line.replace("-", "").replace("\n", "").split(",")
            if len(sline) == 3:
                loops_count += 1
                if loops_count == 1:
                    print("cap")
                    st = sline[1]
                et = sline[2] #https://stackoverflow.com/questions/1630320/what-is-the-pythonic-way-to-detect-the-last-element-in-a-for-loop
                print(sline)
        else:
            if all_loops_count > 5 and loops_count > 0:
                print("done")
                print(st, et) #RETURN DATA FROM HERE
                remove_section("pvideo.mp4", float(st), float(et), "output.mp4")
                break
            

# Create the main window
root = tk.Tk()
root.title("Text Based Video Editor (NON PRODUCTION)")

# Create a Text widget to display the content
text_widget = tk.Text(root, wrap="word", width=40, height=10)
text_widget.pack(pady=10)
text_widget.insert(tk.END, "init")
open_file()
sc = tk.Button(root, text="Write to Video", command=wv)
# Run the Tkinter event loop
sc.pack()
root.mainloop()
