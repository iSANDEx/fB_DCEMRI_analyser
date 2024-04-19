import os
import sys
import numpy as np

def list_folder_content(path, show_hidden=False):
    if show_hidden:
        ddfldrlst = os.listdir(path)
    else:
        ddfldrlst = list(filter(lambda item: not item.startswith('.'),os.listdir(path)))
    return ddfldrlst

def getenv(colab=False):
    """
    Requires sys and os modules:
    import sys
    import os
    Update 03/04/2024: Added support when running inside Google Colab Environment, via the optional flag "colab"
    """
    if colab:
      # Requires mounting the Google Drive before
      HOMEPATH = '/content/drive/MyDrive'
    else:
      if sys.platform == 'win32':
          env_home = 'HOMEPATH'
      elif (sys.platform == 'darwin') | (sys.platform == 'linux'):
          env_home = 'HOME'
      HOMEPATH = os.getenv(env_home)

    return HOMEPATH

HOMEPATH = getenv()
ROOTPATH = os.path.join(HOMEPATH, 'Data', 'ISPY2')

DCMFLDR = os.path.join(ROOTPATH, 'StudyData')

# Folders:
datalist = list_folder_content(DCMFLDR)
ndata = 3

selected_list = np.random.choice(datalist, ndata)
print(selected_list)