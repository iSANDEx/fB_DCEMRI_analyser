// TODO: Bundle this macro and LabelROI into a toolbar

/**************************************************/
// Auxiliar functions
function constArray(size, boolVal) {
	
	booleanArray = newArray(size);
	for (idx=0; idx < size; idx++) {
		booleanArray[idx] = boolVal;
	}
	return booleanArray;
}

// End of auxiliar functions
/**************************************************/
// Start fresh closing everything before running
run("Close All");
close("ROI Manager");
close("Log");
close("Results");

// Defines constant parameters:
FILESEP = File.separator;
EOFDirList = "/"; // See getFileList description at https://imagej.net/ij/developer/macro/functions.html#G
TESTFLDR = "tests";
OUTPUTFLDR = "csv_output";
REFTEST = "Test000";
DATASUBFLDR = "datasets";
ROILOCATION = "landmarks";

/**************************************************************/
// Tests number and reference volumes (this can be taken from the description.json file on each Test folder):
testNro = Array.getSequence(10);
refVol = newArray(0, 1, 2, 1, 2, 1, 1, 2, 2, 2, 0);
roiFrame = Array.copy(refVol);
for (idxVol=0; idxVol < refVol.length; idxVol++) {
	vol_i = refVol[idxVol];
	if (vol_i == 0) {
		roiFrame[idxVol]  = "002";
	} else if (vol_i == 1) {
		roiFrame[idxVol] = "001";
	} else if (vol_i == 2) {
		roiFrame[idxVol] = "002";
	} else {
		roiFrame[idxVol] = "000";
	}		 
}
roiFilenames = "RoiSet-Frame";
/**************************************************************/


// Path to data and analyses output:
homePath= getDirectory("home");
// The following is not a useful folder, is just the example displayed in the interactive window to select the Source Folder for the data
listOfFolders= newArray( substring(homePath, 0, lastIndexOf(homePath, FILESEP)), "Data", "fMRIBreastData");
defaultPath= String.join(listOfFolders,FILESEP);
if (!File.exists(defaultPath)) {
	// defaultPath does not exist, then we assign the homePath as the defaultPath
	defaultPath = homePath;
}
/** 
    Here adds the graphical user interface to setup the analyses:
    Check this example to add interactivity through buttons: https://imagej.net/ij/macros/DialogDemo.txt
**/
title = "iSANDEx Macro - Selectable options";
Dialog.create(title);

Dialog.addDirectory("Select the Root folder hosting the data:", defaultPath); // var srcPath
Dialog.addCheckbox("Check to hide the images during execution (good to save computational resources)", true); // var hideImages
Dialog.addCheckbox("Check to run as a batch process (i.e. process all images at once)", false); // var batchMode
Dialog.addCheckbox("Check to run on debug mode?", false); // var DEBUGMODE; verbose level of the log file
Dialog.addCheckbox("Check to run on test mode (doesn't process anything) ", false); // var testRun

Dialog.show();

/** To recover the variables from each box component, they must be retrieve in the same order as defined when creating the dialog box **/
srcPath = Dialog.getString();
hideImages= Dialog.getCheckbox();
batchMode = Dialog.getCheckbox();
debugMode = Dialog.getCheckbox();
testRun= Dialog.getCheckbox();

// Define the main paths based on the selections made:
path2Tests= srcPath+ TESTFLDR + FILESEP;
path2Output= srcPath+ OUTPUTFLDR + FILESEP;

// Get the number of available tests to review (it gives the option to select which ones to process)
//listOfTests = getFileList(path2Tests);
//testsArray = Array.copy(listOfTests);

testsArray = getFileList(path2Tests);
trueArray = constArray(testsArray.length, 1);
falseArray = constArray(testsArray.length, 0);
for (idx=0; idx < testsArray .length; idx++) {
	testsArray[idx] = testsArray[idx].replace(EOFDirList, "");
}

if ( batchMode) {
	// Select which tests to process (by default, select all of them)
	Dialog.create("Select which tests to process:");
	Dialog.addCheckboxGroup(testsArray.length, 1, testsArray, trueArray);
	Dialog.show();

	tests_to_process = newArray();
	for (idx=0; idx<testsArray.length; idx++) {
	    idx_Selection = Dialog.getCheckbox();
	    if (idx_Selection) {
		tests_to_process = Array.concat(tests_to_process, testsArray[idx]);
	    }
	}
} else {
	// Pick up a single test to process:
	Dialog.create("Select a Test folder:");
	Dialog.addRadioButtonGroup("Pick up a test folder to process:", testsArray, testsArray.length, 1, 0);
	Dialog.show();
	tests_to_process = Array.filter(testsArray, Dialog.getRadioButton);
}

/***
Gets the References ROIs from Test000 and then measures each dataset for all Tests and saves the data as "testXXX.xls"
The folder structure within a test folder is:
<PatientName> -> <PatientName_visitType(Pre/Post-Treatment)_visitDate(yyyymmdd)>
***/

