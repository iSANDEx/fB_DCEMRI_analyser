// Start fresh closing everything before running
run("Close All");
close("ROI Manager");
close("Log");
close("Results");

// Defines constant parameters:
FILESEP = File.separator;
EOFDirList = "/"; // See getFileList description at https://imagej.net/ij/developer/macro/functions.html#G
TESTFLDR = "tests";
REFTEST = "Test000";
DATA_SUBFLDR = "datasets";
ROI_LOCATION = "landmarks";
ROI_FILENAMES = "RoiSet-Frame";
//FIXED_VOLUME = 2;


// Path to data and analyses output:
homePath= getDirectory("home");
// The following is not a useful folder, is just the example displayed in the interactive window to select the Source Folder for the data
listOfFolders= newArray( substring(homePath, 0, lastIndexOf(homePath, FILESEP)), "Data", "fMRIBreastData");
defaultPath= String.join(listOfFolders,FILESEP);
if (!File.exists(defaultPath)) {
	// defaultPath does not exist, then we assign the homePath as the defaultPath
	defaultPath = homePath;
}


title = "iSANDEx Macro - Selectable options";
Dialog.create(title);

Dialog.addDirectory("Select the Root folder hosting the data:", defaultPath); // var srcPath
Dialog.addCheckbox("Check to run on debug mode?", false); // var DEBUGMODE; verbose level of the log file
Dialog.show();


/** To recover the variables from each box component, they must be retrieve in the same order as defined when creating the dialog box **/
srcPath = Dialog.getString();
debugMode = Dialog.getCheckbox();

path2Tests= srcPath+ TESTFLDR + FILESEP;
path2Refs = path2Tests + REFTEST + FILESEP + DATA_SUBFLDR + FILESEP;
listOfPatients = getFileList(path2Refs);

// Get the list of tests to process:
listOfTests = getFileList(path2Tests);

optionList = Array.copy(listOfTests);
for (idx=0; idx < optionList .length; idx++) {
	optionList[idx] = optionList[idx].replace(EOFDirList, "");
}
List.fromArrays(optionList, listOfTests);
testsList = List.getList();

patientList = Array.copy(listOfPatients);
for (idx=0; idx < patientList .length; idx++) {
	patientList [idx] = patientList [idx].replace(EOFDirList, "");
}
List.fromArrays(patientList , listOfPatients);
patientsList = List.getList();

// Pickup Test Folder:
Dialog.create("Select the dataset to review:");
Dialog.addRadioButtonGroup("1) Select from which test (see description of each test below):", optionList, 1, optionList.length, optionList[0]);
Dialog.addRadioButtonGroup("2) Select patient name:", patientList , 1, patientList .length, patientList[0]);
Dialog.addRadioButtonGroup("Reference Volume for registration?", newArray("Pre-Contrast (1)", "1st Post-Contrast (2)"), 1,2,"Pre-Contrast (1)");
Dialog.show();

List.setList(testsList);
listOfTests = newArray(listOfTests[List.indexOf(Dialog.getRadioButton)]);
List.setList(patientsList);
listOfPatients= newArray(listOfPatients[List.indexOf(Dialog.getRadioButton)]);
FixedVolume = Dialog.getRadioButton;
if (FixedVolume=="Pre-Contrast (1)") {
	FIXED_VOLUME = 1;
} else if (FixedVolume=="1st Post-Contrast (2)") {
	FIXED_VOLUME = 2;
}

