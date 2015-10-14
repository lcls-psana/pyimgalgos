#!/usr/bin/env python
##-----------------------------
"""`GlobalUtils.py` contains collection of global utilities with a single call algorithms.

Usage::

    # Import
    # ==============
    from pyimgalgos.GlobalUtils import subtract_bkgd, mask_from_windows, ...

    # Background subtraction
    # ======================
    # Example for cspad, assuming all nda_*.shape = (32,185,388)
    winds_bkgd = [ (s, 10, 100, 270, 370) for s in (4,12,20,28)] # use part of segments 4,12,20, and 28 to subtract bkgd
    nda = subtract_bkgd(nda_data, nda_bkgd, mask=nda_mask, winds=winds_bkgd, pbits=0)

    # Operations with numpy array shape
    # =================================
    shape = (32,185,388)
    size = size_from_shape(shape) # returns 32*185*388   
    shape_2d = shape_as_2d(shape) # returns (32*185,388)
    arr_2d = reshape_to_2d(nda)   # returns re-shaped ndarray

    shape = (4,8,185,388)
    shape_3d = shape_as_3d(shape) # returns (32,185,388)
    arr_3d = reshape_to_3d(nda)   # returns re-shaped ndarray

    # Make mask n-d numpy array using shape and windows
    # =================================================
    shape = (2,185,388)
    w = 1
    winds = [(s, w, 185-w, w, 388-w) for s in (0,1)]
    mask = mask_from_windows(shape, winds)

    # Make mask as 2,3-d numpy array for a few(width) rows/cols of pixels 
    # ===================================================================
    mask2d = mask_2darr_edges(shape=(185,388), width=2)
    mask3d = mask_3darr_edges(shape=(32,185,388), width=5)

    # Make mask of local maximal intensity pixels in x-y (ignoring diagonals)
    # ===================================================================
    # works for 2-d and 3-d arrays only - reshape if needed.
    data = random_normal(shape=(32,185,388), mu=0, sigma=10, pbits=0377)
    mask_xy_max = locxymax(data, order=1, mode='clip')
 
    # Tests
    # ======================
    python pyimgalgos/src/GlobalUtils.py <test-number>

@see :py:class:`pyimgalgos.GlobalUtils`

This software was developed for the SIT project.  If you use all or 
part of it, please give an appropriate acknowledgment.

@version $Id$

@author Mikhail S. Dubrovin
"""

##-----------------------------
#  Module's version from CVS --
##-----------------------------
__version__ = "$Revision$"
# $Source$

##-----------------------------

import sys
import numpy as np
from scipy.signal import argrelmax

##-----------------------------

def size_from_shape(shape) :
    """Returns size from the shape sequence 
    """
    size=1
    for d in shape : size*=d
    return size

##-----------------------------

def shape_as_2d(sh) :
    """Returns 2-d shape for n-d shape if n>2, otherwise returns unchanged shape.
    """
    if len(sh)<3 : return sh
    return (size_from_shape(sh)/sh[-1], sh[-1])

##-----------------------------

def shape_as_3d(sh) :
    """Returns 3-d shape for n-d shape if n>3, otherwise returns unchanged shape.
    """
    if len(sh)<4 : return sh
    return (size_from_shape(sh)/sh[-1]/sh[-2], sh[-2], sh[-1])

##-----------------------------

def reshape_to_2d(arr) :
    """Returns n-d re-shaped to 2-d
    """
    arr.shape = shape_as_2d(arr.shape)
    return arr

##-----------------------------

def reshape_to_3d(arr) :
    """Returns n-d re-shaped to 3-d
    """
    arr.shape = shape_as_3d(arr.shape)
    return arr

##-----------------------------

def mask_2darr_edges(shape=(185,388), width=2) :
    """Returns mask with masked width rows/colunms of edge pixels for 2-d numpy array.
    """
    s, w = shape, width
    mask = np.zeros(shape, dtype=np.uint16)
    mask[w:-w,w:-w] = np.ones((s[0]-2*w,s[1]-2*w), dtype=np.uint16)
    return mask

##-----------------------------

def mask_3darr_edges(shape=(32,185,388), width=2) :
    """Returns mask with masked width rows/colunms of edge pixels for 3-d numpy array.
    """
    s, w = shape, width
    mask = np.zeros(shape, dtype=np.uint16)
    mask[:,w:-w,w:-w] = np.ones((s[0],s[1]-2*w,s[2]-2*w), dtype=np.uint16)
    return mask

##-----------------------------