// List folders in REFTEST (e.g. "Test000"):
path2Ref = path2Tests + REFTEST + FILESEP + DATASUBFLDR + FILESEP;
listOfPatients = getFileList(path2Ref);

if ( !testRun ) {
	setBatchMode(batchMode);
	for (idxTest=0; idxTest < tests_to_process.length; idxTest++) {
		// Skips the tests unselected in the GUI:
		// For each Test folder, we loop over the patients and visits to extract the mean signal intensity over time for each ROI:
		test = tests_to_process[idxTest] + FILESEP;
		testNro = substring(test, 4, test.length-1);
		path_to_test = path2Tests + test + DATASUBFLDR + FILESEP;
		if (debugMode) {
			print("Processing test folder " + test);
		} // if (debugMode)
		// If running in batchMode, it'll process all patients in the test folder. If not, then a choice can be made:
		patientsArray = getFileList(path_to_test);
		for (idx=0; idx < patientsArray.length; idx++) {
			patientsArray[idx] = patientsArray[idx].replace(EOFDirList, "");
		} // for idx (patientsArray)
		if ( ! batchMode ) {
			trueArray = constArray(patientsArray.length, 1);
			Dialog.create("Select which patients to process:");
			Dialog.addCheckboxGroup(patientsArray.length, 1, patientsArray, trueArray);
			Dialog.show();

			patients_to_process = newArray();
			for (idx = 0; idx < patientsArray.length; idx++) {
				idx_Selection = Dialog.getCheckbox();
				if (idx_Selection) {
					patients_to_process = Array.concat(patients_to_process, patientsArray[idx]);
				} // if idx_Selection
			} // for idx patients_to_process
		} else {
			patients_to_process = Array.copy(patientsArray);
		} // if (!batchMode) - patients_to_process

		// Looping over every patient in the test folder:
		for (idxPatient = 0; idxPatient < patients_to_process.length; idxPatient++) {
			currPatient = patients_to_process[idxPatient] + FILESEP;
			path_to_patient = path_to_test + currPatient;
			listOfVisits = getFileList(path_to_patient);
			for (idxVisit = 0; idxVisit < listOfVisits.length; idxVisit++) {
				currVisit = listOfVisits[idxVisit].replace(EOFDirList, FILESEP);
				path_to_visit = path_to_patient + currVisit;
				// Load the Nifti image:
				path_to_nifti = path_to_visit + currVisit.replace(FILESEP, ".nii.gz");
				if (File.exists(path_to_nifti)) {
					print("Reading Nifti volume " + path_to_nifti+", please wait...");
					run("NIfTI-Analyze", "open=" + path_to_nifti);
					rename("CurrImg");
					niiFileID = getImageID();
					run("Flip Vertically", "stack");
					// For each of these dataset, we find the corresponding ROI in the REFTEST folder:
					path2ROIs= path2Ref + currPatient + currVisit + ROILOCATION +FILESEP;
					run("Set Measurements...", "area mean standard min display redirect=None decimal=3");
					roiName = roiFilenames + roiFrame[testNro];
					if (debugMode) {
						print("RoiFrame: " + roiName);
					}
					path2ROI = path2ROIs + roiName + ".zip";
					if (File.exists(path2ROI)) {
						if (debugMode) {
							print("Opening ROI " + path2ROI);
						}
						roiManager("Open", path2ROI);
						nROIs = roiManager("count");
						for (indROI=0; indROI < nROIs; indROI++) {
							roiManager("Select", indROI);
							run("Measure Stack...", "channels frames order=tcz");
						} // for indROI
						// Save the data as CSV file
						saveAs("Results", path2Output + currVisit.replace(FILESEP,"") + "_" + test.replace(FILESEP, "") + "_" + roiName+".csv");
						// Clean ROI content
						roiManager("reset");
						// Reset Results windows
						close("Results");
					} else {
						print("There is no ROI named " + path2ROI);
					} // if (File.exists(path2ROI))
					//} // for nROI
					close("*"); // Closes all image windows
				} else {
					print("File " + path2Nifti + " is not a valid image, skipping");
				} // if (File.exists(path2Nifti))
			} // for idxVisit
		} // for idxPatient
	} // for idxTest
	// Force to disable Batch Mode at the end of execution:
	setBatchMode(false);
} // if ( ! testRun)
print("Saving the Log file...");
selectWindow("Log");
print("All done, bye!");
getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
timestamp = String.format("%.0f", year)+String.format("%02.0f", month)+String.format("%02.0f", dayOfMonth) + "T" + String.format("%02.0f", hour) + String.format("%02.0f", minute) + String.format("%02.0f", second);
saveAs("Text",path2Output + "Log_" + timestamp +".txt" );
return;
