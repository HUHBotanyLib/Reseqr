import sys, getopt, re
import xml.etree.ElementTree as etree
import yaml

from os import listdir     #, rename
from os.path import isdir, isfile, join, splitext, abspath, exists

# namespace for METS
NS = { 'METS' : 'http://www.loc.gov/METS/' }

RPT_LINES = []

HELP = '''\nSYNOPSIS
    python3 reseqr.py -h -s -c <config> -p <project name> -b <batch name>
DESCRIPTION
        -h            help
        -s            write renaming script to batch directory
        -c            configuration file path and name, overrides default
        -p            project name identifier in configuration file, overrides default
        -b            batch directory name to be processed (required option)
           '''

config = None  #global access

def rpt(msg, quit = False):
    RPT_LINES.append(msg)
    print(msg)

    if quit:
        if config is not None:
            with open(config['report_path'], 'w') as rfile:
                for line in RPT_LINES: rfile.write(line + '\n')

        print(' -- Quitting Reseqr\n')
        sys.exit(2)


def read_project_config(config_file, project):
    ''' config parse and check for required values '''

    if config_file == None:
        config_file = 'reseqr.config'  # in current working directory
        rpt('Using default config file: ' + config_file)

    try:
        fyaml = open(config_file)
        config_all = yaml.safe_load(fyaml)
    except IOError:
        rpt('Unable to open config file: ' + config_file, True)
    else:
        fyaml.close()

        if project == None:
            try:
                project = config_all['default project']
            except KeyError:
                rpt('Unable to read default project name in configuration file. ', True)

    # configuration values now available
    if project not in config_all:
        rpt('project "' + project + '" not listed in configuration file', True)


    pconfig = config_all[project]

    #project_name = config['project_name']
    #project_path = config['project_path']
    #mets_path = config['mets_path']

    if 'project_name' not in pconfig:
        rpt('Project name not available in config.', False)
        pconfig['project_name'] = 'Missing project name'

    rpt('\nProject: "{}" located at {}'.format(pconfig['project_name'], abspath(pconfig['project_path'])), False)

    # FIXME these will break if err

    if 'project_path' not in pconfig:
        rpt('Project path not available in config.', True)

    if 'mets_path' not in pconfig:
        rpt('METS path not available in config.', True)

    global config
    config = pconfig

def get_batch_data(batch):

    if batch == None:
        rpt('batch param required. ' + HELP, True)

    batchpath = join(config['project_path'], batch)
    if not exists(batchpath):
        rpt('Specified batch does not exist: ' + batchpath, True)

    rpt('Processing batch "{}"\n'.format(batch))

    # won't throw exception if there are empty directories
    subdir_dict = { d : { f for f in listdir(join(batchpath, d)) if (d != 'mets') }
               for d in listdir(batchpath) if isdir(join(batchpath, d)) and (d != 'mets') }
    #rpt('subdirectories with files: ' + str(subdir_dict) + '\n')

    #subdirs = sorted([ d for d in listdir(batchpath) if isdir(join(batchpath, d)) and (d != 'mets') ])
    subdirs = sorted(subdir_dict.keys())

    desc = 'Batch directory summary:\n'
    for sd in subdirs:
        desc += '    {} with {:d} files\n'.format(sd, len(subdir_dict[sd]))

    desc += '\n'
    rpt(desc)

    #check for renaming prefix to prevent duplicate processing
    for sd in subdirs:
        for f in subdir_dict[sd]:
            if f.startswith(config['local_renaming_prefix']):
                rpt('subdirectory {} contains file already renamed'.format(sd), True)

    return subdirs, subdir_dict

