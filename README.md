### Readme for myo hand washing project

#### Preparation for this project:
*- This project depends on **Python3**.*

---
+ Install VLC player:
    + MacOS users: Please install VLC library by **HomeBrew**, with command
        > brew cask install vlc
     
     + Windows users: Please download and install vlc(***x64 version***) from 
     [VideoLan](https://www.videolan.org/vlc/download-windows.html).
     
        Then set the environment path:
         
         > ***PYTHON_VLC_MODULE_PATH*** <br> to <br>***C:\Program Files\VideoLAN\VLC*** other installed directory.
+ Install python-vlc package, by:
    > pip/pip3 install python-vlc
    
    Please Note: <br> 
    > ***Not** pip3 install vlc* <br> It is different package
---
+ Install myo-python, by:
    > pip/pip3 install myo-python
    
    Please Note: <br>
    > ***Not** pip3 install myo* <br> It is different package
+ Modify myo-python Library:

    >please edit the myo-python library, at ***Event*** class in *myo._ffi.py*, by adding:
    
      @property
      def device_point(self):
        return libmyo.libmyo_event_get_myo(self._handle)
---       
+ Install PyQt5 Library:
    > pip/pip3 install PyQt5 
---
+ Users with PyCharm:
    
    Please turn off the ***"Show plots in tool window"*** at ***Setting > Tools > Python Scientific***
---
+ Users with MacOS in Mojave:
    
    Please create document of ***matplotlibrc*** at ***~/.matplotlib***, by adding:
        
        backend : Agg
    
    or, when using matplotlib,
        
        import matplotlib
        matplotlib.use('Agg')

#### To Run project / Collect data
*For Now, this project could be only functioned on Windows platform (Windows 10), 
because the matplotlib and PyQt5 libraries could not worked with multi-processes in MacOS platform.*

> To start with terminal: 

    python/python3 interface.py
 
> Using Pycharm:

    Run interface.py

The collected data will locate on:
> *myo/data*