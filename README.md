# pySICM

<<<<<<< HEAD
pySICM is a software tool to control Scanning Ion Conductance Microscopes (SICMs). It's written in python.
The master branch is a puzzle of hardly usable code. Feel free to use it, but it's experimental.
=======
pySICM is a software tool to control scanning ion conductance microscopes.

Currently, it is a crowded, undocumented puzzle of code which requires some major rework. Feel free to use, but it is rather experimental.

pySICM uses pycomedi (https://github.com/wking/pycomedi) to access a DAQ board that controls the SICM, hence it requires pycomedi (which, in turn, reuqires comedi (http://www.comedi.org/)). Since comedi is only available for linux machines, pySICM is for linux only. 

This branch will be a complete rewrite of the code, aiming for a more clean and documented version. 

pySICM uses pycomedi (https://github.com/wking/pycomedi) to access a DAQ board that controls the SICM, hence it requires pycomedi (which, in turn, reuqires comedi (http://www.comedi.org/)). Since comedi is only available for linux machines, pySICM is for linux only. 


# Concept

- pySICM is a client-server application
- pySICM is modular
- pySICM consists of three major parts

For more information, see the readme files in the corresponding directories.
>>>>>>> 2e3317b4a39fac4a2dc25ab593e68a69a9123ed4
