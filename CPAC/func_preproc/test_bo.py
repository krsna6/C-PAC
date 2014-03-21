#from bo_func_preproc import *
#preproc = create_func_preproc(slice_timing_correction=True, wf_name='sub4974_bo_func_preproc')
#preproc.inputs.inputspec.calib_reg_bo_RPI='/sam/projects/krishna/C-PAC/CPAC/func_preproc/calib_preproc/reg_bo_reorient/cal_reg_bo_resample.nii.gz'
##'/sam/wave1/sub3112/calib_1/cal_reg_bo.nii.gz'
#preproc.inputs.inputspec.start_idx = 4
#preproc.inputs.inputspec.stop_idx = 180
#preproc.inputs.inputspec.rest='/sam/wave1/sub4974/rest_1/lfo.nii.gz'
#preproc.inputs.scan_params.tr = '2.0'
#preproc.inputs.scan_params.ref_slice = 1
#preproc.inputs.scan_params.acquisition = 'alt+z'
#preproc.base_dir='./'
#preproc.run() #doctest: +SKIP
#    

import nipype.interfaces.utility as util
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
from bo_func_preproc import *
from calib_preproc import *
from registration_via_synth import create_bbr_func_to_anat_via_synth

B0_workflow = pe.Workflow(name='sub4974_B0_TEST')

func_file = '/sam/wave1/sub4974/rest_1/lfo.nii.gz'
wm_seg = '/sam/wave1/sub4974/anat_1/brain_wmseg.nii.gz'
anat_skull_file = '/sam/wave1/sub4974/anat_1/head.nii.gz'
bbr_sched = '/frodo/shared/fsl5/etc/flirtsch/bbr.sch'


calib_preproc = create_calib_preproc()
calib_preproc.inputs.inputspec.bo_name='/sam/wave1/sub4974/calib_1/cal_bo.nii.gz'
calib_preproc.inputs.inputspec.rho_name='/sam/wave1/sub4974/calib_1/cal_rho.nii.gz'
calib_preproc.inputs.inputspec.rs_name='/sam/wave1/sub4974/calib_1/cal_rs.nii.gz'
calib_preproc.inputs.inputspec.reg_bo_name='/sam/wave1/sub4974/calib_1/cal_reg_bo.nii.gz'



preproc = create_func_preproc(slice_timing_correction=True)

preproc.inputs.inputspec.start_idx = 4
preproc.inputs.inputspec.stop_idx = 180
preproc.inputs.inputspec.rest=func_file
preproc.inputs.scan_params.tr = '2.0'
preproc.inputs.scan_params.ref_slice = 1
preproc.inputs.scan_params.acquisition = 'alt+z'


nr3 = create_bbr_func_to_anat_via_synth()
nr3.inputs.inputspec.func = func_file
nr3.inputs.inputspec.anat_skull = anat_skull_file
nr3.inputs.inputspec.anat_wm_segmentation=wm_seg
nr3.inputs.inputspec.bbr_schedule=bbr_sched
    



B0_workflow.connect(calib_preproc, 'outputspec.cal_reg_bo_RPI',preproc, 'inputspec.calib_reg_bo_RPI' )
B0_workflow.connect(calib_preproc, 'outputspec.cal_synth_RPI',nr3, 'inputspec.synth_RPI' )
B0_workflow.connect(calib_preproc, 'outputspec.cal_bo_RPI',nr3, 'inputspec.calib_bo_RPI' )
B0_workflow.connect(calib_preproc, 'outputspec.cal_rho_RPI',nr3, 'inputspec.calib_rho_RPI' )


B0_workflow.base_dir='./'
B0_workflow.run()
B0_workflow.write_graph(format='ps')
print 'RUN CONVERT PS TO PNG COMMAND'
