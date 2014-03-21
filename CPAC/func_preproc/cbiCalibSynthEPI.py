'''
@Krishna Somandepalli
>> Original matlab code by Dr. Edward Vessel re-coded in python 
>> Details of B0 calibration scan:
   https://cbi.nyu.edu/media/library/InterModal_Registration_Using_Calibration.pdf
>> Specific for 'calibration' scans acquired at the 3.0 T Siemens scanner at the 
   Center for Biological Imaging (CBI)
>> Calibration scan outputs in the originals:
cal.nii: calibration data
cal_mean.nii: mean of abs value of cal.nii
cal_snr.nii: SNR image

cal_rho.nii: spin density image 
cal_bo.nii: frequency (B0 field map) image 
cal_rs.nii: R2* image 

cal_mask.nii: brain mask used to restrict calculations and for regularization 
cal_coil.nii: coil sensitivity profile 
cal_oe.nii: phase difference between odd and even echoes 
cal_params.mat: matlab .mat file of stored calibration parameters 

cal_reg_bo.nii : regularized (smoothed) versions of parameter estimates       
cal_reg_rho.nii: ----||----
cal_reg_rs.nii: ----||---- 
cal_reg_coil.nii: ----||----
cal_reg_oe.nii: ----||----
 
cal_synth.nii: synthetic image computed as the average over the calibration  
               scan readout window (NOTE this is NOT the same as the ouput of the current code) 
'''

import nibabel as nb
import numpy as np
import os

#TE=30
#kydir=1
#rhoName = '/sam/wave1/sub4974/calib_1/cal_rho.nii.gz'
#boName = '/sam/wave1/sub4974/calib_1/cal_bo.nii.gz'
#rsName = '/sam/wave1/sub4974/calib_1/cal_rs.nii.gz'

def cbi_create_synth(boName,rhoName, rsName, TE=30, kyDir=1, synthName='cal_synth.nii.gz'):
#if True:
	bo_ = nb.load(boName)
	bo = bo_.get_data()
	#bo_hdr = bo_.get_header(); bo_aff = bo_.get_affine()
	
	rho_ = nb.load(rhoName)
	rho = rho_.get_data()
	#rho_hdr = rho_.get_header(); rho_aff = rho_.get_affine()
	
	rs_ = nb.load(rsName)
	rs = rs_.get_data()
	rs_hdr = rs_.get_header()
	rs_aff = rs_.get_affine()
	
	#change the sign of bo acc to the readout direction kyDir
	bo = float(kydir)*bo
	TE = int(TE)
	
	Ny = rho.shape[1]
	ky = np.array(range((-1*Ny)/2, (Ny/2)))
	y = np.array([float(i) for i in range((-1*Ny)/2, (Ny/2))])/Ny

	# Forward model and inverse
	# see recon code for sign convention, etc.
	# we're going to apply the matrices on the right
	# The fourier operator
	
	zFy=np.empty(shape=(Ny,Ny),dtype=complex)
	for n in range(Ny): 
		zFy[:,n] = np.exp(2*np.pi*1j*ky[n]*y)
	
	#adjoint is the inverse
	#transpose of the conjugate of a matri is its adjoint
	zPFy = zFy.conj().transpose()
	
	# forward is the integeral
	zFy = zFy/Ny
	tStart = TE - (Ny/2)
	
	# Loop over the slices and process one at a time
	#bors = exp(tStart*(i*boslice-rsslice));
    	# ignore phase evolution up to begining of readout
    	# this fixes a weird artifact in the synthetic data
    	# if bo is not exactly right
	
	epi = np.zeros(rho.shape)
	for nz in range(epi.shape[-1]):
		rhoslice = rho[:,:,nz]
		boslice  = bo[:,:,nz]
		rsslice  = rs[:,:,nz]
                data = np.empty(shape=(epi.shape[0],Ny), dtype=complex)
    		brfactor = np.exp((1j*boslice) - rsslice)
		
    		bors = np.exp(np.dot(-1*tStart, rs[:,:,nz]))
		print bors.dtype
		
		
    		for nn in range(Ny):
        		bors = bors*brfactor
        		data[:,nn] = np.dot((bors*rhoslice),zFy[:,nn])
    		
		epi[:,:,nz] = abs(np.dot(data , zPFy))
	
	epi_synth = nb.Nifti1Image(abs(epi), header=rs_hdr, affine=rs_aff)
	epi_synth_path = os.path.join(os.getcwd(), synthName)
	epi_synth.to_filename(epi_synth_path)
	try:
		if os.path.isfile(epi_synth_path): return epi_synth_path
	except IOError
