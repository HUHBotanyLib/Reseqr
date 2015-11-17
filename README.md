# Reseqr

Reseqr is a small software tool for the command line developed for the Harvard Botany Libraries to rename large batches of image files processed by the University Libraries' Imaging Services.  This operation validates the associated METS files with respect to their correlation to the image files on disk and corrects the sequence number in file names as specified in METS files associated with each batch.  Specifically for each file item, the "ORDER" integer value is used to replace the sequence number at the end of the FILEID value, which is the filename on the drive (with a prefix attached).

The specifics of a given project of collated batches have been localized in a configuration file, so this tool may be adapted for other image file processing operations with similar needs.

Reseqr is written in Python3 (v.3.4) and can be run on Windows, OSX, and Linux machines.  Additionally, the PyYAML library must be installed.

## Functionality

   - operates on a single batch per program execution
   - validates image file batch for expected naming conventions
   - validates batch METS files for expected conventions
   - validates correlation between image files and METS descriptors
   - reports validation results to screen and file
   - reports intended file renaming as a Python script that can be run separately
   - renames all image files with an additional prefix to avoid collision, even when no sequence number change is required
   - generates an 'undo' script if a renaming script or renaming execution is specified
   - marks batches to avoid double execution
   - reports on renaming results
   - uses an editable configuration file with each project's constant data
   - allows for concurrent projects

Basic operation includes validation and reporting in all cases.  Additionally the program can be run to either produce a Python script that will rename the files or to rename the files directly.

## Project Setup
   - Image file batches for a given project are located in a single directory specified in the config
   - Each batch is assumed to contain one or more subdirectories that contain the image files
   - METS files are located in the batch subdirectory called 'mets'
   - METS files are in a one-to-one correspondence with the image file subdirectories but are not named so as to determine the pairing.  This is determined by the program reading the METS files.
   - The batch processing report is written to the batch directory.
   - The generated renaming script for a batch covers all the image files in all the subdirectories and is written to the batch directory.

## Configuration file

  -  Uses YAML as the markup language, for its simplicity
  -  Default configuration file is called reseqr.config in distribution directory
  -  Default project can be specified in the config
  -  Multiple project configurations are listed in different sections
  -  Use test project as a model for configuring new projects

## Usage

Reseqr is run from the command line using the Python 3 interpreter or in the Python 3 shell.
The python command can be either "python" as on Windows or "python3" on other operating systems.

`python reseqr.py -h -s -c <config> -p <project name> -b <batch name>`

where the options indicate:
   -       -h            help
   -       -s            write renaming script to batch directory
   -       -x            execute renaming of files
   -       -c            configuration file path and name, overrides default
   -       -p            project name identifier in configuration file, overrides default
   -       -b            batch directory name to be processed (required option)

Options -s and -x are mutually exclusive.

For example, running the program on Batch1 in the default project with the default config would be:

`python reseqr.py -s -b Batch1`

## Testing

Reseqr comes with a test project that constitutes a suite of tests for different error conditions.
Actual image files are not used, only tiny text files named according to the expected image filenaming patterns.

  - Batch1    No errors
  - Batch2
  - Batch3

## Deploying

Download the zip archive from the GitHub project page and extract to the local drive.

## History

   - v.0.1 ~ Nov. 1, 2015


## Credits

J.J. Ford (project manager)
W. Hays (developer)


## License

MIT License (see file LICENSE)

