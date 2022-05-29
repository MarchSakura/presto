#!/bin/env python2
"""
A simple pipelien for demostrating presto
Weiwei Zhu
2015-08-14
Max-Plank Institute for Radio Astronomy
zhuwwpku@gmail.com
"""
import os, sys, glob, re
from presto import sifting
from operator import attrgetter
from commands import getoutput
import numpy as np
import time
import multiprocessing
from multiprocessing.dummy import Pool as dummyPool
process_cnt = multiprocessing.cpu_count()

sstime = time.time()

rootname = 'Sband'
maxDM = 80 #max DM to search
Nsub = 32 #32 subbands
Nint = 64 #64 sub integration
Tres = 0.5 #ms
zmax = 0
process_cnt = multiprocessing.cpu_count()

def func(command):
    return getoutput(command)

def double_func(command1, command2):
    ret = getoutput(command1)
    ret = ret+getoutput(command2)
    return ret

def multifunc(cmds):
    ret = ''
    for command in cmds:
        ret = ret + getoutput(command)
    return ret

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
        #cands.sort(sifting.cmp_sigma)
        cands.sort(key=attrgetter('sigma'), reverse=True)
        #for cand in cands[:1]:
            #print cand.filename, cand.candnum, cand.p, cand.DMstr
        #sifting.write_candlist(cands)
    return cands

if __name__ == '__main__':

    filename = sys.argv[1]
    if len(sys.argv) > 2:
        maskfile = sys.argv[2]
    else:
        maskfile = None

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

    print header
    #except:
        #print 'failed at reading file %s.' % filename
        #sys.exit(0)


    print '''

    ============Generate Dedispersion Plan===============

    '''

    time_start = time.time()

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



    time_end = time.time()
    print 'Generate DDPlan time_cost: ', time_end - time_start


    print '''

    ================Dedisperse Subbands==================

    '''
    time_start = time.time()

    cwd = os.getcwd()
    try:
        if not os.access('subbands', os.F_OK):
            os.mkdir('subbands')
        os.chdir('subbands')
        #logfile = open('dedisperse.log', 'wt')
        res = []
        DSpool = multiprocessing.Pool(process_cnt)
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
                if maskfile:
                    prepsubband = "prepsubband -sub -subdm %.2f -nsub %d -downsamp %d -mask ../%s -o %s %s" % (subDM, Nsub, subdownsamp, maskfile, rootname, '../'+filename)
                else:
                    prepsubband = "prepsubband -sub -subdm %.2f -nsub %d -downsamp %d -o %s %s" % (subDM, Nsub, subdownsamp, rootname, '../'+filename)
                #print prepsubband

                subnames = rootname+"_DM%.2f.sub[0-9]*" % subDM
                prepsubcmd = "prepsubband -nsub %(Nsub)d -lodm %(lowdm)f -dmstep %(dDM)f -numdms %(NDMs)d -numout %(Nout)d -downsamp %(DownSamp)d -o %(root)s %(subfile)s" % {
                        'Nsub':Nsub, 'lowdm':lodm, 'dDM':dDM, 'NDMs':NDMs, 'Nout':Nout, 'DownSamp':datdownsamp, 'root':rootname, 'subfile':subnames}
                #print prepsubcmd
                res.append(DSpool.apply_async(func=double_func, args=(prepsubband, prepsubcmd,)))

            DSpool.close()
            DSpool.join()
        res0 = [i.get() for i in res]
        with open('dedisperse.log', 'wt') as f:
            for i in res0:
                f.write(i)
        os.system('rm *.sub*')
        #logfile.close()
        os.chdir(cwd)

    except:
        print 'failed at prepsubband.'
        os.chdir(cwd)
        sys.exit(0)


    time_end = time.time()
    print 'Dedisperse Subbands time_cost: ', time_end - time_start


    print '''

    ================fft-search subbands==================

    '''

    time_start = time.time()

    try:
        os.chdir('subbands')
        datfiles = glob.glob("*.dat")
        #logfile = open('fft.log', 'wt')
        poolsize = len(datfiles) if len(datfiles) < multiprocessing.cpu_count() else process_cnt
        DATpool = multiprocessing.Pool(poolsize)
        res2 = []
        for df in datfiles: 
            # fftcmd = "realfft %s" % df
            searchcmd2 = "accelsearch -zmax %d %s"  % (zmax, df)
            res2.append(DATpool.apply_async(func=func, args=(searchcmd2,)))
    
        DATpool.close()
        DATpool.join()
        
        res22 = [i.get() for i in res2]
        with open('fft.log', 'wt') as f:
            for i in res22:
                f.write(i)

        os.chdir(cwd)
    except Exception as ex:
        print ex
        print 'failed at fft search.'
        os.chdir(cwd)
        sys.exit(0)



    time_end = time.time()
    print 'fft-search subbands time_cost: ', time_end - time_start

    print '''

    ================sifting candidates==================

    '''

    time_start = time.time()

    cwd = os.getcwd()
    os.chdir('subbands')
    cands = ACCEL_sift(zmax)
    os.chdir(cwd)


    time_end = time.time()
    print 'sifting candidates time_cost: ', time_end - time_start

    print '''

    ================folding candidates==================

    '''

    time_start = time.time()

    try:
        cwd = os.getcwd()
        os.chdir('subbands')
        os.system('ln -s ../%s %s' % (filename, filename))
        #logfile = open('folding.log', 'wt')
        res3 = []
        poolsize = multiprocessing.cpu_count()
        Fpool = multiprocessing.Pool(poolsize)
        for cand in cands:
            foldcmd = "prepfold -n %(Nint)d -nsub %(Nsub)d -dm %(dm)f -p %(period)f %(filfile)s -o %(outfile)s -noxwin -nodmsearch" % {
                    'Nint':Nint, 'Nsub':Nsub, 'dm':cand.DM,  'period':cand.p, 'filfile':filename, 'outfile':rootname+'_DM'+cand.DMstr} #full plots
            res3.append(Fpool.apply_async(func=func, args=(foldcmd, )))
        Fpool.close()
        Fpool.join()
        res33 = [i.get() for i in res3]
        with open('folding.log', 'wt') as f:
            for i in res33:
                f.write(i)
        os.chdir(cwd)
    except:
        print 'failed at folding candidates.'
        os.chdir(cwd)
        sys.exit(0)


    time_end = time.time()
    print 'folding candidates time_cost: ', time_end - time_start

    eetime = time.time()
    print 'total time: ', eetime-sstime
