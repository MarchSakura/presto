#!/home/lqq/presto_with_all_lib/venv/bin/python
# -*- coding: utf-8 -*-

"""
A simple pipelien for demostrating presto
Weiwei Zhu
2015-08-14
Max-Plank Institute for Radio Astronomy
zhuwwpku@gmail.com
"""
import os, sys, glob, re, time
from presto import sifting
from commands import getoutput
from operator import itemgetter, attrgetter
import numpy as np
from multiprocessing import Pool
from multiprocessing import Process

rootname = 'Sband'
maxDM = 80 #max DM to search
Nsub = 32 #32 subbands
Nint = 64 #64 sub integration
Tres = 0.5 #ms
zmax = 0

filename = sys.argv[1]
if len(sys.argv) > 2:
    maskfile = sys.argv[2]
else:
    maskfile = None

def batch_dedisperse_n_fft(name, prep, prepcmd, real_list, accel_list):
    st = time.time()
    logfile = open('dedisperse_%.3f.log' % name, 'wt')
    buffer = []
    print(prep)
    output = getoutput(prep)
    buffer.append(output)
    print(prepcmd)
    output = getoutput(prepcmd)
    buffer.append(output)
    logfile.write("".join(buffer))
    logfile.close()
    buffer = []
    logfile = open('fft_%.3f.log' % name, 'wt')
    for cmd in real_list:
        print(cmd)
        output = getoutput(cmd)
        buffer.append(output)
    for cmd in accel_list:
        print(cmd)
        output = getoutput(cmd)
        buffer.append(output)
    ed = time.time()
    ttime = "fft_batch_time: %f" % (ed - st)
    buffer.append(ttime)
    logfile.write("".join(buffer))
    logfile.close()

def func_wrap(x):
    return batch_dedisperse_n_fft(*x)

def write_fold_log(msg):
    logfile = open('folding.log', 'w')
    logfile.write("\n".join(msg))
    logfile.close()

def combine_log(dedisperse_list):
    cwd = os.getcwd()
    os.chdir("subbands")
    dedisperse_files = ['dedisperse_%.3f.log' % x for x in dedisperse_list]
    fp = open("dedisperse.log", "wt")
    for file in dedisperse_files:
        with open(file, "r") as f:
            fp.write("\n".join(f.readlines()))
    fp.close()
    glob_fft = "fft_[0-9]*.log"
    fft_files = glob.glob(glob_fft)
    fp = open("fft.log", "wt")
    for file in fft_files:
        with open(file, "r") as f:
            fp.write("\n".join(f.readlines()))
    fp.close()
    os.chdir(cwd)
    print("finish combine didesperse and fft log")

def batch_prepfold(fold):
    st = time.time()
    print(fold)
    output = getoutput(fold)
    ed = time.time()
    ttime = "single_fold_time: %f" % (ed - st)
    print(ttime)
    return output

def ACCEL_sift(zmax):
    '''
    The following code come from PRESTO's ACCEL_sift.py
    '''

    globaccel = "*ACCEL_%d" % zmax
    globinf = "*DM*.inf"
    # In how many DMs must a candidate be detected to be considered "good"
    min_num_DMs = 2
    # Lowest DM to consider as a "real" pulsar
    low_DM_cutoff = 2.0
    # Ignore candidates with a sigma (from incoherent power summation) less than this
    sifting.sigma_threshold = 4.0
    # Ignore candidates with a coherent power less than this
    sifting.c_pow_threshold = 100.0

    # If the birds file works well, the following shouldn't
    # be needed at all...  If they are, add tuples with the bad
    # values and their errors.
    #                (ms, err)
    sifting.known_birds_p = []
    #                (Hz, err)
    sifting.known_birds_f = []

    # The following are all defined in the sifting module.
    # But if we want to override them, uncomment and do it here.
    # You shouldn't need to adjust them for most searches, though.

    # How close a candidate has to be to another candidate to                
    # consider it the same candidate (in Fourier bins)
    sifting.r_err = 1.1
    # Shortest period candidates to consider (s)
    sifting.short_period = 0.0005
    # Longest period candidates to consider (s)
    sifting.long_period = 15.0
    # Ignore any candidates where at least one harmonic does exceed this power
    sifting.harm_pow_cutoff = 8.0

    #--------------------------------------------------------------

    # Try to read the .inf files first, as _if_ they are present, all of
    # them should be there.  (if no candidates are found by accelsearch
    # we get no ACCEL files...
    inffiles = glob.glob(globinf)
    candfiles = glob.glob(globaccel)
    # Check to see if this is from a short search
    if len(re.findall("_[0-9][0-9][0-9]M_" , inffiles[0])):
        dmstrs = [x.split("DM")[-1].split("_")[0] for x in candfiles]
    else:
        dmstrs = [x.split("DM")[-1].split(".inf")[0] for x in inffiles]
    dms = map(float, dmstrs)
    dms.sort()
    dmstrs = ["%.2f"%x for x in dms]

    # Read in all the candidates
    cands = sifting.read_candidates(candfiles)

    # Remove candidates that are duplicated in other ACCEL files
    if len(cands):
        cands = sifting.remove_duplicate_candidates(cands)

    # Remove candidates with DM problems
    if len(cands):
        cands = sifting.remove_DM_problems(cands, min_num_DMs, dmstrs, low_DM_cutoff)

    # Remove candidates that are harmonically related to each other
    # Note:  this includes only a small set of harmonics
    if len(cands):
        cands = sifting.remove_harmonics(cands)

    # Write candidates to STDOUT
    if len(cands):
        cands.sort(key=attrgetter("sigma"), reverse=True)
        #for cand in cands[:1]:
            #print cand.filename, cand.candnum, cand.p, cand.DMstr
        #sifting.write_candlist(cands)
    return cands