for (idxTest = 0; idxTest < listOfTests.length; idxTest++) {
	print(listOfTests[idxTest]);
	path_to_test = path2Tests + listOfTests[idxTest];
	for (idxPatient=0; idxPatient < listOfPatients.length; idxPatient++) {
		patient = listOfPatients[idxPatient];
		path_to_patient = path_to_test + DATA_SUBFLDR + FILESEP + patient;
		// Check the patient directory exists in the test folder:
		patient_exists = File.isDirectory(path_to_patient);
		if (patient_exists) {
			patientID = split(patient, "-");
			patientID = patientID[0];
			visits = getFileList(path_to_patient);
			preTreatmentPath = "";
			postTreatmentPath = "";
			for (idxVisit = 0; idxVisit < visits.length; idxVisit++) {
				print(visits[idxVisit]);
				if (visits[idxVisit].startsWith(patientID+"-"+"Pre-Treatment")) {
					preTreatmentVisit = visits[idxVisit];
					preTreatmentPath = path_to_patient + visits[idxVisit];
				}
				if (visits[idxVisit].startsWith(patientID+"-"+"Post-Treatment")) {
					postTreatmentVisit = visits[idxVisit];
					postTreatmentPath = path_to_patient + visits[idxVisit];
				}
				if ( (preTreatmentPath !="") & (postTreatmentPath !="")) {
					ok_to_proceed = true;
					print("Ok to continue...");
				} else {
					print("At least one path is missing for dataset " + path_to_patient);
					ok_to_proceed = false;
				}
			}
			if (ok_to_proceed) {
				folders_in_pre_treat_visit = getFileList(preTreatmentPath);
				for (idxFolder=0; idxFolder<folders_in_pre_treat_visit.length; idxFolder++) {
					path_to_review = preTreatmentPath + folders_in_pre_treat_visit[idxFolder];
					if ( File.isDirectory(path_to_review) ) {
						fixed_nii_filename = getFileList(path_to_review+FIXED_VOLUME + FILESEP);
						run("NIfTI-Analyze", "open=" + path_to_review+FIXED_VOLUME + FILESEP + fixed_nii_filename[0]);
						fixedVolumeID= getImageID();
						rename("Fixed Volume " + preTreatmentVisit);
						run("Flip Vertically", "stack");
					}
				}
				folders_in_post_treat_visit = getFileList(postTreatmentPath);
				for (idxFolder=0; idxFolder<folders_in_post_treat_visit.length; idxFolder++) {
					path_to_review = postTreatmentPath + folders_in_post_treat_visit [idxFolder];
					if ( File.isDirectory(path_to_review) ) {
						fixed_nii_filename = getFileList(path_to_review+FIXED_VOLUME + FILESEP);
						run("NIfTI-Analyze", "open=" + path_to_review+FIXED_VOLUME + FILESEP + fixed_nii_filename[0]);
						fixedVolumeID= getImageID();
						rename("Moving Volume " + postTreatmentVisit);
						run("Flip Vertically", "stack");
					} else {
						if ( (folders_in_post_treat_visit [idxFolder].startsWith("deformation_map")) | (folders_in_post_treat_visit [idxFolder].startsWith("inter_visit_aligned")) ) {
							run("NIfTI-Analyze", "open=" + path_to_review);
							run("Flip Vertically", "stack");
						}
					}
				}
				// Open the ROI:
				path2ROI = path2Refs + patient + FILESEP + preTreatmentVisit + ROI_LOCATION + FILESEP + ROI_FILENAMES + String.format("%03.0f", FIXED_VOLUME)+".zip";
				print(path2ROI);
				roiManager("Open", path2ROI);
			}
		}
	}
}
return;
open("/Users/joseulloa/Data/fMRIBreastData/tests/Test012/datasets/CR-ANON68760/CR-Pre-Treatment-20221212/301/1/301_dyn_ethrive.nii.gz");
selectImage("301_dyn_ethrive.nii.gz");
run("Flip Vertically", "stack");
rename("Pre-Treatment-301_dyn_ethrive.nii.gz");
open("/Users/joseulloa/Data/fMRIBreastData/tests/Test012/datasets/CR-ANON68760/CR-Post-Treatment-20230120/301/1/301_dyn_ethrive.nii.gz");
selectImage("301_dyn_ethrive.nii.gz");
run("Flip Vertically", "stack");
rename("Post-Treatment-301_dyn_ethrive.nii.gz");
open("/Users/joseulloa/Data/fMRIBreastData/tests/Test000/datasets/CR-ANON68760/CR-Pre-Treatment-20221212/landmarks/RoiSet-Frame002.zip");
roiManager("Open", "/Users/joseulloa/Data/fMRIBreastData/tests/Test000/datasets/CR-ANON68760/CR-Pre-Treatment-20221212/landmarks/RoiSet-Frame002.zip");
selectImage("inter_visit_aligned_ants_fixedVol002_CR-Post-Treatment-20230120.nii.gz");
run("Flip Vertically", "stack");
open("/Users/joseulloa/Data/fMRIBreastData/tests/Test012/datasets/CR-ANON68760/CR-Post-Treatment-20230120/deformation_map_ants_fixedVol002_CR-Post-Treatment-20230120.nii.gz");
selectImage("deformation_map_ants_fixedVol002_CR-Post-Treatment-20230120.nii.gz");
run("Flip Vertically", "stack");
