import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import nipype.interfaces.utility as util
from nipype.interfaces.afni import preprocess

#functional preprocessing

def create_calib_preproc(wf_name = 'calib_preproc'):
    """
    
    The main purpose of this workflow is to process functional data. Raw rest file is deobliqued and reoriented 
    into RPI. Then take the mean intensity values over all time points for each voxel and use this image 
    to calculate motion parameters. The image is then skullstripped, normalized and a processed mask is 
    obtained to use it further in Image analysis.
    
    Parameters
    ----------
    
    wf_name : string
        Workflow name
    
    Returns 
    -------
    calib_preproc : workflow object
        Functional Preprocessing workflow object
    
    Notes
    -----
    
    
    Workflow Inputs::
    
        inputspec.bo_name : cal_bo nifti filepath 
            B0 field map from CBI calibration scan

        inputspec.rho_name : cal_rho nifti filepath 
            spin density image CBI calibration scan

        inputspec.rs_name : cal_rs nifti filepath 
            R2* image CBI calibration scan

        inputspec.reg_bo_name : regularized cal_bo nifti filepath 
            smoothed B0 field map from CBI calibration scan for unwarping
            
        inputspec.echo_spacing : string - default 30
            Echo Time in units of echo spacing
            
        inputspec.readout_dir : string - default 1
            Last volume/slice of the functional image (optional)

        inputspec.synth_name : cal_synth nifti NAME only MUST end in '.nii.gz' - default cal_synth.nii.gz
            synthetic image simulation the  conditions of B0 dropout and other epi distortions

            
    Workflow Outputs::
    
        outputspec.cal_bo_RPI : string (nifti file)
            deobliqued reoriented B0 field map from CBI calibration scan
          
        outputspec.cal_rho_RPI : string (nifti file) 
            deobliqued reoriented spin density image CBI calibration scan

        outputspec.cal_rs_RPI : string (nifti file) 
            deobliqued reoriented R2* image CBI calibration scan

        outputspec.cal_reg_bo_RPI : regularized cal_bo nifti filepath 
            deobliqued reoriented smoothed B0 field map from CBI calibration scan for unwarping

        outputspec.cal_synth_RPI : string (nifti file) 
            deobliqued reoriented synthetic image


    Order of commands:
    
	1. Deoblique bo image
	2. Deoblique rho Image
	3. Deoblique rs image
	4. Use 1,2,3 in cbiCalibSynthEPI program with TE=30, readout_dir=1 and cal_synth as defaults
	
	5. Reorient to RPI, 1,2,3 and output
	6. Reorient to RPI 4 and output
	7. Deoblique cal_reg_bo image
	8. Reorient 7 and output
	
    High Level Workflow Graph:
    
    .. image:: ../images/calib_preproc.dot.png
       :width: 1000
    
    
    Detailed Workflow Graph:
    
    .. image:: ../images/calib_preproc_detailed.dot.png
       :width: 1000

    Examples
    --------
    
    >>> from calib_preproc import *
    >>> preproc = create_calib_preproc()
    >>> preproc.inputs.inputspec.bo_name='/sam/wave1/sub4974/calib_1/cal_bo.nii.gz'
    >>> preproc.inputs.inputspec.rho_name='/sam/wave1/sub4974/calib_1/cal_rho.nii.gz'
    >>> preproc.inputs.inputspec.rs_name='/sam/wave1/sub4974/calib_1/cal_rs.nii.gz'
    >>> preproc.inputs.inputspec.reg_bo_name='/sam/wave1/sub4974/calib_1/cal_reg_bo.nii.gz'
    >>> preproc.base_dir='./'
    >>> preproc.run()
    
    >>> from calib_preproc import *
    >>> preproc = create_calib_preproc()
    >>> preproc.inputs.inputspec.bo_name='/sam/wave1/sub4974/calib_1/cal_bo.nii.gz'
    >>> preproc.inputs.inputspec.rho_name='/sam/wave1/sub4974/calib_1/cal_rho.nii.gz'
    >>> preproc.inputs.inputspec.rs_name='/sam/wave1/sub4974/calib_1/cal_rs.nii.gz'
    >>> preproc.inputs.inputspec.reg_bo_name='/sam/wave1/sub4974/calib_1/cal_reg_bo.nii.gz'
    >>> preproc.inputs.inputspec.reg_bo_name='/sam/wave1/sub4974/calib_1/cal_reg_bo.nii.gz'
    >>> preproc.inputs.inputspec.synth_name='cal_epi_synth.nii.gz'
    >>> preproc.inputs.inputspec.echo_spacing='30'
    >>> preproc.inputs.inputspec.readout_dir='1'

    >>> preproc.base_dir='./'
    >>> preproc.run()

    """

    preproc = pe.Workflow(name=wf_name)
    inputNode = pe.Node(util.IdentityInterface(fields=['bo_name',
                                                       'rho_name',
                                                       'rs_name',
                                                       'reg_bo_name',
                                                       'echo_spacing',
                                                       'readout_dir',
                                                       'synth_name']),
                        name='inputspec')
    

    outputNode = pe.Node(util.IdentityInterface(fields=['cal_bo_RPI',
                                                       'cal_rho_RPI',
                                                       'cal_rs_RPI',
                                                       'cal_reg_bo_RPI',
                                                       'cal_synth_RPI']),

                          name='outputspec')

    func_create_synth = pe.Node(util.Function(input_names=['boName', 
                                                      'rhoName', 
                                                      'rsName', 
                                                      'TE', 
                                                      'kyDir', 
                                                      'synthName'],
                               output_names=['epi_synth_path'],
                 function=cbiCalibSynthEPI), name='func_create_synth')
    
    	    
    bo_deoblique = pe.Node(interface=preprocess.Refit(),
                            name='bo_deoblique')
    bo_deoblique.inputs.deoblique = True
    
    rho_deoblique = bo_deoblique.clone('rho_deoblique')
    
    rs_deoblique = bo_deoblique.clone('rs_deoblique')

    reg_bo_deoblique = bo_deoblique.clone('reg_bo_deoblique')

    preproc.connect(inputNode, 'echo_spacing',
                    func_create_synth, 'TE')

    preproc.connect(inputNode, 'readout_dir',
                    func_create_synth, 'kyDir')

    preproc.connect(inputNode, 'synth_name',
                    func_create_synth, 'synthName')

    preproc.connect(inputNode, 'bo_name',
                    bo_deoblique, 'in_file')
    
    preproc.connect(bo_deoblique, 'out_file',
                    func_create_synth, 'boName')

    preproc.connect(inputNode, 'rho_name',
                    rho_deoblique, 'in_file')


    preproc.connect(rho_deoblique, 'out_file',
                    func_create_synth, 'rhoName')

    preproc.connect(inputNode, 'rs_name',
                    rs_deoblique, 'in_file')


    preproc.connect(rs_deoblique, 'out_file',
                    func_create_synth, 'rsName')


    synth_reorient = pe.Node(interface=preprocess.Resample(),
                               name='synth_reorient')
    synth_reorient.inputs.orientation = 'RPI'
    synth_reorient.inputs.outputtype = 'NIFTI_GZ'

    preproc.connect(func_create_synth, 'epi_synth_path',
                    synth_reorient, 'in_file')
        
    preproc.connect(synth_reorient, 'out_file',
                    outputNode, 'cal_synth_RPI')
    
    bo_reorient = synth_reorient.clone('bo_reorient')

    rho_reorient = synth_reorient.clone('rho_reorient')

    rs_reorient = synth_reorient.clone('rs_reorient')

    reg_bo_reorient = synth_reorient.clone('reg_bo_reorient')
    
    
    preproc.connect(bo_deoblique, 'out_file',
                    bo_reorient, 'in_file')
	
    preproc.connect(bo_reorient, 'out_file',
                    outputNode, 'cal_bo_RPI')
	
    preproc.connect(rho_deoblique, 'out_file',
                    rho_reorient, 'in_file')
    
    preproc.connect(rho_reorient, 'out_file',
                    outputNode, 'cal_rho_RPI')
    
    preproc.connect(rs_deoblique, 'out_file',
                    rs_reorient, 'in_file')
		    
    preproc.connect(rs_reorient, 'out_file',
                    outputNode, 'cal_rs_RPI')
    
    preproc.connect(inputNode, 'reg_bo_name',
                    reg_bo_deoblique, 'in_file')

    preproc.connect(reg_bo_deoblique, 'out_file',
                    reg_bo_reorient, 'in_file')
    
    preproc.connect(reg_bo_reorient, 'out_file',
                    outputNode, 'cal_reg_bo_RPI')
    

    return preproc



def cbiCalibSynthEPI(boName,rhoName, rsName, TE=None, kyDir=None, synthName=None):
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

	if TE == None: TE = 30
	if kyDir == None: kyDir = 1
	if synthName == None: synthName = 'cal_synth.nii.gz'
	
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
	bo = float(kyDir)*bo
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
		
    		for nn in range(Ny):
        		bors = bors*brfactor
        		data[:,nn] = np.dot((bors*rhoslice),zFy[:,nn])
    		
		epi[:,:,nz] = abs(np.dot(data , zPFy))
	
	epi_synth = nb.Nifti1Image(abs(epi), header=rs_hdr, affine=rs_aff)
	epi_synth_path = os.path.join(os.getcwd(), synthName)
	epi_synth.to_filename(epi_synth_path)
	if os.path.isfile(epi_synth_path): return epi_synth_path
	
