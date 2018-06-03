var nifti = require('nifti-reader-js')


// Take NIFTI file data and return the grayscale image values
export function convertNifti(data) {
    var niftiHeader = null,
	niftiImage = null,
	niftiExt = null;
    // Decompress if needed
    if (nifti.isCompressed(data)) {
	data = nifti.decompress(data);
    }
    // If valid NIFTI data
    if (nifti.isNIFTI(data)) {
	// Separate image and header data
	niftiHeader = nifti.readHeader(data);
	niftiImage = nifti.readImage(niftiHeader, data);
	// Get the dimensions
	var height = niftiHeader.dims[1]
	var width = niftiHeader.dims[2]
	var depth = niftiHeader.dims[3]
	if (nifti.hasExtension(niftiHeader)) {
	    niftiExt = nifti.readExtensionData(niftiHeader, data);
	}
	// Depending on the bitdepth, convert the current image to an array
	var image
	if (niftiHeader.bitDepth == 8) {
	    image = new Uint8Array(niftiImage)
	}
	else if (niftiHeader.numBitsPerVoxel == 16) {
	    image = new Uint16Array(niftiImage)
	}
	else {
	    alert("Error, unrecognized bit depth in image")
	    return
	}
	console.log(niftiHeader)
	
	var dataY = []
	for (var y = 0; y < height; y++) {
	    dataY.push([])
	    for (var imgN = 0; imgN < niftiHeader.dims[3]; imgN++) {
		dataY[y].push([])
		for (var x = 0; x < width; x++) {
		    dataY[y][imgN].push(-1)
		}
	    }
	}


	var dataZ = []
	for (var x = 0; x < width; x++) {
	    dataZ.push([])
	    for (var imgN = 0; imgN < niftiHeader.dims[3]; imgN++) {
		dataZ[x].push([])
		for (var y = 0; y < height; y++) {
		    dataZ[x][imgN].push(-1)
		}
	    }
	}


	var dataX = []
	for (var imgN = 0; imgN < niftiHeader.dims[3]; imgN++) {
	    // Iterate over the number of expected images (3rd dimension)
	    dataX.push([])
	    var imgStart = height*width*imgN 
	    // Copy the array over to a 2-d array 
	    for (var y = 0; y < height; y++) {
		dataX[imgN].push([])
		for (var x = 0; x < width; x++) {
		    var idx = (imgStart + width * y + x);
		    dataX[imgN][y].push(image[idx])
		    dataY[y][imgN][x] = image[idx]
		    dataZ[x][imgN][y] = image[idx]
		}
	    }
	}
	let pixDims = niftiHeader.pixDims
	var imgs = [
	    {imgDat: dataX, pixHeight:pixDims[0], pixWidth:pixDims[1]},
	    {imgDat: dataY, pixHeight:pixDims[2], pixWidth:pixDims[1]},
	    {imgDat: dataZ, pixHeight:pixDims[2], pixWidth:pixDims[0]}
	]
	return imgs
    }
    else {
	return false
    }
}
