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

// Annotation format:
LINEWIDTH = 1;
run("Line Width...", "line="+LINEWIDTH);

// Tests number and reference volumes (this can be taken from the description.json file on each Test folder):
testNro = Array.getSequence(10);
refVol = newArray(0, 1, 2, 1, 2, 1, 1, 2, 2, 2, 0);
roiFrame = Array.copy(refVol);
for (idxVol=0; idxVol < refVol.length; idxVol++) {
	vol_i = refVol[idxVol];
	if (vol_i == 0) {
		roiFrame[idxVol]  = "001";
	} else if (vol_i == 1) {
		roiFrame[idxVol] = "001";
	} else if (vol_i == 2) {
		roiFrame[idxVol] = "002";
	} else {
		roiFrame[idxVol] = "001";
	}		 
}
roiFilenames = "RoiSet-Frame";


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
// Dialog.addCheckbox("Check to hide the images during execution (good to save computational resources)", true); // var hideImages
// Dialog.addCheckbox("Check to run as a batch process (i.e. process all images at once)", false); // var batchMode
Dialog.addCheckbox("Check to run on debug mode?", false); // var DEBUGMODE; verbose level of the log file
Dialog.addCheckbox("Check to run on test mode (doesn't process anything) ", false); // var testRun

Dialog.show();

/** To recover the variables from each box component, they must be retrieve in the same order as defined when creating the dialog box **/
srcPath = Dialog.getString();
hideImages= false; // Dialog.getCheckbox();
batchMode = false; // Dialog.getCheckbox();
debugMode = Dialog.getCheckbox();
testRun= !Dialog.getCheckbox();

path2Tests= srcPath+ TESTFLDR + FILESEP;
path2Output= srcPath+ OUTPUTFLDR + FILESEP;

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
	
// Dataset must be selected individually if not run as Batch Process:
Dialog.create("Select the dataset to review:");
Dialog.addRadioButtonGroup("1) Select from which test (see description of each test below):", optionList, 1, optionList.length, 0);
Dialog.addRadioButtonGroup("2) Select patient name:", patientList , 1, patientList .length, 0);
Dialog.show();

List.setList(testsList);
listOfTests = newArray(listOfTests[List.indexOf(Dialog.getRadioButton)]);
List.setList(patientsList);
listOfPatients= newArray(listOfPatients[List.indexOf(Dialog.getRadioButton)]);

if (testRun) {
	setBatchMode(hideImages);
	for (idxTest=0; idxTest < listOfTests.length; idxTest++) {
		// For each Test folder, we loop over the patients and visits to extract the mean signal intensity over time for each ROI:
		test = listOfTests[idxTest].replace(EOFDirList, FILESEP);
		testNro = substring(test, 4, test.length-1);
		if ( debugMode ) {
			print("Test: "+parseInt(testNro));
		}
		path2Test = path2Tests + test + DATASUBFLDR + FILESEP;
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
					// Convert image to RGB so can overlay ROI as colour draw
					selectImage(niiFileID);
					run("RGB Color");
					// Additionally, will need to get information about time and z axes:
					Stack.getDimensions(width, height, channels, slices, frames);
					print("Image contains " + frames + " timepoints");
					// For each of these dataset, we find the corresponding ROI in the REFTEST folder:
					path2ROIs= path2Ref + currPatient + currVisit + ROILOCATION +FILESEP;
					run("Set Measurements...", "area mean standard min display redirect=None decimal=3");
					// roiName =  roiFilenames + String.format("%03.0f", nROI);
					roiName = roiFilenames + roiFrame[testNro];
					print("RoiFrame: " + roiName);
					path2ROI = path2ROIs + roiName + ".zip";
					if (File.exists(path2ROI)) {
						print("Opening ROI...");
						roiManager("Open", path2ROI);
						nROIs = roiManager("count");
						Br = 0.2; Ar = 1.0 / ( Math.exp(Br * nROIs) - 1);
						Bg =0.2; Ag = 1.0 / ( 1.0 - Math.exp(-Br * nROIs) );
						Bb =0.1; Ab = 1.0 / ( 1.0 - Math.exp(-Br * nROIs) );
						for (indROI=0; indROI < nROIs; indROI++) {
							roiManager("Select", indROI);
							run("Measure Stack...", "channels frames order=tcz");
							Stack.getPosition(channel, slice, frame); // TODO: From here, get the different slices that the ROI cover, this will be used later to make sub-stacks from that
							R = Math.round ( 255.0 * Ar * ( Math.exp( Br * ( nROIs - indROI) ) - 1.0 ) );
							G = Math.round( 255.0 * Ag * ( 1.0 - Math.exp( -Bg * (nROIs - indROI) ) ) );
							B = Math.round( 255.0 * Ab * ( 1.0 - Math.exp( -Bb * indROI ) ) );
							if (debugMode) {
								print(" Colour palette for ROI No " + indROI +":");
								print("Red: " + R +"\nGreen: " + G +"\nBlue: " + B);
							}
							setForegroundColor(R, G, B);
							for (nTimePoints = 0; nTimePoints <= frames; nTimePoints++) {
								Stack.setPosition(channel, slice, nTimePoints);
								run("Draw", "slice");
								//roiManager("Select", indROI);
								//roiManager("Draw");
							} /**
							Dialog.create("Continue?");
							Dialog.addMessage("Continue?")
							Dialog.show(); **/
						} // for indROI
						// TODO: After drawing the ROI in all time frames, make a sub-stack with the slices covered by the ROIs. This should probably be a loop
						// run("Make Subset...", "slices=69 frames=1-6");
						// subStackID = getImageID();
						//roiManager("Show All with labels");
						//if (idxVisit <  (listOfVisits.length - 1) ){
							// Clean ROI content
						//	roiManager("reset");
							// Reset Results windows
						//	close("Results");
						//} // if (idxVisit) - Reset ROI for next visit
					} else {
						print("There is no ROI named " + path2ROI);
					} // if (File.exists(path2ROI))
					if (idxVisit <  (listOfVisits.length - 1) ){
						Dialog.create("Continue?");
						Dialog.addMessage("Continue to review next Visit?")
						Dialog.show();
						// Clean ROI content
						roiManager("reset");
						// Reset Results windows
						close("Results");
					} // if (idxVisit) - Reset ROI and continue to next visit
				} else {
					print("File " + path2Nifti + " is not a valid image, skipping");
				} // if (File.exists(path2Nifti))
			} // for idxVisit
		} // for idxPatient
	} // for idxTest
	// Force to disable Batch Mode at the end of execution:
	setBatchMode(false);
} else { 
	print("Everthing seems ok, but I have nothing to do..."); 
} // if (testRun)

print("Saving the Log file...");
selectWindow("Log");
print("All done, bye!");
getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
timestamp = String.format("%.0f", year)+String.format("%02.0f", month)+String.format("%02.0f", dayOfMonth) + "T" + String.format("%02.0f", hour) + String.format("%02.0f", minute) + String.format("%02.0f", second);
saveAs("Text",path2Output + "Log_" + timestamp +".txt" );
setBatchMode(false);
return;
