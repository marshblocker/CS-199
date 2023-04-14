import os
import platform
import winsound


# Create a cross-platform function that notifies the user that the program is done
# by creating a sound. Do it for Windows, Linux, and Mac. Run it three times.
# Use a python stdlib to find the current OS.
def notify_user():
    # Windows
    if platform.system() == 'Windows':
        for _ in range(3):
            winsound.Beep(1000, 1000)
    # Linux
    elif platform.system() == 'Linux':
        for _ in range(3):
            os.system(
                'play --no-show-progress --null --channels 1 synth %s sine %f' % (1, 1000))
    # Mac
    elif platform.system() == 'Darwin':
        for _ in range(3):
            os.system('say "A task has been completed."')
    else:
        for _ in range(3):
            print('\a')

notify_user()