def get_mets_file_data(re_pattern, mf):
    '''
    for each metsfile
        read all the structMap.div.div.fptr
        ToDo:  verify just one fptr per div
        Note: the FILEID has a production prefix + batch subdir prefix + seq number
              where the subdir prefix is unique to the metsfile in the given batch
        verify the FILEID matches the regular expression used for data extraction
        verify they have the same prefix
        ToDo: verify continuity of  order numbers

 <structMap>
  <div DMDID="C0" TYPE="CITATION">
   <div ORDER="1" LABEL="Hooker, Joseph D. June 12, 1873 [1]" TYPE="PAGE">
    <fptr FILEID="FIMG-JP2-GenA_0001"/>
   </div>
    '''

    # does this need exception handling?
    tree = etree.parse(mf)
    root = tree.getroot()

    fptr_data = []    # list of fptrs, each a dictionary with fields order, prefix, seqno
    prefixes = set()  # distinct prefixes

    for div in root.findall("./METS:structMap/METS:div/METS:div", NS):
        fptrs = div.findall("METS:fptr", NS)
        if len(fptrs) is not 1:
            rpt('METS div/div with no fptr or multiple fptr tags where ORDER = {}'.format(div.get("ORDER")), True)
        #print('fptrs: ' + str(len(fptrs)))
        fptr = div.find("METS:fptr", NS)
        m = re_pattern.match(fptr.get("FILEID"))
        if m:
            #print('group 1: ' + m.group(1) + '; group 2: ' + m.group(2) + '; group 3: ' + m.group(3))
            prefixes.add(m.group(2))
            fptr_data.append({ 'order' : div.get("ORDER"), 'filename' : m.group(1), 'seqno' : m.group(3) })
        else:
            rpt('METS FILEID does not match regular expression', True)

    #rpt('fptrdata: ' + str(fptr_data))

    prefix = None
    if len(prefixes) == 1:
        prefix = prefixes.pop()
    else:
        rpt('multiple FILEID prefixes for mets file ' + mf + ' : ' + str(prefixes), True)

    return prefix, fptr_data

def get_mets_data(batch):
    re_pattern = re.compile(r'' + config['imaging_services_prefix'] + '((\w+)_(\d+))')

    metsbatchpath = join(config['mets_path'], batch, 'mets')

    if not exists(metsbatchpath):
        rpt('METS directory for batch {} not found'.format(batch), true)

    metsfiles = sorted([ f for f in listdir(metsbatchpath) if splitext(f)[1] == '.xml' ])  # join path?
    #rpt(str(len(metsfiles)) + ' metsfiles: ' + str(metsfiles))

    if len(metsfiles) == 0:
        rpt("No mets files found for this batch", True)

    desc = 'METS files summary:\n'

    metsdata_dict = {}
    for mf in metsfiles:
        prefix, metsdata = get_mets_file_data(re_pattern, join(metsbatchpath, mf))
        metsdata_dict[prefix] = metsdata
        desc += '    {} with prefix "{}" listing {:d} file items\n'.format(mf, prefix, len(metsdata))

    desc += '\n'
    rpt(desc)

    return metsdata_dict

def compare_drive_to_mets(subdirs, subdir_dict, metsdata_dict):
    rpt('Validation:')
    # correlate batch subdirs and mets files
    # sort and compare subdirs and metsdata dictionaries
    if len(subdirs) != len(metsdata_dict):
        rpt('subdirs count ' + str(len(subdirs)) + ' != mets count' + str(len(metsdata_dict)), True)

    set_subdirs = set(subdirs)
    set_metsdata = set(metsdata_dict.keys())
    if set_subdirs != set_metsdata:
        rpt('subdirs names do not match mets file prefixes: ', False)  # exit after listing
        #list the differences
        diff_subdirs = set_subdirs - set_metsdata
        if len(diff_subdirs) > 0:
            rpt('  subdirs without corresponding mets files: ' + str(diff_subdirs), True)
        diff_metsdata = set_metsdata - set_subdirs
        if len(diff_metsdata) > 0:
            rpt('  mets files without corresponding subdirs: ' + str(diff_metsdata), True)
    else:
        rpt('    subdirectories match mets file prefixes')

    #if len(VAL_ERRS) > 0:
    #    rpt('    exiting early with validation errors', True, True)

    #compare file counts and fptr counts
    for sd in subdirs:
        fcount = len(subdir_dict[sd])
        #print('sd ' + sd + ' file count: ' + str(fcount))
        fptrcount = len(metsdata_dict[sd])
        #print('sd ' + sd + ' fptr count: ' + str(fptrcount))
        if len(subdir_dict[sd]) != len(metsdata_dict[sd]):
            rpt('In subdirectory {} mismatch of file counts with METS fptrs {}'.format(sd, str(fcount), str(fptrcount)), True)
        else:
            rpt('    subdirectory {} has same number of files as listed by associated mets file'.format(sd))

        #exit if any file not found on drive
        for fptr in metsdata_dict[sd]:
            if fptr['filename'] not in subdir_dict[sd]:
                rpt('file {} listed in mets not found in drive subdirectory'.format(fptr['filename']), True)
            #else:
            #    print('found {}'.format(fptr['filename']))

    rpt('    confirmed one-to-one correspondence between all METS fptr items and files on drive')


