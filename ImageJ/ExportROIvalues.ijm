// Start fresh closing everything before running
run("Close All");
close("ROI Manager");
close("Log");
close("Results");

// Defines constant parameters:
FILESEP = File.separator;
EOFDirList = "/"; // See getFileList description at https://imagej.net/ij/developer/macro/functions.html#G
REFTEST = "Test000";
DATASUBFLDR = "datasets";
ROILOCATION = "landmarks";

// Tests number and reference volumes (this can be taken from the description.json file on each Test folder):
testNro = Array.getSequence(9);
RefVol = newArray(0, 1, 2, 1, 2, 1, 1, 2, 2, 2);
roiFilenames = "RoiSet-Frame";


// Path to data and analyses output:
homePath= getDirectory("home");
defaultDir= File.setDefaultDir(homePath);
// The following is not a useful folder, is just the example displayed in the interactive window to select the Source Folder for the data
listOfFolders= newArray( substring(homePath, 0, lastIndexOf(homePath, FILESEP)), "Data", "fMRIBreastData");
examplePath= String.join(listOfFolders,FILESEP);
// Here the user selects the true source directory:
srcPath= getDir("Select the Root folder hosting the data (e.g. "+examplePath+"):");

path2Tests= srcPath+ "tests" + FILESEP;
path2Output= srcPath+ "output" + FILESEP;

/***
Gets the References ROIs from Test000 and then measures each dataset for all Tests and saves the data as "testXXX.xls"
The folder structure within a test folder is:
<PatientName> -> <PatientName_visitType(Pre/Post-Treatment)_visitDate(yyyymmdd)>
***/

// List folders in REFTEST (e.g. "Test000"):
path2Ref = path2Tests + REFTEST + FILESEP + DATASUBFLDR + FILESEP;
listOfPatients = getFileList(path2Ref);

// Get the list of tests to process:
listOfTests = getFileList(path2Tests);

// Options when running as a batch and debugging:
// Check this example to add interactivity through buttons: https://imagej.net/ij/macros/DialogDemo.txt
goRun = 1;
batchMode = true;

if (goRun) {
setBatchMode(batchMode);
for (idxTest=0; idxTest < listOfTests.length; idxTest++) {
	// For each Test folder, we loop over the patients and visits to extract the mean signal intensity over time for each ROI:
	test = listOfTests[idxTest].replace(EOFDirList, FILESEP);
	path2Test = path2Tests + test + DATASUBFLDR + FILESEP;
	listOfPatients = getFileList(path2Test);
	for (idxPatient = 0; idxPatient < listOfPatients.length; idxPatient++) {
		currPatient = listOfPatients[idxPatient].replace(EOFDirList, FILESEP);
		path2Patient = path2Test + currPatient;
		listOfVisits = getFileList(path2Patient);
		for (idxVisit = 0; idxVisit < listOfVisits.length; idxVisit++) {
			currVisit = listOfVisits[idxVisit].replace(EOFDirList, FILESEP);
			path2Visit = path2Patient + currVisit;
			// Load the Nifti image:
			path2Nifti = path2Visit + currVisit.replace(FILESEP, ".nii.gz");
			if (File.exists(path2Nifti)) {
				print("Reading Nifti volume " + path2Nifti+", please wait...");
				run("NIfTI-Analyze", "open=" + path2Nifti);
				niiFileID = getImageID();
				run("Flip Vertically", "stack");
				// For each of these dataset, we find the corresponding ROI in the REFTEST folder:
				path2ROIs= path2Ref + currPatient + currVisit + ROILOCATION +FILESEP;
				run("Set Measurements...", "area mean standard min display redirect=None decimal=3");
				for (nROI=1; nROI < 3; nROI++){
					roiName =  roiFilenames + String.format("%03.0f", nROI);
					path2ROI = path2ROIs + roiName + ".zip";
					if (File.exists(path2ROI)) {
						print("Opening ROI...");
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
				} // for nROI
				close("*"); // Closes all image windows
			} else {
				print("File " + path2Nifti + " is not a valid image, skipping");
			} // if (File.exists(path2Nifti))
		} // for idxVisit
	} // for idxPatient
} // for idxTest
// Force to disable Batch Mode at the end of execution:
setBatchMode(false);
} // if (goRun)
print("Saving the Log file...");
selectWindow("Log");
print("All done, bye!");
getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
timestamp = String.format("%.0f", year)+String.format("%02.0f", month)+String.format("%02.0f", dayOfMonth) + "T" + String.format("%02.0f", hour) + String.format("%02.0f", minute) + String.format("%02.0f", second);
saveAs("Text",path2Output + "Log_" + timestamp +".txt" );
return;