def mask_from_windows(ashape=(32,185,388), winds=None) :
    """Makes mask as 2-d or 3-d numpy array defined by the shape with ones in windows.
       N-d shape for N>3 is converted to 3-d.
       @param shape - shape of the output numpy array with mask.
       @param winds - list of windows, each window is a sequence of 5 parameters (segment, rowmin, rowmax, colmin, colmax)     
    """
    ndim = len(ashape)
        
    if ndim<2 :
        print 'ERROR in mask_from_windows(...):',\
              ' Wrong number of dimensions %d in the shape=%s parameter. Allowed ndim>1.' % (ndim, str(shape))
        return None

    shape = ashape if ndim<4 else shape_as_3d(ashape)

    seg1 = np.ones((shape[-2], shape[-1]), dtype=np.uint16) # shaped as last two dimensions
    mask = np.zeros(shape, dtype=np.uint16)

    if ndim == 2 :
        for seg,rmin,rmax,cmin,cmax in winds : mask[rmin:rmax,cmin:cmax] =  seg1[rmin:rmax,cmin:cmax]
        return mask

    elif ndim == 3 :
        for seg,rmin,rmax,cmin,cmax in winds : mask[seg,rmin:rmax,cmin:cmax] =  seg1[rmin:rmax,cmin:cmax]
        return mask

##-----------------------------

def list_of_windarr(nda, winds=None) :
    """Converts 2-d or 3-d numpy array in the list of 2-d numpy arrays for windows
       @param nda - input 2-d or 3-d numpy array
    """
    ndim = len(nda.shape)
    #print 'len(nda.shape): ', ndim

    if ndim == 2 :
        return [nda] if winds is None else \
               [nda[rmin:rmax, cmin:cmax] for (s, rmin, rmax, cmin, cmax) in winds]

    elif ndim == 3 :
        return [nda[s,:,:] for s in range(ndim.shape[0])] if winds is None else \
               [nda[s, rmin:rmax, cmin:cmax] for (s, rmin, rmax, cmin, cmax) in winds]

    else :
        print 'ERROR in list_of_windarr (with winds): Unexpected number of n-d array dimensions: ndim = %d' % ndim
        return []

##-----------------------------

def mean_of_listwarr(lst_warr) :
    """Evaluates the mean value of the list of 2-d arrays.
       @lst_warr - list of numpy arrays to evaluate per pixel mean intensity value.
    """
    s1, sa = 0., 0. 
    for warr in lst_warr :
        sa += np.sum(warr, dtype=np.float64)
        s1 += warr.size
    return sa/s1 if s1 > 0 else 1

##-----------------------------

def subtract_bkgd(data, bkgd, mask=None, winds=None, pbits=0) :
    """Subtracts numpy array of bkgd from data using normalization in windows for good pixels in mask.
       Shapes of data, bkgd, and mask numpy arrays should be the same.
       Each window is specified by 5 parameters: (segment, rowmin, rowmax, colmin, colmax)
       For 2-d arrays segment index is not used, but still 5 parameters needs to be specified.
       @param data - numpy array for data.
       @param bkgd - numpy array for background.
       @param mask - numpy array for mask.
       @param winds - list of windows, each window is a sequence of 5 parameters.     
       @param pbits - print control bits; =0 - print nothing, !=0 - normalization factor.
    """
    mdata = data if mask is None else data*mask
    mbkgd = bkgd if mask is None else bkgd*mask

    lwdata = list_of_windarr(mdata, winds)
    lwbkgd = list_of_windarr(mbkgd, winds)
    
    mean_data = mean_of_listwarr(lwdata)
    mean_bkgd = mean_of_listwarr(lwbkgd)

    frac = mean_data/mean_bkgd
    if pbits : print 'subtract_bkgd, fraction = %10.6f' % frac

    return data - bkgd*frac



##-----------------------------
# See: http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.argrelmax.html#scipy.signal.argrelmax

def locxymax(nda, order=1, mode='clip') :
    """For 2-d or 3-d numpy array finds mask of local maxima in x and y axes (diagonals are ignored) 
       using scipy.signal.argrelmax and return their product.

       @param nda - input ndarray
       @param order - range to search for local maxima along each dimension
       @param mode - parameter of scipy.signal.argrelmax of how to treat the boarder
    """
    shape = nda.shape
    size  = nda.size
    ndim = len(shape)

    if ndim< 2 or ndim>3 :
        msg = 'ERROR: locxymax nda shape %s should be 2-d or 3-d' % (shape)
        sys.exit(msg)

    ext_cols = argrelmax(nda, -1, order, mode)
    ext_rows = argrelmax(nda, -2, order, mode)
    
    indc = np.array(ext_cols, dtype=np.uint16)
    indr = np.array(ext_rows, dtype=np.uint16)

    msk_ext_cols = np.zeros(shape, dtype=np.uint16)
    msk_ext_rows = np.zeros(shape, dtype=np.uint16)

    if ndim == 2 :
        icr = indc[0,:] 
        icc = indc[1,:]
        irr = indr[0,:]
        irc = indr[1,:]

        msk_ext_cols[icr,icc] = 1
        msk_ext_rows[irr,irc] = 1

    elif ndim == 3 :
        ics = indc[0,:] 
        icr = indc[1,:] 
        icc = indc[2,:]
        irs = indr[0,:]
        irr = indr[1,:]
        irc = indr[2,:]

        msk_ext_cols[ics,icr,icc] = 1
        msk_ext_rows[irs,irr,irc] = 1

    #print 'nda.size:',   nda.size
    #print 'indc.shape:', indc.shape
    #print 'indr.shape:', indr.shape
    
    return msk_ext_rows * msk_ext_cols