def write_renaming_script(metsdata_dict, batch):
    '''
    currently only Python
    currently don't separate scripts for each subdir

    note checking if script already exists, assume overwriting is intentional
    '''
    fname = join(config['project_path'], batch , batch + '-rename-script.py')

    lc = 0

    #try:
    with open(fname, 'w') as script:
        script.write('import os\n\n')

    #except (OSError, IOError) as e:
    #    rpt('Unable to open ' + fname + ' for renaming script', True, False)

        for subdir in sorted(metsdata_dict.keys()):   #ToDo: use subdirs list instead
            chunk = ''
            ren_prefix = config['local_renaming_prefix'] + subdir + '_'
            for fptr in metsdata_dict[subdir]:
                #print(str(fptr))
                #fpath = join(subdir, fptr['filename'])
                #print(str(fpath))

                #check that not renaming to self
                #src = join(subdir, fptr['filename'])
                #dest = join(subdir, 'R_' + subdir + '_' + fptr['order'])

                #put the same zero padding in the new file name as found in the FILEID
                template = '{}{:0' + str(len(fptr['seqno'])) + 'd}'
                chunk += ('os.rename( \'{}\', \'{}\')\n'.format(join(subdir, fptr['filename']),
                          join(subdir, template.format(ren_prefix, int(fptr['order'])))))

                lc = lc + 1
            script.write(chunk + '\n\n')
    rpt('Wrote script {} with {:d} lines'.format(fname, lc ))


def process_files(metsdata_dict, batch, exec):
    '''
    for files in the batch subdirectories,  either write a Python script to do renaming (exec == False)
    or rename files directly (exec == True)
    if renaming directly, each change action is written to the batch report
    currently don't separate scripts for each subdir

    ToDo: wait for go_ahead on direct renaming before implementing this
    '''



def main():

    print('Image File Resequencer: Reseqr')

    #default command line option values
    write_script = False
    force = False
    config_file = None
    project = None
    batch = None

    try:
#      opts, args = getopt.getopt(sys.argv[1:],"hi:o:,["ifile=","ofile="]")
        opts, args = getopt.getopt(sys.argv[1:],"hvsfc:p:b:")
    except getopt.GetoptError:
        rpt('getopterr: ' + HELP, True)

    for opt, arg in opts:
        if opt == '-h':
            print(HELP)
            sys.exit()
        #elif opt == '-v':
        #    global VERBOSE
        #    VERBOSE = True
        elif opt == '-s':
            write_script = True
        #elif opt == '-f':
        #    force = True
        elif opt == 'c':
            config_file = arg   #includes path
        elif opt == '-p':
            project = arg
        elif opt == "-b":
            batch = arg

    # assign to global
    read_project_config(config_file, project)

    #init reporting
    config['report_path'] = join(config['project_path'], batch, batch + '-report.txt')

    # batch subdirs and files
    subdirs, subdir_dict = get_batch_data(batch)

    # METS
    metsdata_dict = get_mets_data(batch)

    # valid correlation
    compare_drive_to_mets(subdirs, subdir_dict, metsdata_dict)

    # determine renaming
    # for each subdir, calculate the differences between order number and seq number to identify files to be renamed

    rpt('\n')

    if write_script:
        write_renaming_script(metsdata_dict, batch)

    rpt('Processing completed', True)

if __name__ == "__main__":
    main()