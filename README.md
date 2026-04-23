# COMP116 Resources

Course lectures and helper files for generating knitting patterns for course final projects and tutorials.

## Environment Setup

### Setup Miniconda

Miniconda is a minimal version of Anaconda, a package distribution platform for Python. It provides access to `conda`, which is an environment managing tool in the command line (note: command line, or terminal, refers to a place where you can enter commands and do things on your computer directly without going through the frontend user interface, like dragging and dropping files into folders, creating folders, renaming things, and many more).

Here's a [tutorial](https://www.anaconda.com/docs/getting-started/miniconda/install); choose the instructions suitable for your operating system and follow through. This step is completed if you can enter `conda` in your command line and it runs.

### Download VSCode

If you do not yet have a favorite code editor, please download VSCode from [here](https://code.visualstudio.com/download).

### Creating a Python environment

In your command line, run the following:

```
conda create -n py314 -c conda-forge python=3.14
conda activate py314
python -m pip install numpy matplotlib jupyter
```

Before you run the programs or notebooks, always activate the environment `py314`.

## Usage

To run the `knitting_helper.py` or `shaping_helper.py` under `knitout_utils/`, please activate the environment first. The environment being setup to be python=3.14 is important because the compiled python bytecode of `knitout_writer.pyc` is in version 3.14.

## Acknowledgement

This course is developed by the instructor, largely based on publicly available resources as listed under the course [Resources](https://ymei.wescreates.wesleyan.edu/teaching/comp116-sp26/resources/#additional-sites) page and prior computational machine knitting research literature. The instructor especially wants to acknowledge help and materials from Yue Xu (for discussing doubleknit jacquard options for HW4), Jenny Lin (guest lecture on machine knitting for CSE556 at UW), Megan Hofmann (slides from CSE 599 special topics course taught at UW), and the CMU Textiles Lab (everything from open source repositories, research, blog posts, to the entire infrastructure that this course and a lot of machine knitting research build upon). Claude assisted the instructor in course material development and logistics planning.
