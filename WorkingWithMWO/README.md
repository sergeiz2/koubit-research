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
   
     **NOTE 2:** [pypiwin32]()is not available on conda channels. Ininitally, I installed the packages I could with the conda package manager and the rest with pip, but this is also generally recommended against, since pip and conda don't always play nice together, but again, it worked for me. See more detail [below.]()

* **pip3** is included by default with the Python binary installers starting with Python 3.4. You'll need to install it in your conda environemnt if you choose to go that route.
* [**pywin32**](https://pypi.org/project/pywin32/) is a library which caused me some trouble. From the package description:  
   >  The Python for Win32 (pywin32) extension provides access to many of the Windows APIs from Python.
   >  ## Binaries 
   >  By far the easiest way to use pywin32 is to grab binaries from the [most recent release.](https://github.com/mhammond/pywin32/releases)
   >  ## Installing via PIP
   >  You can install pywin32 via pip: `pip install pywin32`.
   >  Note that if you want to use pywin32 for “system wide” features, such as registering COM objects or implementing Windows Services, then you must run the following command from an elevated command prompt:
   >  `python Scripts/pywin32_postinstall.py -install`.
  * 
  

* [pypiwin32**](
   
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
