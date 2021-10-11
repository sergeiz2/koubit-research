# Using the AWRDE API 
This is a simple writeup of how to set up and use the AWR Design Environment (AWRDE) API to analyze circuits with Python.

## Description
The AWR Design Environment (AWRDE) contains a built-in Scripting Development Environment (SDE) based on the SAX Basic programming language. Scripting enables easy automation of tasks and facilitates data retrieval, which can help with data analysis and presentation. SAX Basic is compatible with Visual Basic for Applications (VBA). 

AWRDE has an extensive API, and with a little work, the commands available through VBA can also be accessed by Python, opening up the possibility of using the large body of open-source libraries and tools written for Python to retrieve and parse AWR specialized data data. The API also allows a used to programmatically alter values and inputs used in simulations, allowing a program to dynamically optimize these values in response to the data that it recieves from AWR.

## Getting Started

This process was tested with Windows 10 Home, AWRDE 15 and 16, and Python 3.8.10. Officially the requirements are as follows:

* **Python 3.7** or later
   * Python can be downloaded either from [Python Org](https://www.python.org/) or from from [Anaconda](https://www.anaconda.com/). If installing directly from Python Org, your Python install directory and the `/scripts` directory should both be added to your 'PATH' Environemental Variable in Windows.  
   
     **NOTE 1:** The Anaconda installation guide recommends against adding Anaconda Python to your `PATH`; instead the proper libraries can be installed in the conda environment in which your code will run, and the appropriate environment can be selected in your IDE or activated before executing your code. That said, Anaconda's installation was the only Python installation *I used* and so I added it to my `PATH` anyways.  
   
     **NOTE 2:** [pypiwin32]()is not available on conda channels. Initially, I installed the packages I could with the Conda package manager and the rest with PIP, but this is also generally recommended against, since PIP and Conda don't always play nice together, but again, it worked for me. See more detail below.

* **pip3** is included by default with the Python binary installers starting with Python 3.4. You may need to install it explicitly if you're not using a Conda environment, though it's also a requirement for installing **pywin32** (below) so if going the Conda environement route, Conda will install it for you.

### Installing [**pywin32**](https://pypi.org/project/pywin32/) 
This is a library which caused me some trouble. From the package description:  
   >  The Python for Win32 (pywin32) extension provides access to many of the Windows APIs from Python.
   >  ## Binaries 
   >  By far the easiest way to use pywin32 is to grab binaries from the [most recent release.](https://github.com/mhammond/pywin32/releases)
   >  ## Installing via PIP
   >  You can install pywin32 via pip: `pip install pywin32`.
   >  Note that if you want to use pywin32 for “system wide” features, such as registering COM objects or implementing Windows Services, then you must run the following command from an elevated command prompt:
   >  `python Scripts/pywin32_postinstall.py -install`.

The [guide published by AWR](https://kb.awr.com/display/awrscripts/AWR+Scripting+in+Python) instructs that [**pypiwin32**](https://pypi.org/project/pypiwin32/) should be installed with `pip`. It is not available on any Conda channels as far as I know. That said, **pypiwin32** is [apparently outdated:](https://stackoverflow.com/questions/55918311/what-is-the-difference-between-pywin32-and-pypiwin32)
  >   Pypiwin32 is an old and outdated repackaging of pywin32 from its creator to use wheels. It is abandoned for a long time. You should just use pywin32.

I was able to set up *just* pywin32 in my conda environment as follows.
* Open a terminal window and activate the conda environment with `conda activate <your_env_name>` (or if you don't have Anaconda in your 'PATH' open a anaconda terminal through the gui.)
* Install version 222 of pywin32 with `conda install pywin32==222`  
  Note that this is not the newest version of pywin32. For resasons that remain unclear to me, newer versions don't install properly.
* Open a command prompt with Administrator privileges.
* Again, activate your conda environment.
* Navigate to `<your_anaconda_environment_location>/Scripts`.
* Run `python pywin32_postinstall.py -install`.
* Return to your other terminal.
* Navigate to `<your_anaconda_environment_location>/Lib/site-packages/win32com/client`.
* Run `python makepy.py'.
* This will pull up a window that looks like this:  
  
  ![Select Library Popup](./SelectLibrary.png)
* Select the appropriate library and click "OK".
   
* **pyawr** is a library which incorporates win32com, the library which handles interfacing between the Python and Windows' [COM interface](https://en.wikipedia.org/wiki/Component_Object_Model) which allows different applications to "talk to" each other. 

### Installing

* How/where to download your program
* Any modifications needed to be made to files/folders

### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Sergei Zvenigorodsky

## References

## Acknowledgments
Readme template from [README-Template.md](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)
