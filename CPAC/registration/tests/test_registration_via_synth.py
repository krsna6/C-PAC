import nipype.interfaces.utility as util

def test_nonlinear_register():
    from registration_via_synth import create_nonlinear_register
    
    import nipype.pipeline.engine as pe
    import nipype.interfaces.fsl as fsl
    
    ## necessary inputs
    ## -input_brain
    ## -input_skull
    ## -reference_brain
    ## -reference_skull
    ## -fnirt_config
    ## -fnirt_warp_res
    
    ## input_brain
    anat_bet_file = '/sam/wave1/sub3120/anat_1/brain.nii.gz'
    anat_file = '/sam/wave1/sub3120/anat_1/head.nii.gz'

    ## input_skull
    
    ## reference_brain
    mni_file = '/frodo/shared/fsl5/data/standard/MNI152_T1_2mm_brain.nii.gz'
    
    ## reference_skull
    
    ## fnirt_config
    fnirt_config = 'T1_2_MNI152_2mm'
    
    ## fnirt_warp_res
    fnirt_warp_res = None
    
    #?? what is this for?:
    func_file = '/sam/wave1/sub3120/rest_1/lfo_pp_noss.nii.gz'
    
    mni_workflow = pe.Workflow(name='mni_workflow')

    linear_reg = pe.Node(interface=fsl.FLIRT(),
                         name='linear_reg_0')
    linear_reg.inputs.cost = 'corratio'
    linear_reg.inputs.dof = 6
    linear_reg.inputs.interp = 'nearestneighbour'
    
    linear_reg.inputs.in_file = func_file
    linear_reg.inputs.reference = anat_bet_file
    
    #T1 to MNI Node
    c = create_nonlinear_register()
    c.inputs.inputspec.input_brain = anat_bet_file
    c.inputs.inputspec.reference_brain = '/frodo/shared/fsl5/data/standard/MNI152_T1_2mm_brain.nii.gz'
    c.inputs.inputspec.input_skull = anat_file
    c.inputs.inputspec.reference_skull = '/frodo/shared/fsl5/data/standard/MNI152_T1_2mm.nii.gz'
    
    
    
    c.inputs.inputspec.fnirt_config = 'T1_2_MNI152_2mm'
    
    #EPI to MNI warp Node
    mni_warp = pe.Node(interface=fsl.ApplyWarp(),
                       name='mni_warp')
    mni_warp.inputs.ref_file = '/frodo/shared/fsl5/data/standard/MNI152_T1_2mm_brain.nii.gz'
    mni_warp.inputs.in_file = func_file

    mni_workflow.connect(c, 'outputspec.nonlinear_xfm',
                         mni_warp, 'field_file')
    mni_workflow.connect(linear_reg, 'out_matrix_file',
                         mni_warp, 'premat')
    
    mni_workflow.base_dir = './'
    mni_workflow.run()    
    
def test_registration_via_synth():
    from registration_via_synth import create_linear_func_to_synth, create_linear_rho_to_anat, create_bbr_func_to_anat_via_synth
    
    import nipype.pipeline.engine as pe
    import nipype.interfaces.fsl as fsl
    import nipype.interfaces.utility as util

    func_file = '/sam/wave1/sub3120/rest_1/lfo.nii.gz'
    anat_skull_file = '/sam/wave1/sub3120/anat_1/head.nii.gz'
    anat_bet_file = '/sam/wave1/sub3120/anat_1/brain.nii.gz'
    mni_brain_file = '/frodo/shared/fsl5/data/standard/MNI152_T1_2mm_brain.nii.gz'
    mni_skull_file = '/frodo/shared/fsl5/data/standard/MNI152_T1_2mm.nii.gz'
    
    synth_file = '/sam/wave1/sub3120/calib_1/cal_synth.nii.gz'
    
    cal_bo_file = '/sam/wave1/sub3120/calib_1/cal_reg_boRPI.nii.gz'

    cal_rho_file = '/sam/wave1/sub3120/calib_1/cal_rho.nii.gz'
    
    wm_seg = '/sam/wave1/sub3120/anat_1/brain_wmseg.nii.gz'
    
    bbr_sched = '/frodo/shared/fsl5/etc/flirtsch/bbr.sch'
    
    
    
    
#    nr1 = create_linear_func_to_synth()
#    nr1.inputs.inputspec.func = func_file
#    nr1.inputs.inputspec.synth = synth_file
#    nr1.inputs.inputspec.calib_bo_RPI = cal_bo_file
#    
#    nr1.base_dir = './'
#    nr1.run()
    
    
#    nr2 = create_linear_rho_to_anat()
#    nr2.inputs.inputspec.anat_skull = anat_skull_file
#    nr2.inputs.inputspec.calib_rho = cal_rho_file
#    
#    nr2.base_dir = './'
#    nr2.run()
#    

    nr3 = create_bbr_func_to_anat_via_synth()
    nr3.inputs.inputspec.func = func_file
    nr3.inputs.inputspec.synth = synth_file
    nr3.inputs.inputspec.calib_bo_RPI = cal_bo_file
    nr3.inputs.inputspec.anat_skull = anat_skull_file
    nr3.inputs.inputspec.calib_rho = cal_rho_file
    nr3.inputs.inputspec.anat_wm_segmentation=wm_seg
    nr3.inputs.inputspec.bbr_schedule=bbr_sched
    nr3.base_dir = './'
    nr3.run()
    
    
    
    
#test_nonlinear_register()
test_registration_via_synth()
