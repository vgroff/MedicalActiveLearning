var nifti = require('nifti-reader-js')
import {Image} from "./image.js"
import {Image3D} from "./image3d.js"

export function getImageData(data) {
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
	console.log("header", niftiHeader)
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
	if (niftiHeader.numBitsPerVoxel == 8) {
	    image = new Uint8Array(niftiImage)
	}
	else if (niftiHeader.numBitsPerVoxel == 16) {
	    image = new Uint16Array(niftiImage)	    
	}
	else if (niftiHeader.numBitsPerVoxel == 32) {
	    image = new Uint32Array(niftiImage)
	}
	else if (niftiHeader.numBitsPerVoxel == 64) {
	    image = new Uint64Array(niftiImage)
	}
	else {
	    console.log("Error, unrecognized bit depth in image")
	    alert("Error, unrecognized bit depth in image")
	    return
	}
	console.log(niftiHeader)
	var max = 0
	for (var imgN = 0; imgN < niftiHeader.dims[3]; imgN++) {
	    // Iterate over the number of expected images (3rd dimension)
	    var imgStart = height*width*imgN 
	    // Copy the array over to a 2-d array 
	    for (var y = 0; y < height; y++) {
		for (var x = 0; x < width; x++) {
		    var idx = (imgStart + width * y + x);
		    if (max < image[idx]) {
			max = image[idx]
		    }
		}
	    }
	}
	console.log("MAX", max)
	var dataX = []
	var mean = 0
	var stdDev = 0
	var counts = 0
	for (var imgN = 0; imgN < niftiHeader.dims[3]; imgN++) {
	    // Iterate over the number of expected images (3rd dimension)
	    dataX.push([])
	    var imgStart = height*width*imgN 
	    // Copy the array over to a 2-d array 
	    for (var y = 0; y < height; y++) {
		dataX[imgN].push([])
		for (var x = 0; x < width; x++) {
		    var idx = (imgStart + width * y + x);
		    dataX[imgN][y].push(image[idx] / max)
		    if (image[idx] / max > 0.01) {
			mean += image[idx]/max
			counts += 1
		    }
		}
	    }
	}
	console.log("MEAN", mean/(counts), dataX)
	let pixDims = niftiHeader.pixDims
	return [dataX, pixDims[1], pixDims[2], pixDims[3], mean/counts]
    }
    else {
	alert("File not recognised")
	return false
    }
}

// Take NIFTI file data and return the grayscale image values
export function convertNifti(data) {
    var res = getImageData(data)
    var dataX = res[0]
    var image3D = new Image3D(dataX, res[1], res[2], res[3])
    return [image3D, res[4]]
}