##-----------------------------
##-----------------------------
##---------- TEST -------------
##-----------------------------
##-----------------------------

from pyimgalgos.TestImageGenerator import random_normal
from time import time
import pyimgalgos.GlobalGraphics as gg

##-----------------------------

def test_01() :
    print '%s\n%s\n' % (80*'_','Test method subtract_bkgd(...):')
    shape1 = (32,185,388)
    winds = [ (s, 10, 155, 20, 358) for s in (0,1)]
    data = random_normal(shape=shape1, mu=300, sigma=50, pbits=0377)
    bkgd = random_normal(shape=shape1, mu=100, sigma=10, pbits=0377)

    cdata = subtract_bkgd(data, bkgd, mask=None, winds=winds, pbits=0377)

##-----------------------------

def test_02() :
    print '%s\n%s\n' % (80*'_','Test method size_from_shape(shape):')
    shape = (2,3,4,5)
    print '  shape=%s,  size_from_shape(shape)=%d' % (shape, size_from_shape(shape))

##-----------------------------

def test_03() :
    print '%s\n%s\n' % (80*'_','Test method shape_as_2d(shape):')
    shape = (2,3,4,5)
    print '  shape=%s,  shape_as_2d(shape)=%s' % (shape, shape_as_2d(shape))

##-----------------------------

def test_04() :
    print '%s\n%s\n' % (80*'_','Test method shape_as_3d(shape):')
    shape = (2,3,4,5)
    print '  shape=%s,  shape_as_3d(shape)=%s' % (shape, shape_as_3d(shape))

##-----------------------------

def test_05() :
    print '%s\n%s\n' % (80*'_','Test method mask_from_windows(shape, winds):')
    shape = (2,185,388)
    w = 1
    winds = [(s, w, 185-w, w, 388-w) for s in (0,1)]
    mask = mask_from_windows(shape, winds)
    print '  shape=%s \nwinds:\n%s, \nmask_from_windows(shape, winds):\n%s' % (shape, winds, mask_from_windows(shape, winds))

##-----------------------------

def test_06() :
    print '%s\n%s\n' % (80*'_','Test method mask_3darr_edges(shape, width):')
    shape = (32,185,388)
    width = 1
    print '  shape=%s, masking width=%d, mask_3darr_edges(shape, width):\n%s' % (shape, width, mask_3darr_edges(shape, width))

##-----------------------------

def test_07() :
    print '%s\n%s\n' % (80*'_','Test method mask_2darr_edges(shape, width):')
    shape = (185,388)
    width = 2
    print '  shape=%s, masking width=%d, mask_2darr_edges(shape, width):\n%s' % (shape, width, mask_2darr_edges(shape, width))

##-----------------------------

def test_08() :
    print '%s\n%s\n' % (80*'_','Test method locxymax(nda, order, mode):')
    #data = random_normal(shape=(32,185,388), mu=0, sigma=10, pbits=0377)
    data = random_normal(shape=(2,185,388), mu=0, sigma=10, pbits=0377)
    t0_sec = time()
    mask = locxymax(data, order=1, mode='clip')
    print 'Consumed t = %10.6f sec' % (time()-t0_sec)

    if True :
      img = data if len(data.shape)==2 else reshape_to_2d(data)
      msk = mask if len(mask.shape)==2 else reshape_to_2d(mask)

      ave, rms = img.mean(), img.std()
      amin, amax = ave-2*rms, ave+2*rms
      gg.plotImageLarge(img, amp_range=(amin, amax), title='random')
      gg.plotImageLarge(msk, amp_range=(0, 1), title='mask loc max')
      gg.show()

##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------

def usage() : return 'Use command: python %s <test-number>, where <test-number> = 1,2,...,7,...' % sys.argv[0]

##-----------------------------

def main() :    
    print '\n%s\n' % usage()
    if len(sys.argv) != 2 : test_01()
    elif sys.argv[1]=='1' : test_01()
    elif sys.argv[1]=='2' : test_02()
    elif sys.argv[1]=='3' : test_03()
    elif sys.argv[1]=='4' : test_04()
    elif sys.argv[1]=='5' : test_05()
    elif sys.argv[1]=='6' : test_06()
    elif sys.argv[1]=='7' : test_07()
    elif sys.argv[1]=='8' : test_08()
    else                  : sys.exit ('Test number parameter is not recognized.\n%s' % usage())

##-----------------------------

if __name__ == "__main__" :
    main()
    sys.exit('\nEnd of test')

##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------
