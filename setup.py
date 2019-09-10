import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
from am_viewer.am_viewer import __version__


setuptools.setup(
     name='am_viewer',  
     version=__version__,
     author="James Cowdery",
     author_email="jtc@dolby.com",
     description="A PMD, serial ADM and AES-X242 audio metadata real-time viewer",
     long_description=long_description,
     long_description_content_type="text/markdown",
     scripts=['scripts/am_viewer'],
     entry_points={'console_scripts':'am_viewer=am_viewer.am_viewer:main'},
     packages=setuptools.find_packages(),
     python_requires='>=3',
     install_requires=['netifaces', 'zeroconf', 'scapy == 2.4.3'],
     include_package_data=True,
     package_data = {'adm': ['limits.txt'],
     				 'am_viewer': ['pmd_tool.Darwin','pmd_tool.Linux','pmd_tool.Windows.exe']
     				 },
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: Microsoft :: Windows",
         "Operating System :: POSIX :: Linux",
         "Operating System :: MacOS :: MacOS X"
     ],
 )