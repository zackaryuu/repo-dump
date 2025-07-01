import subprocess
from zuu.STRUCT.DECOR.track_and_terminate import cleanup

@cleanup(
    windows=["notepad"]
)
def notepad_can_be_closed():
    subprocess.call(["start", "notepad"], shell=True)

notepad_can_be_closed()
