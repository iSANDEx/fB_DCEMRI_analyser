/**************************************************/
// Auxiliar functions
function getRefVolFromJSON(path2json) {
	jsonFile = File.openAsString(path2json);
	arrayJson =split(jsonFile, ","); 
	// Field of interest is "Registration Details" -> "reference volume"
	for (idx=0; idx<arrayJson.length; idx++) {
		if (startsWith(arrayJson[idx], " \"reference volume\"")) {
			referenceVolumeStr = split(arrayJson[idx], ":");
			reference_volume = String.format("%03.0f", parseInt(referenceVolumeStr[1]));
			return reference_volume;
		}
	}
	return false;
}

// End of auxiliar functions
/**************************************************/
// Start fresh closing everything before running
run("Close All");
close("ROI Manager");
close("Log");
close("Results");

macro "ExploreSingleDataset - [a]" {
// Defines constant parameters:
FILESEP = File.separator;
EOFDirList = "/"; // See getFileList description at https://imagej.net/ij/developer/macro/functions.html#G
TESTFLDR = "tests";
LOGFLDR = "logs";
OUTPUTFLDR = "output" + FILESEP + "pub";
REFTEST = "Test000";
DATASUBFLDR = "datasets";
ROILOCATION = "landmarks";

roiFilenames = "RoiSet-Frame";

// Annotation format:
LINEWIDTH = 1;
run("Line Width...", "line="+LINEWIDTH);
setFont("SansSerif", 20, "antialiased");
setJustification("left");

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
//Dialog.addCheckbox("Check to run on test mode (doesn't process anything) ", false); // var testRun

Dialog.show();

/** To recover the variables from each box component, they must be retrieve in the same order as defined when creating the dialog box **/
srcPath = Dialog.getString();
hideImages= false; // Dialog.getCheckbox();
batchMode = false; // Dialog.getCheckbox();
debugMode = Dialog.getCheckbox();
testRun= false; // Dialog.getCheckbox();

path2Tests= srcPath+ TESTFLDR + FILESEP;
path2Output= srcPath+ OUTPUTFLDR + FILESEP;
path2Logs = srcPath + LOGFLDR + FILESEP;
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
Dialog.addRadioButtonGroup("1) Select from which test (see description of each test below):", optionList, 1, optionList.length, optionList[1]);
Dialog.addRadioButtonGroup("2) Select patient name:", patientList , 1, patientList.length, patientList[0]);
Dialog.show();

List.setList(testsList);
listOfTests = newArray(listOfTests[List.indexOf(Dialog.getRadioButton)]);
List.setList(patientsList);
listOfPatients= newArray(listOfPatients[List.indexOf(Dialog.getRadioButton)]);

if ( ! testRun) {
	setBatchMode(hideImages);
	for (idxTest=0; idxTest < listOfTests.length; idxTest++) {
		// For each Test folder, we loop over the patients and visits to extract the mean signal intensity over time for each ROI:
		test = listOfTests[idxTest].replace(EOFDirList, FILESEP);
		testNro = substring(test, 4, test.length-1);
		if ( debugMode ) {
			print("Test: "+parseInt(testNro));
		}
		path2Test = path2Tests + test + DATASUBFLDR + FILESEP;
		roiFrame = getRefVolFromJSON(path2Tests + test + "description.json");
		for (idxPatient = 0; idxPatient < listOfPatients.length; idxPatient++) {
			currPatient = listOfPatients[idxPatient].replace(EOFDirList, FILESEP);
			path2Patient = path2Test + currPatient;
			listOfVisits = getFileList(path2Patient);
			RoiSetCounter = 0;
			for (idxVisit = 0; idxVisit < listOfVisits.length; idxVisit++) {
				currVisit = listOfVisits[idxVisit].replace(EOFDirList, FILESEP);
				VisitName = split(currVisit,"-");
				visitID = VisitName[1];
				path2Visit = path2Patient + currVisit;
				// Load the Nifti image:
				path2Nifti = path2Visit + currVisit.replace(FILESEP, ".nii.gz");
				if (File.exists(path2Nifti)) {
					print("Reading Nifti volume " + path2Nifti+", please wait...");
					run("NIfTI-Analyze", "open=" + path2Nifti);
					niiFileID = getImageID();
					run("Flip Vertically", "stack");
					// Convert image to RGB so can overlay ROI as colour draw
					//selectImage(niiFileID);
					//run("RGB Color");
					// Additionally, will need to get information about time and z axes:
					Stack.getDimensions(width, height, channels, slices, frames);
					if (debugMode) {
						print("Image contains " + frames + " timepoints");
					}
					// For each of these dataset, we find the corresponding ROI in the REFTEST folder:
					path2ROIs= path2Ref + currPatient + currVisit + ROILOCATION +FILESEP;
					run("Set Measurements...", "area mean standard min display redirect=None decimal=3");
					roiName = roiFilenames + roiFrame;
					print("RoiFrame: " + roiName);
					path2ROI = path2ROIs + roiName + ".zip";
					if (File.exists(path2ROI)) {
						print("Opening ROI...");
						roiManager("Open", path2ROI);
						nROIs = roiManager("count");
						// Keep track of the slice displayed to add some descriptive text and to make a substack at the end
						currSlice = 0;
						subStacks = newArray(); 
						for (indROI=RoiSetCounter; indROI < nROIs; indROI++) {
							roiManager("Select", indROI);
							ROIName = Roi.getName;
							roiManager("Rename", visitID+ "-" + ROIName);
							print(visitID+ "-" + ROIName);
							run("Measure Stack...", "channels frames order=tcz");
							Stack.getPosition(channel, slice, frame); // TODO: From here, get the different slices that the ROI cover, this will be used later to make sub-stacks from that
							// Identify the current slice and add it to the subStack array, if it is not already in there
							if (currSlice != slice) {
								subStacks = Array.concat(subStacks, slice);
							} // if currSlice != slice - populating subStack
							currSlice = slice; // Update the current slice value
						} // for indROI
						RoiSetCounter = nROIs;
						// TODO: After drawing the ROI in all time frames, make a sub-stack with the slices covered by the ROIs. This should probably be a loop
						String.resetBuffer;
						String.append("["); //subStacks[0];
						subStack = Array.sort(subStacks);
						for (idxSubStack=0;idxSubStack<subStacks.length; idxSubStack++) {
							String.append(subStacks[idxSubStack]+",");
						}
						String.append("]")
						if (debugMode) {
							print("Slices to add at the subStack: " + String.buffer);
						}
						run("Make Subset...", "slices=" + String.buffer + "frames=1-"+frames);
						subStackID = getImageID();
					} else {
						print("There is no ROI named " + path2ROI);
					} // if (File.exists(path2ROI))
				} else {
					print("File " + path2Nifti + " is not a valid image, skipping");
				} // if (File.exists(path2Nifti))
				// Close full stack
				selectImage(niiFileID);
				close();
				// Adjust bright and contrast of the substack:
				selectImage(subStackID);
				run("Enhance Contrast", "saturated=0.35");
			} // for idxVisit
		} // for idxPatient
	} // for idxTest
	// Force to disable Batch Mode at the end of execution:
	setBatchMode("exit and display");
} else { 
	print("Everthing seems ok, but I have nothing to do..."); 
} // if (testRun)

print("Saving the Log file...");
selectWindow("Log");
print("All done, bye!");
getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
timestamp = String.format("%.0f", year)+String.format("%02.0f", month)+String.format("%02.0f", dayOfMonth) + "T" + String.format("%02.0f", hour) + String.format("%02.0f", minute) + String.format("%02.0f", second);
saveAs("Text", path2Logs + "IJ_Log_ExploreSingleDataset_" + timestamp +".txt" );
return;

} // end macro "ExploreSingleDataset"
