# Reseqr

Reseqr is a software tool developed for the Harvard Botany Libraries to rename batched image files processed by the University Libraries' Imaging Services.  This operation validates the METS files with respect to their correlation to the image files on disk and corrects the sequence number in file names as specified in METS files associated with each batch.

The specifics of a given project have been localized in a configuration file, so this tool may be adapted for other units with similar needs.  

Reseqr is written in Python3 (v.3.4) and can be run on Windows, OSX, and Linux machines.  The PyYAML library must be installed additionally.

## Functionality

   - operates on a single batch per program execution
   - validates image file batch for expected naming conventions
   - validates batch METS files for expected conventions
   - validates correlation between image files and METS descriptors
   - reports validation results to screen and file
   - reports intended file renaming as a Python script that can be run separately
   - renames all image files with an additional prefix to avoid collision, even when no sequence number change is required
   - marks batches to avoid double execution
   - reports on renaming results
   - uses an editable configuration file with each project's constant data
   - allows for concurrent projects


## Project Setup
   - Image file batches for a given project are located in a single directory specified in the config 
   - Each batch is assumed to contain one or more subdirectories that contain the image files
   - METS files are located in the batch subdirectory called 'mets'
   - METS files are in a one-to-one correspondence with the image file subdirectories but are not named so as to determine the pairing.  This is determined by the program reading the METS files.
   - The batch processing report is written to the batch directory.
   - The generated renaming script for a batch covers all the image files in all the subdirectories and is written to the batch directory.

## Usage

Reseqr is run from the command line using the Python 3 interpreter or in the Python 3 shell.
The python command can be either "python" as on Windows or "python3" on other operating systems.

`python reseqr.py -h -s -c <config> -p <project name> -b <batch name>`

where the options indicate:
   -       -h            help
   -       -s            write renaming script to batch directory
   -       -c            configuration file path and name, overrides default
   -       -p            project name identifier in configuration file, overrides default
   -       -b            batch directory name to be processed (required option)
         
For example, running the program on Batch1 in the default project with the default config would be:

python reseqr.py -s -b Batch1

## Deploying

## History

   - v.0.1 ~ Nov. 1, 2015
 

## Credits

W. Hays

## License 

MIT License (see file LICENSE)

