# Reseqr

Reseqr is a software tool developed for the Harvard Botany Libraries to rename batches of image files processed by the University Libraries' Imaging Services.  This operation validates the METS files with respect to their correlation to the image files on disk and corrects the sequence number in file names as specified in METS files associated with each batch.

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


## Usage

Reseqr is a command line application.   

## Deploying

## History

   - v.0.1 ~ Nov. 1, 2015
 

## Credits

W. Hays

## License - MIT License (see file LICENSE)

