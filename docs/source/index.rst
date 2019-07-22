.. UrbanSim Templates documentation master file, created by
   sphinx-quickstart on Fri Jan  4 15:26:06 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

UrbanSim Templates
==================

UrbanSim Templates provides building blocks for Orca-based simulation models. It's part of the `Urban Data Science Toolkit <http://docs.udst.org>`__ (UDST).

The library contains templates for common types of model steps, plus a tool called ModelManager that runs as an extension to the `Orca <https://udst.github.io/orca>`__ task orchestrator. ModelManager can register template-based model steps with the orchestrator, save them to disk, and automatically reload them for future sessions.

v0.2.dev7, released July 22, 2019


Contents
--------

.. toctree::
   :maxdepth: 2
   
   getting-started
   modelmanager
   model-steps
   data-templates
   utilities
   development
