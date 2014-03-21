'''
@ krishna
this script reads the default CPAC subject list and adds a field called 'calib'
calib is a dict with FOUR keys: 
1) calib_bo, 2)calib_reg_bo, 3) calib_rho, 4) calib_rs

input: 1) CPAC subject list got from extract_data
       2) calib_info.yml manually created - a text file with each row format as:
       	  >>> subject_id: calib_folder name
	  
Assumptions: assumes that the calib folder resides in the same level as that of
	     anat folder
	     ex: if /sam/wave1/sub001/anat_1/anat.nii.gz read from CPAC subject list
	     implies /sam/wave1/sub001/calib_1 exists has files with same names as keys
	     and ending in '.nii.gz'

calib_names in the calib_dir: 
1) cal_bo.nii.gz
2) cal_reg_bo.nii.gz
3) cal_rho.nii.gz
4) cal_rs.nii.gz

To RUN: use..
>> import CPAC; CPAC.utils.add_calib_info.run('CPAC_subject_list.yml', 'calib_test.yml')
where calib_test.yml has the calib folder names corresponding to each subject in a yml format
'''

import sys, os, yaml, json

#cpac_sub_list_file = sys.argv[1]
#calib_list_file = sys.argv[2]


# defining calib_names
cal_bo_name = 'cal_bo.nii.gz'
cal_reg_bo_name = 'cal_reg_bo.nii.gz'
cal_rho_name = 'cal_rho.nii.gz'
cal_rs_name = 'cal_rs.nii.gz'

def run(cpac_sub_list_file, calib_list_file):
	cpac_sub_list = yaml.load(open(cpac_sub_list_file,'rb'))
	calib_list = yaml.load(open(calib_list_file,'rb'))

	# check if the number of subjects in both lists are the same
	if len(calib_list) == len(cpac_sub_list):
		print 'number of subjects = ', len(calib_list)
		
		#loop through each subject in CPAC subject list and process calib_list thereby
		for sub_idx, cpac_sub in enumerate(cpac_sub_list):
			print sub_idx, ') ', cpac_sub['subject_id'], 
			subject_id = cpac_sub['subject_id']
			if subject_id in calib_list.keys():
				calib_dir = calib_list[subject_id]
				print calib_dir, 
				anat_dir = cpac_sub['anat']
				anat_base = anat_dir.split(subject_id)[0]
				calib_dir_path = os.path.join(anat_base, subject_id, calib_dir)
				if os.path.isdir(calib_dir_path):
					calib_dir_ls = os.listdir(calib_dir_path)
					#print calib_dir_path, calib_dir_ls
					if cal_bo_name in calib_dir_ls and cal_reg_bo_name in calib_dir_ls and cal_rho_name in  calib_dir_ls and cal_rs_name in calib_dir_ls:
						print ' all required calib files exist'
						cal_bo = os.path.realpath(os.path.join(calib_dir_path, cal_bo_name))
						cal_reg_bo = os.path.realpath(os.path.join(calib_dir_path, cal_reg_bo_name))
						cal_rho = os.path.realpath(os.path.join(calib_dir_path, cal_rho_name))
						cal_rs = os.path.realpath(os.path.join(calib_dir_path, cal_rs_name))
						
						# add a dict for key 'calib' for each list item in cpac subject list
						cpac_sub_list[sub_idx]['calib']={'cal_bo': cal_bo, 'cal_reg_bo': cal_reg_bo, 'cal_rho': cal_rho, 'cal_rs': cal_rs}
						

					
					else: print calib_dir_ls, ' IN ', calib_dir_path, ' DOESNOT INCLUDE ONE OF ', cal_bo_name, cal_reg_bo_name, cal_rho_name, cal_rs_name 
				
				
				else: print calib_dir_path, 'DIRECTORY DOESNOT EXIST CHECK!!!'			
				
			else: print subject_id, ' .. DOESNOT EXIST IN THE MANUALLY CREATE CALIB LIST CHECK!!'

	else: print 'ERROR!!!!! UNEQUAL NUMBER OF SUBJECTS BETWEEN CALIB INFO AND CPAC SUBJECT LIST CHECK!!!'


	# write out the edited cpac subject list
	with open('CPAC_subject_list_calib.yml', 'wb') as outfile:
		outfile.write(yaml.dump(cpac_sub_list, default_flow_style=False))
	return os.path.realpath('CPAC_subject_list_calib.yml')