if __name__=="__main__":

    print("new 0.1.2")    


    ss = time.time()
    print '''

    ====================Read Header======================

    '''

    readheadercmd = 'readfile %s' % filename
    print readheadercmd
    output = getoutput(readheadercmd)
    print output
    header = {}
    for line in output.split('\n'):
        items = line.split("=")
        if len(items) > 1:
            header[items[0].strip()] = items[1].strip()

    #print header
    #except:
        #print 'failed at reading file %s.' % filename
        #sys.exit(0)

    ee = time.time()
    print('Read Header time_cost: ', ee - ss)


    ss = time.time()

    print '''

    ============Generate Dedispersion Plan===============

    '''

    try:
        Nchan = int(header['Number of channels'])
        tsamp = float(header['Sample time (us)']) * 1.e-6
        BandWidth = float(header['Total Bandwidth (MHz)'])
        fcenter = float(header['Central freq (MHz)'])
        Nsamp = int(header['Spectra per file'])

        ddplancmd = 'DDplan.py -d %(maxDM)s -n %(Nchan)d -b %(BandWidth)s -t %(tsamp)f -f %(fcenter)f -s %(Nsub)s -o DDplan.ps' % {
                'maxDM':maxDM, 'Nchan':Nchan, 'tsamp':tsamp, 'BandWidth':BandWidth, 'fcenter':fcenter, 'Nsub':Nsub}
        print ddplancmd
        ddplanout = getoutput(ddplancmd)
        print ddplanout
        planlist = ddplanout.split('\n')
        ddplan = []
        planlist.reverse()
        for plan in planlist:
            if plan == '':
                continue
            elif plan.strip().startswith('Low DM'):
                break
            else:
                ddplan.append(plan)
        ddplan.reverse()
    except:
        print 'failed at generating DDplan.'
        sys.exit(0)


    ee = time.time()
    print('Generate Dedispersion Plan time_cost: ', ee - ss)


    ss = time.time()

    print '''

    ================Dedisperse Subbands==================

    '''


    cwd = os.getcwd()

    try:
        if not os.access('subbands', os.F_OK):
            os.mkdir('subbands')
        else:
            print('subbands dir exists')
        os.chdir('subbands')

        huge_zip = []
        subDM_list = []
        prepsubband_sub_cmd = []
        prepsubband_nsub_cmd = []
        realfft_cmd = []
        accelsearch_cmd = []
        for line in ddplan:
            ddpl = line.split()
            lowDM = float(ddpl[0])
            hiDM = float(ddpl[1])
            dDM = float(ddpl[2])
            DownSamp = int(ddpl[3])
            NDMs = int(ddpl[6])
            calls = int(ddpl[7])
            Nout = Nsamp/DownSamp 
            Nout -= (Nout % 500)
            dmlist = np.split(np.arange(lowDM, hiDM, dDM), calls)

            #copy from $PRESTO/python/Dedisp.py
            subdownsamp = DownSamp/2
            datdownsamp = 2
            if DownSamp < 2: subdownsamp = datdownsamp = 1


            for i, dml in enumerate(dmlist):
                lodm = dml[0]
                subDM = np.mean(dml)
                subDM_list.append(subDM)
                if maskfile:
                    prepsubband = "prepsubband -sub -subdm %.2f -nsub %d -downsamp %d -mask ../%s -o %s %s" % (subDM, Nsub, subdownsamp, maskfile, rootname, '../'+filename)
                else:
                    prepsubband = "prepsubband -sub -subdm %.2f -nsub %d -downsamp %d -o %s %s" % (subDM, Nsub, subdownsamp, rootname, '../'+filename)
                prepsubband_sub_cmd.append(prepsubband)

                subnames = rootname+"_DM%.2f.sub[0-9]*" % subDM
                #prepsubcmd = "prepsubband -nsub %(Nsub)d -lodm %(lowdm)f -dmstep %(dDM)f -numdms %(NDMs)d -numout %(Nout)d -downsamp %(DownSamp)d -o %(root)s ../%(filfile)s" % {
                        #'Nsub':Nsub, 'lowdm':lodm, 'dDM':dDM, 'NDMs':NDMs, 'Nout':Nout, 'DownSamp':datdownsamp, 'root':rootname, 'filfile':filename}
                prepsubcmd = "prepsubband -nsub %(Nsub)d -lodm %(lowdm)f -dmstep %(dDM)f -numdms %(NDMs)d -numout %(Nout)d -downsamp %(DownSamp)d -o %(root)s %(subfile)s" % {
                        'Nsub':Nsub, 'lowdm':lodm, 'dDM':dDM, 'NDMs':NDMs, 'Nout':Nout, 'DownSamp':datdownsamp, 'root':rootname, 'subfile':subnames}
                prepsubband_nsub_cmd.append(prepsubcmd)

                realfft_cmd.append(["realfft Sband_DM%.2f.dat" % i for i in dml])
                accelsearch_cmd.append(["accelsearch -zmax 0 Sband_DM%.2f.fft" % i for i in dml])

            pool = Pool()
            pool.map(func_wrap, zip(subDM_list, prepsubband_sub_cmd, prepsubband_nsub_cmd, realfft_cmd, accelsearch_cmd))
            pool.close()
            pool.join()

        os.system('rm *.sub*')
        # logfile.close()
        os.chdir(cwd)
    except Exception as ex:
        print(ex)
        print 'failed at prepsubband.'
        os.chdir(cwd)
        sys.exit(0)

    ee = time.time()
    print('Dedisperse Subbands time_cost: ', ee - ss)

    # combining the fft and dedisperse log
    combine_process = Process(target=combine_log, args=(subDM_list,))
    combine_process.start()

    ss = time.time()

    print '''

    ================sifting candidates==================

    '''

    cwd = os.getcwd()
    os.chdir('subbands')
    cands = ACCEL_sift(zmax)
    os.chdir(cwd)


    ee = time.time()
    print('sifting candidates time_cost: ', ee - ss)

    ss = time.time()

    print '''

    ================folding candidates==================

    '''

    try:
        cwd = os.getcwd()
        os.chdir('subbands')
        os.system('ln -s ../%s %s' % (filename, filename))

        prepfold_cmd = []
        dm_list = []

        # logfile = open('folding.log', 'wt')
        for cand in cands:
            #foldcmd = "prepfold -dm %(dm)f -accelcand %(candnum)d -accelfile %(accelfile)s %(datfile)s -noxwin " % {
            #'dm':cand.DM,  'accelfile':cand.filename+'.cand', 'candnum':cand.candnum, 'datfile':('%s_DM%s.dat' % (rootname, cand.DMstr))} #simple plots
            foldcmd = "prepfold -n %(Nint)d -nsub %(Nsub)d -dm %(dm)f -p %(period)f %(filfile)s -o %(outfile)s -noxwin -nodmsearch" % {
                    'Nint':Nint, 'Nsub':Nsub, 'dm':cand.DM,  'period':cand.p, 'filfile':filename, 'outfile':rootname+'_DM'+cand.DMstr} #full plots
            dm_list.append(cand.DM)
            prepfold_cmd.append(foldcmd)
        pool = Pool()
        res = pool.map_async(func=batch_prepfold, iterable=prepfold_cmd, callback=write_fold_log)
        pool.close()
        pool.join()
        res.get()
        os.chdir(cwd)
    except:
        print 'failed at folding candidates.'
        os.chdir(cwd)
        sys.exit(0)


    ee = time.time()
    print('folding candidates time_cost: ', ee - ss)

    combine_process.join()